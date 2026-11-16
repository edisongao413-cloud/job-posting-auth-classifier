# Collection Guide: What to Search For

**Goal for batch 1:** 15 postings (5 likely open, 5 likely blocked, 5 typical).
**Final goal:** ~150 postings, with at least 30 `blocked` and 20 `open`.

## Rules for every posting
- U.S.-based, full-time, entry-level or early-career (0–2 years). Skip internships and senior roles.
- Analyst-type roles you could realistically apply to (data, business, BI, pricing, research, insurance, financial analyst).
- Posted in the last 60 days.
- Copy the **full** job description, including the "Requirements" and "Additional information" sections at the bottom, where work-authorization lines usually appear.
- One posting per company per batch, so the dataset isn't dominated by one employer's wording.
- Label it right away using `LABELING_GUIDE.md`, before reading any model's opinion.

## Group A: likely `open` (5 per batch)
| Where | Search |
|---|---|
| LinkedIn Jobs | `"data analyst" "visa sponsorship"` |
| LinkedIn Jobs | `"business analyst" "OPT"` |
| Handshake (UCLA) | filter **"Accepts OPT/CPT"** or **"Will sponsor"**, keyword `analyst` |
| HigherEdJobs.com | `research analyst` or `institutional research` (universities, so also `cap_exempt = yes`) |
| UC / USC / university hospital career sites | `data analyst`, `research analyst` |

## Group B: likely `blocked` (5 per batch)
| Where | Search |
|---|---|
| Career sites of Lockheed Martin, Northrop Grumman, RTX, Booz Allen Hamilton, Leidos, General Dynamics | `data analyst`, `business analyst` |
| LinkedIn Jobs | `"data analyst" "U.S. citizen"` |
| LinkedIn Jobs | `"analyst" "security clearance" entry level` |
| LinkedIn Jobs | `"analyst" "without sponsorship now or in the future"` |
| LinkedIn Jobs | `"analyst" "ITAR"` |

## Group C: typical, usually `unclear` (5 per batch)
| Where | Search |
|---|---|
| LinkedIn Jobs | `"data analyst" entry level` |
| LinkedIn Jobs | `"pricing analyst"` |
| LinkedIn Jobs | `"insurance analyst"` or `"underwriting analyst"` |
| LinkedIn Jobs | `"business intelligence analyst" new grad` |

Pick postings in the order they appear in the results instead of hand-picking interesting ones. This keeps the typical group representative.

## Batch 1 checklist
- [ ] 0001: Kansas City Fed Research Associate (already read)
- [ ] 0002: University of Cincinnati Institutional Research Analyst (already read)
- [ ] 0003–0005: Group A
- [ ] 0006–0010: Group B
- [ ] 0011–0015: Group C
- [ ] Each has a `.txt` file and a row in `postings_index.csv`
