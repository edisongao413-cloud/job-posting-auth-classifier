"""Shared helpers: load posting text and labels."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
LABELS = ["blocked", "unclear", "open"]


def load_text(pid: str) -> str:
    return (ROOT / "data" / "postings" / f"{pid}.txt").read_text(encoding="utf-8")


def load_dataset(split: str | None = None) -> pd.DataFrame:
    """Postings with the final label (from labels_final.csv if it exists, else the AI draft) and split."""
    final = ROOT / "data" / "labels_final.csv"
    if final.exists():
        lab = pd.read_csv(final, dtype=str)[["id", "final_label"]]
    else:
        lab = pd.read_csv(ROOT / "data" / "postings_index.csv", dtype=str)[["id", "auth_label"]]
        lab = lab.rename(columns={"auth_label": "final_label"})
    lab["id"] = lab["id"].str.zfill(4)
    sp = pd.read_csv(ROOT / "data" / "split.csv", dtype=str)
    sp["id"] = sp["id"].str.zfill(4)
    df = lab.merge(sp, on="id")
    if split:
        df = df[df["split"] == split]
    return df.reset_index(drop=True)
