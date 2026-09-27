"""
GAP ANALYSIS B - reconciling the two criticality definitions.

My C1: untrusted region containing an actionable element                -> 46.6%
Codex strict: untrusted region on the task TARGET's critical path       ->  0.67%

Neither is simply right. Prismata composes TWO layers:
    effective_capability = min(action_gate_capability, provenance_capability)
A mislabel is critical only if the gate ALSO permits the element it exposes.
So the critical fraction is a FUNCTION OF GATE WIDTH, not a constant.

My C1 is the gate-wide-open limit. Codex's strict is near the gate-closed limit.
This sweep measures the curve between them on real DOMs.
"""
import json, sys, ast, collections
import numpy as np
sys.path.insert(0,'/home/claude/idea3/src')
from lxml import html as LH
from deepparse import deep_parse
from dom_analysis import gt_provenance, is_actionable

FILES=['data/data/train/train_0.json','data/data/train/train_1.json','data/data/train/train_10.json']
tasks=[]
for f in FILES: tasks+=json.load(open(f))
keep={t['task_id'] for t in json.load(open('results/corpus.json'))}
tasks=[t for t in tasks if t['annotation_id'] in keep]

def target_id(a):
    try:
        pc=a['pos_candidates']; pc=ast.literal_eval(pc) if isinstance(pc,str) else pc
        if pc: return str(json.loads(pc[0]['attributes'])['backend_node_id'])
    except Exception: pass
    return None

def tree_dist(a,b):
    """symmetric ancestor-hop distance between two nodes"""
    pa=[a]+list(a.iterancestors()); pb=[b]+list(b.iterancestors())
    sa={id(x):i for i,x in enumerate(pa)}
    for j,y in enumerate(pb):
        if id(y) in sa: return sa[id(y)]+j
    return 999

GATE_K=[1,2,3,5,8,13,21,34,55,89,144,233,377,10**6]
counts={k:[0,0] for k in GATE_K}     # [critical regions, total untrusted regions]
per_traj={k:collections.defaultdict(int) for k in GATE_K}
n_obs=0
for t in tasks:
    for step,a in enumerate(t['actions']):
        tid=target_id(a)
        if not tid: continue
        try:
            tree=LH.fromstring(a['raw_html']); deep_parse(tree)
        except Exception: continue
        nodes=[e for e in tree.iter() if isinstance(e.tag,str)]
        seeds={}
        for el in nodes:
            l,_=gt_provenance(el)
            if l: seeds[el]=l
        prov={}
        for el in nodes:
            n=el
            while n is not None:
                if n in seeds: prov[el]=seeds[n]; break
                n=n.getparent()
            else: prov[el]='D'
            prov.setdefault(el,'D')
        tgt=[e for e in nodes if e.get('backend_node_id')==tid]
        if not tgt: continue
        tgt=tgt[0]; n_obs+=1
        acts=[e for e in nodes if is_actionable(e)]
        # gate admits the K actionable elements closest to the task target
        ranked=sorted(acts, key=lambda e: tree_dist(e,tgt))
        regions=[]
        for el in nodes:
            if prov[el]=='D': continue
            p=el.getparent()
            if p is None or prov.get(p,'D')=='D': regions.append(el)
        for K in GATE_K:
            admitted={id(e) for e in ranked[:K]}
            for r in regions:
                counts[K][1]+=1
                inside=[d for d in r.iterdescendants() if isinstance(d.tag,str) and is_actionable(d)]
                if is_actionable(r): inside.append(r)
                if any(id(d) in admitted for d in inside):
                    counts[K][0]+=1
                    per_traj[K][t['annotation_id']]+=1
print(f"observations analysed: {n_obs}\n")
print(f"{'gate width K':>13s} {'critical regions':>17s} {'critical fraction':>18s} {'mean crit/traj':>15s}")
out=[]
for K in GATE_K:
    c,u=counts[K]
    kk='ALL' if K>10**5 else str(K)
    mt=np.mean([per_traj[K].get(t,0) for t in keep])
    print(f"{kk:>13s} {c:17,d} {100*c/max(u,1):17.2f}% {mt:15.2f}")
    out.append(dict(K=(None if K>10**5 else K),critical=c,total=u,frac=c/max(u,1),mean_per_traj=float(mt)))
json.dump(out,open('results/gate_sweep.json','w'))
