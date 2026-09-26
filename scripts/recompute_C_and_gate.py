"""Recompute C (critical untrusted regions per observation) and the gate-width
curve under the corrected pipeline, on the 57-site frame.

The audit said the <pre> splice defect had "the widest blast radius" because it
inflates actionable counts, which feed criticality, which feeds C and the gate
curve. Measured: the defect never fires on this corpus (skipped_literal = 0 over
1,163 pages), so actionable counts are byte-identical between v1 and v2. What
DOES move these figures is the same-origin iframe fix, which removes 13.7% of
untrusted regions. Both versions are computed here so the change is auditable.
"""
from pathlib import Path as _Path
ROOT = _Path(__file__).resolve().parents[1]
import json, sys, time, gc, collections, os
sys.path.insert(0, str(ROOT / 'src'))
import pipeline_v2 as P
import numpy as np
from lxml import html as LH

V1 = os.environ.get('V1_PARSER', '0') == '1'
if V1:
    P.set_fixes(literal_markup=False, splice_count=False, attr_norm=False,
                same_origin=False, cap_aware_label=False)
TAG = 'v1' if V1 else 'v2'

FILES = [f'{ROOT}/data/mind2web/data/train/train_0.json',
         f'{ROOT}/data/mind2web/data/train/train_1.json',
         f'{ROOT}/data/mind2web/data/train/train_10.json']
GATE_K = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 10**6]

bysite = collections.defaultdict(list)
for f in FILES:
    for t in json.load(open(f)): bysite[t['website']].append(t)
    gc.collect()
selected = []
for s in sorted(bysite):
    selected += sorted(bysite[s], key=lambda t: t['annotation_id'])[:3]
del bysite; gc.collect()
keep16 = {t['task_id'] for t in json.load(open(f'{ROOT}/results/legacy/corpus.json'))}
print(f"[{TAG}] frame {len(selected)} trajectories / {len(set(t['website'] for t in selected))} sites", flush=True)

def dist_to_target(el, tgt_chain):
    """ancestor-hop distance from el up to the first node shared with the target's
    root chain, plus that node's depth along the chain."""
    n, up = el, 0
    while n is not None:
        j = tgt_chain.get(id(n))
        if j is not None: return up + j
        n = n.getparent(); up += 1
    return 10**6

rows = []
gate = {k: [0, 0] for k in GATE_K}
gate16 = {k: [0, 0] for k in GATE_K}
t0 = time.time()
for i, t in enumerate(selected):
    for step, a in enumerate(t['actions']):
        try:
            tree = LH.fromstring(a['raw_html'])
        except Exception:
            continue
        P.deep_parse(tree)
        nodes = tree.xpath('//*')
        if not nodes: continue
        host = P.host_for(t['website'])
        seeds = {}
        for el in nodes:
            lab, _ = P.gt_provenance(el, host)
            if lab: seeds[el] = lab
        prov = {}
        for el in nodes:
            if el in seeds: prov[el] = seeds[el]
            else:
                p_ = el.getparent()
                prov[el] = prov[p_] if (p_ is not None and p_ in prov) else 'D'
        acts = [e for e in nodes if P.is_actionable(e)]
        anc = set()
        for x in acts:
            n = x
            while n is not None and id(n) not in anc:
                anc.add(id(n)); n = n.getparent()
        regions = [el for el in nodes if prov[el] != 'D'
                   and (el.getparent() is None or prov.get(el.getparent(), 'D') == 'D')]
        C = sum(1 for r in regions if id(r) in anc)
        rows.append(dict(task=t['annotation_id'], site=t['website'], step=step,
                         n_regions=len(regions), C=C, n_act=len(acts),
                         in16=t['annotation_id'] in keep16))
        tid = P.target_id(a)
        if not tid or not regions: continue
        tgt = next((e for e in nodes if e.get('backend_node_id') == tid), None)
        if tgt is None: continue
        chain, n, j = {}, tgt, 0
        while n is not None:
            chain[id(n)] = j; n = n.getparent(); j += 1
        ranked = sorted(acts, key=lambda e: dist_to_target(e, chain))
        for k in GATE_K:
            adm = {id(e) for e in ranked[:k]}
            adm_anc = set()
            for x in ranked[:k]:
                n = x
                while n is not None and id(n) not in adm_anc:
                    adm_anc.add(id(n)); n = n.getparent()
            nc = sum(1 for r in regions if id(r) in adm_anc)
            gate[k][0] += nc; gate[k][1] += len(regions)
            if t['annotation_id'] in keep16:
                gate16[k][0] += nc; gate16[k][1] += len(regions)
    if (i + 1) % 25 == 0:
        print(f"  [{i+1}/{len(selected)}] obs={len(rows)} ({time.time()-t0:.0f}s)", flush=True)

out = dict(rows=rows, gate={str(k): v for k, v in gate.items()},
           gate16={str(k): v for k, v in gate16.items()})
json.dump(out, open(f'{ROOT}/results/C_gate_{TAG}.json', 'w'))

def rep(rs, name):
    c = np.array([r['C'] for r in rs])
    print(f"\n[{TAG}] {name}: {len(rs)} obs")
    print(f"   regions   total {sum(r['n_regions'] for r in rs):,}   "
          f"critical {int(c.sum()):,}   = {100*c.sum()/max(sum(r['n_regions'] for r in rs),1):.2f}%")
    print(f"   C per observation : mean {c.mean():.1f}  median {np.median(c):.1f}  "
          f"p90 {np.percentile(c,90):.0f}  max {c.max()}  zero {(c==0).sum()}")
    bt = collections.defaultdict(int)
    for r in rs: bt[r['task']] += r['C']
    tv = np.array([bt[k] for k in bt])
    print(f"   C per trajectory  : mean {tv.mean():.1f}  median {np.median(tv):.1f}  "
          f"p90 {np.percentile(tv,90):.0f}  max {tv.max()}  zero {(tv==0).sum()}  "
          f"(n={len(tv)})   <- the published C aggregation")
rep(rows, '57-site frame')
rep([r for r in rows if r['in16']], '16-site published frame')
for nm, g in (('57-site frame', gate), ('16-site published frame', gate16)):
    print(f"\n[{TAG}] GATE-WIDTH SWEEP, {nm}  (critical regions / all untrusted regions)")
    print(f"   {'K':>9s} {'critical':>10s} {'total':>9s} {'fraction':>10s}")
    for k in GATE_K:
        c, n = g[k]
        print(f"   {('unbounded' if k > 10**5 else str(k)):>9s} {c:10,d} {n:9,d} "
              f"{100*c/max(n,1):9.2f}%")
print(f"[{TAG}] done in {time.time()-t0:.0f}s", flush=True)
