from pathlib import Path as _Path
ROOT = _Path(__file__).resolve().parents[1]
import json, re, time, os, gc, collections, sys
sys.path.insert(0, str(ROOT / 'legacy'))
import numpy as np
from lxml import html as LH

# reuse the verified, optimized pipeline (cells 03-04 of the reproduction notebook)
src = open(f'{ROOT}/legacy/verify_pipeline.py').read()
head = src.split('# %% [CELL 05]')[0]
head = head.split('# %% [CELL 03]')[1]
ns = {'re': re, 'json': json, 'time': time, 'os': os, 'gc': gc,
      'collections': collections, 'np': np, 'LH': LH}
exec(compile('# %% [CELL 03]' + head, 'pipeline', 'exec'), ns)
analyse_observation = ns['analyse_observation']
print("pipeline loaded", flush=True)

FILES = [f'{ROOT}/data/mind2web/data/train/train_0.json',
         f'{ROOT}/data/mind2web/data/train/train_1.json',
         f'{ROOT}/data/mind2web/data/train/train_10.json']
PER_SITE = 3   # same rule as the 16-site frame, extended to every site present

bysite = collections.defaultdict(list)
for f in FILES:
    data = json.load(open(f))
    for t in data:
        bysite[t['website']].append(t)
    del data; gc.collect()

selected = []
for s in sorted(bysite):
    cand = sorted(bysite[s], key=lambda t: t['annotation_id'])
    selected += cand[:PER_SITE]
del bysite; gc.collect()
print(f"FRAME: {len(selected)} trajectories over {len(set(t['website'] for t in selected))} sites", flush=True)

corpus = []
t0 = time.time()
for i, t in enumerate(selected):
    obs = []
    for j, a in enumerate(t['actions']):
        r = analyse_observation(a['raw_html'], a.get('cleaned_html'), a['action_uid'],
                                 t['website'], step=j, task_id=t['annotation_id'])
        if r: obs.append(r)
    corpus.append(dict(task_id=t['annotation_id'], site=t['website'], domain=t['domain'],
                        subdomain=t['subdomain'], n_steps=len(t['actions']), observations=obs))
    print(f'[{i+1}/{len(selected)}] {t["website"]:16s} steps={len(obs):2d} '
          f'regions={sum(o["n_untrusted_regions"] for o in obs):4d} ({time.time()-t0:.0f}s)', flush=True)

json.dump(corpus, open(f'{ROOT}/results/legacy/corpus57.json', 'w'))
print("WROTE corpus57.json", time.time()-t0, flush=True)
