# Labeling Guide

Label every posting **before** running any model, using only the posting text.

## `auth_label`

**blocked**: the posting rules out an F-1/OPT candidate who will need sponsorship later. Any one of:
- Requires U.S. citizenship, or citizenship / permanent residency ("green card holders only").
- Requires a security clearance, or the ability to obtain one.
- Requires "U.S. person" status for export-control reasons (ITAR / EAR).
- Says it will not sponsor, now or in the future ("must be authorized to work without sponsorship now or in the future", "we do not sponsor visas").

**open**: the posting is explicitly welcoming. Any one of:
- States that sponsorship is available, or that it sponsors H-1B.
- States that OPT/CPT or international students are welcome to apply.

**unclear**: neither of the above. Includes:
- No mention of work authorization at all.
- Only "must be authorized to work in the U.S." with no mention of future sponsorship (OPT holders are currently authorized, so this does not rule you out).

If a posting contains both a blocked and an open statement:
- If it **explicitly says OPT or STEM OPT holders are eligible** (for example, "F-1 visa holders with STEM OPT extension are eligible to apply"), label it **open** and write "no future sponsorship" in `notes`. You can apply, even though the employer will not sponsor later.
- Otherwise, choose **blocked** and note it.

## `cap_exempt`
`yes` if the employer is a university, a university-affiliated hospital or research institute, or a
nonprofit research organization; otherwise `no`. If unsure, `no` and add a note.

## `evidence_quote`
Copy the shortest exact sentence that justifies the label. Leave it empty for `unclear` postings with no mention.

## Balance target
Aim for at least 30 `blocked` and 20 `open` postings among ~150 total. If you are short, search for
government contractors, defense, and finance roles (often blocked) and university or large tech roles (often open).
