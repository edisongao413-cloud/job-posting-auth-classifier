# Project brief for AI assistants

Goal: classify the work-authorization stance of U.S. job postings for an F-1/OPT candidate, and compare a
keyword baseline with an LLM classifier against hand labels.

Data
- `data/postings/<id>.txt`: raw posting text, one file per posting (not committed to git).
- `data/postings_index.csv`: one row per posting with metadata and the HAND label.

Labels (definitions in LABELING_GUIDE.md): `blocked`, `unclear`, `open`; plus `cap_exempt` yes/no.

Rules
- Hand labels in `postings_index.csv` are ground truth. Never change them to match a model's output.
- Write model predictions to `results/`, never into `postings_index.csv`.
- Report metrics honestly, including where the LLM does worse than the baseline.
- Never commit API keys; they live in `.env`.
