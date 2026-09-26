import json, collections, numpy as np
C=json.load(open('results/corpus.json'))
rows=[r for t in C for o in t['observations'] for r in o['regions']]
obs=[o for t in C for o in t['observations']]
print(f"trajectories={len(C)} observations={len(obs)} regions={len(rows)} sites={len(set(t['site'] for t in C))}")
tot_nodes=sum(o['n_nodes'] for o in obs); tot_unt=sum(o['n_untrusted_nodes'] for o in obs)
tot_cp=sum(o['n_untrusted_on_critical_path'] for o in obs)
print(f"\nnodes={tot_nodes:,} untrusted={tot_unt:,} ({100*tot_unt/tot_nodes:.2f}%) actionable={sum(o['n_actionable'] for o in obs):,}")
print(f"\n--- CLAIM 1 (Prismata: 1.2% of untrusted content lies on critical paths) ---")
print(f"  untrusted NODES that are ancestors of an actionable element:")
print(f"    {tot_cp:,} / {tot_unt:,} untrusted nodes = {100*tot_cp/tot_unt:.2f}%   [Prismata reports 1.2%]")
print(f"    as share of ALL DOM nodes: {100*tot_cp/tot_nodes:.2f}%")
c1n=sum(1 for r in rows if r['c1'])
print(f"  untrusted REGIONS containing >=1 actionable element: {c1n:,}/{len(rows):,} = {100*c1n/len(rows):.1f}%")
print(f"\n--- provenance mix of untrusted regions ---")
for k,v in collections.Counter(r['prov'] for r in rows).most_common():
    print(f"    {k}: {v:5d} ({100*v/len(rows):5.1f}%)")
print(f"\n--- CLAIM 2 (Prismata: all but 0.10% of critical untrusted content has preceding structural cues) ---")
print(f"    cue availability measured in the LABELER'S input (accessibility-tree view only)")
for nm,sub in [('C1 containment',[r for r in rows if r['c1']]),
               ('C2 exposure',[r for r in rows if r['c2']]),
               ('all regions',rows)]:
    n=len(sub) or 1
    a=sum(1 for r in sub if r.get('cue_aria')); h=sum(1 for r in sub if r['has_visible_cue'])
    s=sum(1 for r in sub if r.get('cue_selftext')); y=sum(1 for r in sub if r.get('cue_any'))
    print(f"    {nm:16s} n={len(sub):5d} | aria/role {100*a/n:5.1f}% | ancestor/heading {100*h/n:5.1f}%"
          f" | self-text {100*s/n:5.1f}% | ANY {100*y/n:5.1f}% | NO CUE {100*(n-y)/n:5.2f}%")
print(f"\n--- CSS obfuscation: does structural ground truth work on this site at all? ---")
bysite=collections.defaultdict(lambda: dict(sem=[], c1=0, c2=0, reg=0, unt=0, nodes=0))
for t in C:
    for o in t['observations']:
        b=bysite[t['site']]; b['sem'].append(o['semantic_class_ratio'])
        b['unt']+=o['n_untrusted_nodes']; b['nodes']+=o['n_nodes']
        for r in o['regions']:
            b['reg']+=1; b['c1']+=r['c1']; b['c2']+=r['c2']
print(f"  {'site':16s} {'sem-class':>9s} {'untrusted%':>11s} {'regions':>8s} {'C1':>6s} {'C2':>6s}")
for s,b in sorted(bysite.items(), key=lambda kv: np.mean(kv[1]['sem'])):
    print(f"  {s:16s} {np.mean(b['sem']):9.3f} {100*b['unt']/max(b['nodes'],1):10.2f}% {b['reg']:8d} {b['c1']:6d} {b['c2']:6d}")
per=collections.defaultdict(lambda: dict(c1=0,c2=0,site=None,steps=0))
for t in C:
    per[t['task_id']]['site']=t['site']; per[t['task_id']]['steps']=len(t['observations'])
    for o in t['observations']:
        for r in o['regions']:
            per[t['task_id']]['c1']+=r['c1']; per[t['task_id']]['c2']+=r['c2']
a1=np.array([v['c1'] for v in per.values()]); a2=np.array([v['c2'] for v in per.values()])
print(f"\n--- C PER TRAJECTORY ---")
for nm,a in [('C1',a1),('C2',a2)]:
    print(f"  {nm}: mean={a.mean():7.2f} median={np.median(a):6.1f} min={a.min()} max={a.max()} zeros={int((a==0).sum())}/{len(a)}")
json.dump({'per_traj':{k:v for k,v in per.items()},
           'bysite':{k:{kk:(float(np.mean(vv)) if kk=='sem' else vv) for kk,vv in v.items()} for k,v in bysite.items()},
           'totals':dict(nodes=tot_nodes,untrusted=tot_unt,on_critical_path=tot_cp,regions=len(rows))},
          open('results/C_measurements.json','w'))
print("\nwrote results/C_measurements.json")
