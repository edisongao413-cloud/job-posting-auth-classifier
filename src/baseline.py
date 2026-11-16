"""Keyword baseline: label each posting with regular-expression rules.

Rules are applied in this order:
  1. Explicit OPT/STEM OPT eligibility            -> open (even if it also says no future sponsorship)
  2. Any blocking phrase                         -> blocked
  3. Any welcoming phrase                        -> open
  4. Otherwise                                   -> unclear

Only the posting text is used (never the search query or notes).
Run:  python3 src/baseline.py [dev|test|all]
"""
import re
import sys

import pandas as pd

from common import ROOT, load_dataset, load_text

OPT_ELIGIBLE = [
    r"(F-?1|STEM)\s*OPT[^.]{0,80}(eligible|welcome|encouraged|open)",
    r"(open|eligible) to (candidates|applicants|students)[^.]{0,40}\b(OPT|CPT)\b",
    r"\b(OPT|CPT)\b[^.]{0,40}(welcome|encouraged|eligible to apply)",
    r"F-?1[^.]{0,40}(welcome|encouraged)",
]
BLOCKED = [
    r"\bU\.?S\.?\s*citizen(ship)?\b[^.]{0,60}\b(required|must|only)\b(?!\s*:\s*No\b)",  # skip "Required: No"
    r"\bmust be (a )?U\.?S\.? citizen",
    r"\bcitizenship is required",
    r"(active|current|obtain|maintain|eligib\w* (for|to obtain))[^.]{0,40}security clearance",
    r"security clearance[^.]{0,40}(is )?required",
    r"\b(ITAR|export[- ]controlled?|export control)\b",
    r"\bU\.?S\.? person",
    r"(not|unable to|will not|won't|do not|does not|cannot|can't|no)\b[^.]{0,30}\b(visa )?sponsor",
    r"sponsorship[^.]{0,40}(is )?(not available|not offered|not provided|unavailable)",
    r"without[^.]{0,30}sponsorship",
    r"green card holders?|permanent residents? (only|required)|citizens? or (lawful )?permanent residents?",
    r"public trust",
]
OPEN = [
    r"sponsorship[^.]{0,20}(is )?(available|offered|provided)",
    r"eligible for (visa )?sponsorship",
    r"(will|can|may) (provide|offer)?\s*(visa )?sponsor",
    r"\bH-?1B\b[^.]{0,40}(sponsor|support|provide|offer)",
    r"visa support",
    r"international (students|candidates|applicants)[^.]{0,30}(welcome|encouraged|eligible)",
]


def first_match(patterns, text):
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            return p, m.group(0)
    return None, None


def classify(text: str) -> tuple[str, str]:
    flat = re.sub(r"\s+", " ", text)
    for label, pats in (("open", OPT_ELIGIBLE), ("blocked", BLOCKED), ("open", OPEN)):
        p, hit = first_match(pats, flat)
        if hit:
            return label, hit
    return "unclear", ""


if __name__ == "__main__":
    split = sys.argv[1] if len(sys.argv) > 1 else "dev"
    df = load_dataset(None if split == "all" else split)
    preds = [classify(load_text(pid)) for pid in df["id"]]
    df["pred"] = [p[0] for p in preds]
    df["matched_text"] = [p[1] for p in preds]
    out = ROOT / "results" / f"baseline_preds_{split}.csv"
    df.to_csv(out, index=False)
    print(f"Saved {out}  ({len(df)} postings)")
