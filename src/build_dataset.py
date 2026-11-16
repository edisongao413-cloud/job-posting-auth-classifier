"""Build the project dataset from the collected CSV.

Reads  data/raw/job-postings-150.csv
Writes data/postings/<id>.txt   (posting text with collector notes removed)
       data/postings_index.csv  (one row per posting: metadata + draft label + review columns)

Run from the project folder:  python3 src/build_dataset.py
"""
import re
from pathlib import Path

import pandas as pd

from clean_text import clean

ROOT = Path(__file__).resolve().parent.parent
raw = pd.read_csv(ROOT / "data" / "raw" / "job-postings-150.csv")

out_dir = ROOT / "data" / "postings"
out_dir.mkdir(parents=True, exist_ok=True)

truncated = raw["full_job_description"].str.contains(
    r"truncat|assembled|fragment|not be retrieved in full|only the opening", case=False)
listing_url = raw["job_url"].str.contains(r"linkedin\.com/jobs/[a-z-]+-jobs$")

rows = []
for i, r in raw.iterrows():
    pid = f"{int(r['id']):04d}"
    txt = out_dir / f"{pid}.txt"
    if not txt.exists():  # never overwrite a text file you may have edited by hand
        txt.write_text(clean(r["full_job_description"]) + "\n", encoding="utf-8")
    rows.append({
        "id": pid,
        "batch": r["batch"],
        "group": r["group"],
        "source_platform": r["source_platform"],
        "search_query": r["search_query"],
        "company": r["company"],
        "job_title": r["job_title"],
        "location": r["location"],
        "posted_date": r["posted_date"],
        "job_url": r["job_url"],
        "url_type": "listing_page" if listing_url[i] else "posting",
        "text_quality": "truncated" if truncated[i] else "complete",
        "auth_label": r["label"],
        "cap_exempt": r["cap_exempt"],
        "evidence_quote": r["label_evidence_quote"],
        "label_source": "ai_draft",
        "human_label": "",
        "human_verified": "",
        "notes": r["notes"],
    })

idx_path = ROOT / "data" / "postings_index.csv"
if idx_path.exists():
    raise SystemExit("data/postings_index.csv already exists - not overwriting. Rename it first to rebuild.")
pd.DataFrame(rows).to_csv(idx_path, index=False, encoding="utf-8-sig")
print(f"Wrote {len(rows)} postings to {out_dir} and data/postings_index.csv")
