import re, sys, pandas as pd
HEADER = re.compile(r'^\s*(Company|Job Title|Title|Location|Employment Type|Posted Date|Date Posted|Source|Source Platform|Job URL|URL|Search Query|Batch|Group)\s*:', re.I)
NOTE = re.compile(r'^\s*(\(?Notes?\b|\[Note|Collector note|Label|Evidence|JD text source|Full JD|LinkedIn\s*(view URL|:)|Posted on LinkedIn|Posted\b[^\n]{0,25}:|Source URL|Job URL|Source\s*:|Salary\s*:|Pay range|Job Type\s*:|Employment type\s*:)', re.I)
MARK = re.compile(r'mirror|retrieved|list page|search result|search index|crawl|not separately verified|not retrievable|assembled from', re.I)
def clean(t):
    lines = str(t).splitlines()
    # drop the metadata header block at the top
    i = 0
    while i < len(lines) and (HEADER.match(lines[i]) or not lines[i].strip()):
        i += 1
    body = []
    for l in lines[i:]:
        if NOTE.match(l):
            continue
        # remove bracketed or parenthetical collector remarks, keep the rest of the sentence
        l = re.sub(r'\s*[\[(][^\])]*?(mirror|retrieved|crawl|search result|not separately verified|assembled)[^\])]*[\])]', '', l, flags=re.I)
        if MARK.search(l) and len(l) < 600:
            continue
        body.append(l)
    out = "\n".join(body).strip()
    # drop inline collector notes such as "Note: No work-authorization ... language appears ..."
    out = re.sub(r'\s*Note:\s*No work-authorization[^\n]*', '', out, flags=re.I)
    return out
if __name__ == '__main__':
    d = pd.read_csv(sys.argv[1])
    c = d.full_job_description.map(clean)
    for k, p in {'Source:': r'Source: ', 'Job URL:': r'Job URL:', 'Note:': r'Note:', 'mirror': r'mirror', 'retrieved': r'retrieved via', 'label words': r'\b(?:blocked|unclear)\b', 'work-authorization language': r'work-authorization language'}.items():
        print(f"{k:28s} before={d.full_job_description.str.contains(p, case=False, regex=True).sum():3d} after={c.str.contains(p, case=False, regex=True).sum():3d}")
    print("chars before/after", int(d.full_job_description.str.len().sum()), int(c.str.len().sum()))
    left = c[c.str.contains(r'mirror|retrieved via|\b(?:blocked|unclear)\b|Source: ', case=False, regex=True)]
    for i, t in left.items():
        m = re.search(r'.{0,120}(mirror|retrieved via|\bblocked\b|\bunclear\b|Source: ).{0,120}', t, re.I | re.S)
        print('LEFT', d.id[i], repr(m.group(0)) if m else '')
