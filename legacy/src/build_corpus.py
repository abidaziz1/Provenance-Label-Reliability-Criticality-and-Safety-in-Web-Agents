import json, sys, time, os, collections, random
sys.path.insert(0,'/home/claude/idea3/src')
from dom_analysis import analyse_observation

FILES=['data/data/train/train_0.json','data/data/train/train_1.json','data/data/train/train_10.json']
# 16 sites x 3 trajectories: crossed design so site-level ICC is estimable.
# Chosen to span UGC-heavy (reviews/forums), hosted-party (marketplace listings),
# media (comments/ads) and travel (third-party inventory).
TARGET_SITES=['amazon','rottentomatoes','boardgamegeek','ign','airbnb','booking',
              'agoda','newegg','rei','kohls','uniqlo','underarmour','eventbrite',
              'travelzoo','ticketcenter','cvs']
PER_SITE=3
random.seed(20260826)

tasks=[]
for f in FILES:
    tasks += json.load(open(f))
bysite=collections.defaultdict(list)
for t in tasks: bysite[t['website']].append(t)

selected=[]
for s in TARGET_SITES:
    cand=sorted(bysite.get(s,[]), key=lambda t: t['annotation_id'])
    selected += cand[:PER_SITE]
print(f'selected {len(selected)} trajectories over {len(set(t["website"] for t in selected))} sites', flush=True)

out=[]; t0=time.time()
for i,t in enumerate(selected):
    obs=[]
    for j,a in enumerate(t['actions']):
        r=analyse_observation(a['raw_html'], a.get('cleaned_html'), a['action_uid'],
                              t['website'], step=j, task_id=t['annotation_id'])
        if r: obs.append(r)
    out.append(dict(task_id=t['annotation_id'], site=t['website'], domain=t['domain'],
                    subdomain=t['subdomain'], task=t['confirmed_task'],
                    n_steps=len(t['actions']), observations=obs))
    print(f'[{i+1}/{len(selected)}] {t["website"]:16s} steps={len(obs):2d} '
          f'regions={sum(o["n_untrusted_regions"] for o in obs):4d} '
          f'({time.time()-t0:.0f}s)', flush=True)
json.dump(out, open('results/corpus.json','w'))
print('WROTE results/corpus.json', time.time()-t0, flush=True)
