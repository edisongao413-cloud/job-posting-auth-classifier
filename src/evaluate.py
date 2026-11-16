"""Evaluate predictions against the final labels.

Run:  python3 src/evaluate.py results/baseline_preds_dev.csv
"""
import sys

import pandas as pd

from common import LABELS


def report(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str)
    rows = []
    for lab in LABELS:
        tp = ((df.pred == lab) & (df.final_label == lab)).sum()
        fp = ((df.pred == lab) & (df.final_label != lab)).sum()
        fn = ((df.pred != lab) & (df.final_label == lab)).sum()
        prec = tp / (tp + fp) if tp + fp else float("nan")
        rec = tp / (tp + fn) if tp + fn else float("nan")
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else float("nan")
        rows.append({"label": lab, "support": int(tp + fn), "precision": prec, "recall": rec, "f1": f1})
    m = pd.DataFrame(rows).round(3)
    print(f"\n{path}  (n={len(df)})")
    print(m.to_string(index=False))
    print("\nConfusion matrix (rows = true label, columns = predicted):")
    print(pd.crosstab(df.final_label, df.pred).reindex(index=LABELS, columns=LABELS, fill_value=0))
    return m


if __name__ == "__main__":
    for p in sys.argv[1:]:
        report(p)
