"""Split postings into a development set (to build and adjust methods) and a test set (to report results).

Stratified by the draft label so both sets have the same mix. Fixed seed so the split never changes.
Run once:  python3 src/split_data.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
labels = pd.read_csv(ROOT / "data" / "postings_index.csv", dtype=str)
labels["id"] = labels["id"].str.zfill(4)
labels["final_label"] = labels["auth_label"]  # stratify on the draft label; review changes are small
path = ROOT / "data" / "split.csv"
if path.exists():
    raise SystemExit("data/split.csv already exists. The split must not change once made.")

dev = labels.groupby("final_label", group_keys=False)[["id", "final_label"]].apply(
    lambda g: g.sample(frac=30 / len(labels), random_state=42))
labels["split"] = labels["id"].isin(dev["id"]).map({True: "dev", False: "test"})
labels[["id", "split"]].to_csv(path, index=False)
print(pd.crosstab(labels["final_label"], labels["split"]))
