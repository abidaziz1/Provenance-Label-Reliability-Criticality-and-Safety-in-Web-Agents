"""Measure the number, criticality and concentration of security-critical label
opportunities on real DOMs. Tests Prismata's 1.2% / 0.10% structural claims."""
import json, sys, collections, math
import numpy as np

C = json.load(open('results/corpus.json'))
rows=[]
for traj in C:
    for obs in traj['observations']:
        for r in obs['regions']:
            r['n_actionable_page']=obs['n_actionable']
            r['n_nodes_page']=obs['n_nodes']
            rows.append(r)
print(f"trajectories={len(C)}  observations={sum(len(t['observations']) for t in C)}  "
      f"untrusted_regions={len(rows)}")
print(f"sites={len(set(t['site'] for t in C))}")

tot_nodes=sum(o['n_nodes'] for t in C for o in t['observations'])
tot_unt =sum(o['n_untrusted_nodes'] for t in C for o in t['observations'])
tot_act =sum(o['n_actionable'] for t in C for o in t['observations'])
print(f"\nDOM totals: nodes={tot_nodes:,}  untrusted_nodes={tot_unt:,} "
      f"({100*tot_unt/tot_nodes:.2f}%)  actionable={tot_act:,}")

# ---- Prismata claim 1: fraction of untrusted content on a critical path to an
#      actionable element
c1=[r for r in rows if r['c1']]
c2=[r for r in rows if r['c2']]
unt_nodes_in_c1=sum(r['n_desc_nodes']+1 for r in c1)
print(f"\n--- CLAIM 1  (Prismata: 1.2% of untrusted content on critical paths) ---")
print(f"untrusted REGIONS containing an actionable element (C1): {len(c1)}/{len(rows)} "
      f"= {100*len(c1)/max(len(rows),1):.2f}%")
print(f"untrusted NODES inside such regions: {unt_nodes_in_c1:,}/{tot_unt:,} "
      f"= {100*unt_nodes_in_c1/max(tot_unt,1):.2f}%")
print(f"untrusted nodes as share of ALL nodes inside C1 regions: "
      f"{100*unt_nodes_in_c1/tot_nodes:.2f}%")

# ---- Prismata claim 2: all but 0.10% have preceding structural cues
print(f"\n--- CLAIM 2  (Prismata: all but 0.10% have preceding structural cues) ---")
for name, subset in [('C1 (containment)', c1), ('C2 (exposure)', c2), ('all regions', rows)]:
    if not subset: continue
    withcue=sum(1 for r in subset if r['has_visible_cue'])
    print(f"  {name:20s} n={len(subset):5d}  cue visible to labeler: {withcue:5d} "
          f"({100*withcue/len(subset):5.1f}%)   NO cue: {len(subset)-withcue:5d} "
          f"({100*(len(subset)-withcue)/len(subset):5.2f}%)")

# ---- opportunity counts per trajectory
print(f"\n--- C PER TRAJECTORY ---")
per_traj=collections.defaultdict(lambda: dict(c1=0,c2=0,regions=0,steps=0,site=None))
for traj in C:
    k=traj['task_id']; per_traj[k]['site']=traj['site']; per_traj[k]['steps']=len(traj['observations'])
    for obs in traj['observations']:
        for r in obs['regions']:
            per_traj[k]['regions']+=1
            per_traj[k]['c1']+= 1 if r['c1'] else 0
            per_traj[k]['c2']+= 1 if r['c2'] else 0
a1=np.array([v['c1'] for v in per_traj.values()])
a2=np.array([v['c2'] for v in per_traj.values()])
for nm,a in [('C1',a1),('C2',a2)]:
    print(f"  {nm}: mean={a.mean():7.2f} median={np.median(a):6.1f} "
          f"min={a.min()} max={a.max()} zero-trajectories={int((a==0).sum())}/{len(a)}")

# ---- concentration by site  (common-cause test)
print(f"\n--- CONCENTRATION BY SITE (common-cause test) ---")
bysite=collections.defaultdict(lambda: dict(c1=0,c2=0,n=0))
for v in per_traj.values():
    bysite[v['site']]['c1']+=v['c1']; bysite[v['site']]['c2']+=v['c2']; bysite[v['site']]['n']+=1
tot1=sum(v['c1'] for v in bysite.values()); tot2=sum(v['c2'] for v in bysite.values())
ranked=sorted(bysite.items(), key=lambda kv:-kv[1]['c1'])
print(f"  {'site':16s} {'traj':>4s} {'C1':>7s} {'%C1':>7s} {'C2':>7s} {'%C2':>7s}")
for s,v in ranked:
    print(f"  {s:16s} {v['n']:4d} {v['c1']:7d} {100*v['c1']/max(tot1,1):6.1f}% "
          f"{v['c2']:7d} {100*v['c2']/max(tot2,1):6.1f}%")
def gini(x):
    x=np.sort(np.array(x,dtype=float)); n=len(x)
    if x.sum()==0: return float('nan')
    return float((2*np.arange(1,n+1)-n-1).dot(x)/(n*x.sum()))
print(f"\n  Gini(C1 across sites)={gini([v['c1'] for v in bysite.values()]):.3f}   "
      f"Gini(C2)={gini([v['c2'] for v in bysite.values()]):.3f}")
top3=sorted((v['c1'] for v in bysite.values()), reverse=True)[:3]
print(f"  top-3 sites hold {100*sum(top3)/max(tot1,1):.1f}% of all C1 opportunities")
sites_zero=[s for s,v in bysite.items() if v['c1']==0]
print(f"  sites with ZERO C1 opportunities detected: {len(sites_zero)}/{len(bysite)} {sites_zero}")

json.dump(dict(per_traj={k:v for k,v in per_traj.items()},
               bysite={k:v for k,v in bysite.items()}),
          open('results/C_measurements.json','w'), default=str)
print("\nwrote results/C_measurements.json")
