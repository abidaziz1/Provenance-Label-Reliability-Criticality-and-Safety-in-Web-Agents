"""
GAP ANALYSIS A - the natural critical fraction.

Codex's criticality definition is STRICTER than my C1: an opportunity is critical
only if it lies on the TASK TARGET's critical path (root -> the element the task
actually needs) and is gate-permitted. Their construction fixed this fraction at
10 critical / 25 untrusted = 40% by design.

Nobody has measured what it is in nature. That number decides whether the refined
research direction describes a common failure or a rare coincidence.
"""
import json, sys, ast, collections
sys.path.insert(0,'/home/claude/idea3/src')
from lxml import html as LH
from deepparse import deep_parse, rendered_text
from dom_analysis import gt_provenance, is_actionable

FILES=['data/data/train/train_0.json','data/data/train/train_1.json','data/data/train/train_10.json']
tasks=[]
for f in FILES: tasks+=json.load(open(f))
keep={t['task_id'] for t in json.load(open('results/corpus.json'))}
tasks=[t for t in tasks if t['annotation_id'] in keep]

def target_id(a):
    try:
        pc=a['pos_candidates']
        pc=ast.literal_eval(pc) if isinstance(pc,str) else pc
        if pc: return str(json.loads(pc[0]['attributes'])['backend_node_id'])
    except Exception: pass
    return None

rows=[]; per_traj=collections.defaultdict(lambda: dict(unt=0,crit=0,site=None,steps=0))
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
            l,r=gt_provenance(el)
            if l: seeds[el]=(l,r)
        prov={}
        for el in nodes:
            n=el
            while n is not None:
                if n in seeds: prov[el]=seeds[n][0]; break
                n=n.getparent()
            else: prov[el]='D'
            prov.setdefault(el,'D')
        tgt=[e for e in nodes if e.get('backend_node_id')==tid]
        if not tgt: continue
        tgt=tgt[0]
        # the TASK TARGET's critical path: root -> target
        tpath={id(x) for x in tgt.iterancestors()}; tpath.add(id(tgt))
        # maximal untrusted regions
        regions=[]
        for el in nodes:
            if prov[el]=='D': continue
            p=el.getparent()
            if p is None or prov.get(p,'D')=='D': regions.append(el)
        n_unt=len(regions)
        # STRICT criticality: region is an ancestor of the task target
        crit=[r for r in regions if id(r) in tpath]
        # LOOSER: region contains ANY actionable element (my original C1)
        loose=[r for r in regions if any(is_actionable(d) for d in r.iterdescendants())]
        k=t['annotation_id']
        per_traj[k]['site']=t['website']; per_traj[k]['steps']+=1
        per_traj[k]['unt']+=n_unt; per_traj[k]['crit']+=len(crit)
        rows.append(dict(task=k,site=t['website'],step=step,n_untrusted=n_unt,
                         n_strict_critical=len(crit),n_loose_critical=len(loose),
                         target_depth=len(list(tgt.iterancestors()))))
json.dump(dict(rows=rows,per_traj={k:v for k,v in per_traj.items()}),
          open('results/critical_fraction.json','w'))

tot_u=sum(r['n_untrusted'] for r in rows); tot_c=sum(r['n_strict_critical'] for r in rows)
tot_l=sum(r['n_loose_critical'] for r in rows)
print(f"observations with a resolvable task target: {len(rows)}")
print(f"untrusted regions total            : {tot_u:,}")
print(f"STRICT critical (on target's path) : {tot_c:,}  = {100*tot_c/max(tot_u,1):.2f}%")
print(f"LOOSE  critical (my original C1)   : {tot_l:,}  = {100*tot_l/max(tot_u,1):.2f}%")
print(f"\nCodex construction assumed          : 40.00%  (10 critical / 25 untrusted)")
print(f"ratio construction : nature (strict) = {40.0/max(100*tot_c/max(tot_u,1),1e-9):.0f}x")
obs_with=sum(1 for r in rows if r['n_strict_critical']>0)
print(f"\nobservations with >=1 strict-critical region: {obs_with}/{len(rows)} = {100*obs_with/len(rows):.1f}%")
tr_with=sum(1 for v in per_traj.values() if v['crit']>0)
print(f"trajectories with >=1 strict-critical region: {tr_with}/{len(per_traj)} = {100*tr_with/len(per_traj):.1f}%")
print(f"\nper-site strict-critical counts:")
bs=collections.defaultdict(lambda:[0,0])
for v in per_traj.values():
    bs[v['site']][0]+=v['crit']; bs[v['site']][1]+=v['unt']
for s,(c,u) in sorted(bs.items(), key=lambda kv:-kv[1][0]):
    print(f"   {s:16s} critical={c:4d}  untrusted={u:5d}  {100*c/max(u,1):5.2f}%")
