"""Create data/label_review.csv: one row per posting, with a colored flag, the AI draft label,
the work-authorization sentences found in the posting, and empty columns for your review.

Flags
  🔴  must fix: evidence problem or likely wrong label
  🟠  data quality: truncated text, search-page link, cap_exempt or seniority to double-check
  🟡  normal check: read the sentences and confirm the label

Run from the project folder:  python3 src/make_review_sheet.py
"""
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
idx = pd.read_csv(ROOT / "data" / "postings_index.csv", dtype=str)
idx["id"] = idx["id"].str.zfill(4)

AUTH = re.compile(r"sponsor|citizen|clearance|authoriz|visa|\bOPT\b|\bCPT\b|ITAR|export[- ]control|"
                  r"U\.?S\.? person|green card|permanent resident|public trust|work permit|eligible to work",
                  re.I)
SENIOR = re.compile(r"\bII\b|\bIII\b|Senior|\bSr\.?\b|Manager|\bLead\b|Experienced", re.I)

MUST_FIX = {
    "0018": "Likely wrong: only says 'must have work authorization' -> guide says unclear",
    "0116": "Evidence quote is NOT in the posting text (only in collector note). Check the real posting",
}
CAP_EXEMPT_CHECK = {
    "0071": "cap_exempt: MITRE is a nonprofit research org - 'yes' may be right, confirm",
    "0084": "cap_exempt: IDA is a nonprofit research org - 'yes' may be right, confirm",
    "0104": "cap_exempt: Recidiviz is a nonprofit but likely NOT cap-exempt, confirm",
}


def auth_sentences(text):
    flat = re.sub(r"\s+", " ", text)
    sents = re.split(r"(?<=[.!?])\s+", flat)
    hits = [s.strip()[:300] for s in sents if AUTH.search(s)]
    return " || ".join(hits[:4]) if hits else "(none found)"


rows = []
for _, r in idx.iterrows():
    text = (ROOT / "data" / "postings" / f"{r['id']}.txt").read_text(encoding="utf-8")
    issues = []
    if r["id"] in MUST_FIX:
        issues.append(MUST_FIX[r["id"]])
    if r["text_quality"] == "truncated":
        issues.append("Truncated text: work-authorization section may be missing")
    if r["url_type"] == "listing_page":
        issues.append("Link is a LinkedIn search page, not the posting")
    if r["id"] in CAP_EXEMPT_CHECK:
        issues.append(CAP_EXEMPT_CHECK[r["id"]])
    if SENIOR.search(str(r["job_title"])):
        issues.append("Title may not be entry level")

    if r["id"] in MUST_FIX:
        flag = "🔴"
    elif issues:
        flag = "🟠"
    else:
        flag = "🟡"

    quote = r["evidence_quote"]
    if str(quote).strip().lower() == "no work-authorization language in jd":
        quote = ""

    rows.append({
        "flag": flag,
        "id": r["id"],
        "issue": " | ".join(issues),
        "company": r["company"],
        "job_title": r["job_title"],
        "ai_label": r["auth_label"],
        "evidence_quote": quote,
        "auth_sentences_in_posting": auth_sentences(text),
        "human_verified": "",
        "human_label": "",
        "cap_exempt": r["cap_exempt"],
        "review_note": "",
        "text_file": f"data/postings/{r['id']}.txt",
        "job_url": r["job_url"],
    })

out = pd.DataFrame(rows)
order = {"🔴": 0, "🟠": 1, "🟡": 2}
out = out.sort_values(by=["flag", "id"], key=lambda s: s.map(order) if s.name == "flag" else s)
path = ROOT / "data" / "label_review.csv"
if path.exists():
    raise SystemExit(f"{path} already exists - not overwriting your review. Rename it first if you want a fresh sheet.")
out.to_csv(path, index=False, encoding="utf-8-sig")
print(out["flag"].value_counts().to_string())
print(f"Saved {path}")
