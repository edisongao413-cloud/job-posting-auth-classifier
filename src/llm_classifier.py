"""LLM classifier: ask a model to label each posting and quote its evidence.

Setup: create a file named .env in the project folder containing ONE of these lines:
    ANTHROPIC_API_KEY=sk-ant-...
    OPENAI_API_KEY=sk-...          (then also add OPENAI_MODEL=<model name>)
.env is listed in .gitignore, so the key never goes to GitHub.

Responses are cached in results/llm_raw/, so re-running never pays twice for the same posting.
Only the posting text is sent (never the search query, notes, or your labels).

Run:  python3 src/llm_classifier.py dev      (try on the 30 development postings first)
      python3 src/llm_classifier.py test
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

import pandas as pd

from common import ROOT, load_dataset, load_text

DEFAULT_ANTHROPIC_MODEL = "claude-haiku-5-5"  # override with ANTHROPIC_MODEL=... in .env

PROMPT = """You are classifying a U.S. job posting for an international student on F-1 OPT who will need visa sponsorship in the future.

Decide ONE label:
- "blocked": the posting rules this candidate out. Examples: requires U.S. citizenship or permanent residency; requires a security clearance or eligibility for one; requires "U.S. person" status / export-control (ITAR/EAR); states the employer will not sponsor now or in the future.
- "open": the posting is explicitly welcoming. Examples: says sponsorship is available or it sponsors H-1B; says OPT/CPT or international students are welcome or eligible.
- "unclear": neither. This includes no mention of work authorization, or only "must be authorized to work in the U.S." without saying anything about future sponsorship.

Rules:
- If the posting explicitly says OPT or STEM OPT holders are eligible, label it "open" even if it also says it will not sponsor later.
- Equal-opportunity statements that list "citizenship status" as a protected category are NOT a restriction.
- A field such as "US Citizenship Required: No" means citizenship is NOT required.
- Base the decision only on the posting text.

Return ONLY a JSON object, no other text:
{{"label": "blocked" | "open" | "unclear", "evidence_quote": "<shortest exact sentence from the posting that supports the label, or empty string if none>"}}

Job posting:
<<<
{posting}
>>>"""


def load_env():
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def call_anthropic(prompt):
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps({"model": os.environ.get("ANTHROPIC_MODEL", DEFAULT_ANTHROPIC_MODEL), "max_tokens": 2000,
                         "messages": [{"role": "user", "content": prompt}]}).encode(),
        headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01",
                 "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Claude API error {e.code}: {e.read().decode(errors='replace')}")
    # Newer models can return several content blocks (e.g. "thinking" before "text"); keep only the text.
    text = "".join(b.get("text", "") for b in body.get("content", []) if b.get("type") == "text")
    usage = dict(body.get("usage", {}), stop_reason=body.get("stop_reason"))
    return text, usage


def call_openai(prompt):
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps({"model": os.environ["OPENAI_MODEL"], "temperature": 0,
                         "messages": [{"role": "user", "content": prompt}]}).encode(),
        headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}", "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        body = json.load(r)
    return body["choices"][0]["message"]["content"], body.get("usage", {})


def parse(text):
    m = re.search(r"\{.*\}", text, re.S)
    try:
        obj = json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        obj = {}
    label = str(obj.get("label", "")).strip().lower()
    return (label if label in {"blocked", "open", "unclear"} else "parse_error"), str(obj.get("evidence_quote", ""))


def norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


if __name__ == "__main__":
    load_env()
    if os.environ.get("ANTHROPIC_API_KEY"):
        call = call_anthropic
    elif os.environ.get("OPENAI_API_KEY"):
        call = call_openai
    else:
        raise SystemExit("No API key found. Create a .env file in the project folder (see the top of this file).")

    split = sys.argv[1] if len(sys.argv) > 1 else "dev"
    df = load_dataset(None if split == "all" else split)
    cache = ROOT / "results" / "llm_raw"
    cache.mkdir(parents=True, exist_ok=True)

    preds, quotes, found = [], [], []
    for i, pid in enumerate(df["id"], 1):
        f = cache / f"{pid}.json"
        if f.exists():
            raw = json.loads(f.read_text())
        else:
            text, usage = call(PROMPT.format(posting=load_text(pid)))
            raw = {"response": text, "usage": usage}
            f.write_text(json.dumps(raw, indent=1))
            time.sleep(0.5)
        label, quote = parse(raw["response"])
        preds.append(label)
        quotes.append(quote)
        found.append(bool(quote) and norm(quote) in norm(load_text(pid)))
        print(f"{i}/{len(df)} {pid}: {label}")

    df["pred"], df["llm_quote"], df["quote_found_in_posting"] = preds, quotes, found
    out = ROOT / "results" / f"llm_preds_{split}.csv"
    df.to_csv(out, index=False)
    print(f"Saved {out}")
