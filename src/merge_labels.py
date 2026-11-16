"""Merge your review (data/label_review.csv) into the final answer key.

Final label = human_label if you wrote one, otherwise ai_label (when human_verified = yes).
Writes data/labels_final.csv and prints how often you changed the AI draft label.

Run:  python3 src/merge_labels.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
rev = pd.read_csv(ROOT / "data" / "label_review.csv", dtype=str).fillna("")
rev["id"] = rev["id"].str.zfill(4)

rev["verified"] = rev["human_verified"].str.strip().str.lower().isin(["yes", "y"])
rev["final_label"] = rev["human_label"].str.strip().str.lower().where(
    rev["human_label"].str.strip() != "", rev["ai_label"])
bad = ~rev["final_label"].isin(["blocked", "unclear", "open"])
if bad.any():
    raise SystemExit(f"Unknown labels in rows: {rev.loc[bad, 'id'].tolist()} (use blocked / unclear / open)")

changed = rev["verified"] & (rev["final_label"] != rev["ai_label"])
n_ver = int(rev["verified"].sum())
print(f"Verified: {n_ver} of {len(rev)}")
if n_ver:
    print(f"You changed the AI draft label on {int(changed.sum())} of {n_ver} verified postings "
          f"({changed.sum() / n_ver:.0%}); agreement {1 - changed.sum() / n_ver:.0%}")
    for _, r in rev[changed].iterrows():
        print(f"  {r['id']}: {r['ai_label']} -> {r['final_label']}  {r['review_note']}")

# Copy any links you fixed in the review sheet back into postings_index.csv
idx_path = ROOT / "data" / "postings_index.csv"
idx = pd.read_csv(idx_path, dtype=str)
idx["id"] = idx["id"].str.zfill(4)
new_links = rev.set_index("id")["job_url"]
changed_links = idx["id"].map(new_links).fillna(idx["job_url"]) != idx["job_url"]
if changed_links.any():
    idx.loc[changed_links, "job_url"] = idx.loc[changed_links, "id"].map(new_links)
    idx.loc[changed_links, "url_type"] = "posting"
    idx.to_csv(idx_path, index=False, encoding="utf-8-sig")
    print(f"Updated {int(changed_links.sum())} links in postings_index.csv: {idx.loc[changed_links, 'id'].tolist()}")

out = rev[["id", "company", "job_title", "final_label", "ai_label", "verified", "cap_exempt", "review_note"]]
out.to_csv(ROOT / "data" / "labels_final.csv", index=False, encoding="utf-8-sig")
print("Saved data/labels_final.csv")
