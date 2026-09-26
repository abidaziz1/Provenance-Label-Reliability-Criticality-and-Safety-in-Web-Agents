"""Token sizes for NB1 (sanitized pages) and NB3 (transmitted observations)."""
from pathlib import Path as _Path
ROOT = _Path(__file__).resolve().parents[1]
import json, sys, collections, re, gc, random
import numpy as np
sys.path.insert(0, str(ROOT / 'src'))
src = open(f'{ROOT}/scripts/ablation_v2.py').read().split("bysite = collections.defaultdict")[0]
exec(src)
FILES = [f'{ROOT}/data/mind2web/data/train/train_{i}.json' for i in (0, 1, 10)]
bysite = collections.defaultdict(list)
for f in FILES:
    for t in json.load(open(f)): bysite[t['website']].append(t)
    gc.collect()
# NB1: 7 candidate sites, 2 trajectories x 2 pages
NB1_SITES = ["rentalcars", "seatgeek", "booking", "airbnb", "sports.yahoo", "amazon", "kohls"]
def ours_sanitize(raw_html, max_chars=200_000):
    tree = LH.fromstring(raw_html)
    for bad in tree.xpath("//script | //style | //noscript | //svg | //iframe"):
        p = bad.getparent()
        if p is not None: p.remove(bad)
    for el in tree.iter():
        if not isinstance(el.tag, str): continue
        for k in list(el.attrib):
            if k.lower().startswith("on") or k.lower() == "style": del el.attrib[k]
        if el.text and el.text.strip(): el.text = f"[text:length:{len(el.text.strip())}]"
        if el.tail and el.tail.strip(): el.tail = f"[text:length:{len(el.tail.strip())}]"
    s = LH.tostring(tree, encoding="unicode"); return len(s), s[:max_chars]
nb1 = []
for s in NB1_SITES:
    for t in sorted(bysite.get(s, []), key=lambda t: t['annotation_id'])[:2]:
        for a in t['actions'][:2]:
            full, cut = ours_sanitize(a['raw_html']); nb1.append((s, full, len(cut)))
print("NB1 pages:", len(nb1), " sites present:", sorted({x[0] for x in nb1}))
print(f"   sanitized chars sent: mean {np.mean([x[2] for x in nb1]):,.0f}  max {max(x[2] for x in nb1):,}  "
      f"pages truncated at 200k: {sum(1 for x in nb1 if x[1] > 200_000)}")
# NB3: observation sizes on the ablation pages
sel = [x for s in sorted(bysite) for x in sorted(bysite[s], key=lambda t: t['annotation_id'])[:3]]
random.seed(20260919); random.shuffle(sel)
sizes = collections.defaultdict(list); n = 0
for t in sel:
    for act in t['actions'][:6]:
        tr = build(t, act, 'page', 'A1', 'P_none', True)
        if tr is None: continue
        n += 1
        for pol in ('P_correct', 'P_none'):
            for env in ('narrow', 'page'):
                x = build(t, act, env, 'A2', pol, True)
                if x: sizes[(env, pol)].append(len(x['sent']))
print(f"NB3 trial pages: {n}")
for k, v in sizes.items():
    print(f"   {k}: mean {np.mean(v):,.0f} chars  p90 {np.percentile(v,90):,.0f}  max {max(v):,}")
allv = [x for v in sizes.values() for x in v]
json.dump(dict(nb1=[list(x) for x in nb1], nb3={f"{a}/{b}": v for (a, b), v in sizes.items()},
               nb3_mean=float(np.mean(allv))), open(f'{ROOT}/results/roadmap/budget_nb13.json', 'w'))
