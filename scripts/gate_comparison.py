"""How many untrusted regions are 'critical' under a gate a defender can actually
compute, versus the oracle gate the published smoke test used?

The published criticality ranks actionable elements by tree distance to the task's
TARGET node. A defender labeling a page does not know the target: that is the thing
the agent is trying to find. So every criticality number in the smoke test is
oracle-informed. This measures the deployable alternatives on the 57-site frame.
"""
from pathlib import Path as _Path
ROOT = _Path(__file__).resolve().parents[1]
import json, sys, time, gc, collections, re, os
sys.path.insert(0, str(ROOT / 'src'))
import pipeline_v2 as P
from pipeline_v2 import *
import numpy as np
from lxml import html as LH

FILES = [f'{ROOT}/data/mind2web/data/train/train_0.json',
         f'{ROOT}/data/mind2web/data/train/train_1.json',
         f'{ROOT}/data/mind2web/data/train/train_10.json']
K = 21
STOP = set("a an the of for to in on and or with your you my me is are be at by from "
           "this that it as i we us our find show get".split())

def toks(s):
    return {w for w in re.findall(r"[a-z0-9]+", (s or "").lower())
            if len(w) > 2 and w not in STOP}

def elem_label(e):
    return (gattr(e, "aria_label") or gattr(e, "title") or gattr(e, "alt")
            or rendered_text(e)[:60] or e.get("value") or "")

def g_lexical(acts, task, tgt, k):
    tt = toks(task)
    sc = [(-(len(tt & toks(elem_label(e))) / max(len(tt | toks(elem_label(e))), 1)), i, e)
          for i, e in enumerate(acts)]
    sc.sort()
    return {id(e) for _, _, e in sc[:k]}, sum(1 for s, _, _ in sc[:k] if s < 0)

def g_doc(acts, task, tgt, k):
    return {id(e) for e in acts[:k]}, 0

def g_labelled(acts, task, tgt, k):
    """target-free, label-aware: prefer elements that carry a visible label at all,
    then lexical overlap. Bare icon links rank last."""
    tt = toks(task)
    sc = []
    for i, e in enumerate(acts):
        lab = elem_label(e).strip()
        lt = toks(lab)
        j = len(tt & lt) / max(len(tt | lt), 1)
        sc.append((-(j * 2 + (1 if lab else 0)), i, e))
    sc.sort()
    return {id(e) for _, _, e in sc[:k]}, 0

def g_oracle(acts, task, tgt, k):
    chain, n, j = {}, tgt, 0
    while n is not None: chain[id(n)] = j; n = n.getparent(); j += 1
    def d(e):
        n, up = e, 0
        while n is not None:
            if id(n) in chain: return up + chain[id(n)]
            n = n.getparent(); up += 1
        return 10**6
    return {id(e) for e in sorted(acts, key=d)[:k]}, 0

GATES = [('doc_order', g_doc), ('lexical', g_lexical),
         ('label_aware', g_labelled), ('ORACLE', g_oracle)]

bysite = collections.defaultdict(list)
for f in FILES:
    for t in json.load(open(f)): bysite[t['website']].append(t)
    gc.collect()
selected = [x for s in sorted(bysite) for x in sorted(bysite[s], key=lambda t: t['annotation_id'])[:3]]
del bysite; gc.collect()
print(f"frame {len(selected)} trajectories / {len(set(t['website'] for t in selected))} sites", flush=True)

tot = collections.Counter(); crit = collections.Counter()
agree = collections.Counter(); sites_with = collections.defaultdict(set)
n_obs = 0; lex_nonzero = 0; t0 = time.time()
for i, t in enumerate(selected):
    for act in t['actions'][:6]:
        tid = P.target_id(act)
        if not tid: continue
        try: tree = LH.fromstring(act['raw_html'])
        except Exception: continue
        deep_parse(tree); host = host_for(t['website']); nodes = tree.xpath('//*')
        seeds = {}
        for el in nodes:
            lab, _ = gt_provenance(el, host)
            if lab: seeds[el] = lab
        prov = {}
        for el in nodes:
            if el in seeds: prov[el] = seeds[el]
            else:
                p_ = el.getparent()
                prov[el] = prov[p_] if (p_ is not None and p_ in prov) else 'D'
        tgt = next((e for e in nodes if e.get('backend_node_id') == tid), None)
        if tgt is None: continue
        acts = [e for e in nodes if is_actionable(e)]
        if not acts: continue
        regions = [el for el in nodes if prov[el] != 'D'
                   and (el.getparent() is None or prov.get(el.getparent(), 'D') == 'D')]
        regions = [r for r in regions if any(is_actionable(d) for d in r.iterdescendants())
                   or is_actionable(r)]
        if not regions: continue
        n_obs += 1
        adm = {}
        for name, fn in GATES:
            s, nz = fn(acts, t['confirmed_task'], tgt, K)
            adm[name] = s
            if name == 'lexical': lex_nonzero += nz
        for r in regions:
            inside = [d for d in r.iterdescendants() if isinstance(d.tag, str) and is_actionable(d)]
            if is_actionable(r): inside.append(r)
            hit = {name: any(id(d) in adm[name] for d in inside) for name, _ in GATES}
            for name, _ in GATES:
                tot[name] += 1
                if hit[name]:
                    crit[name] += 1; sites_with[name].add(t['website'])
                if hit[name] == hit['ORACLE']: agree[name] += 1
    if (i + 1) % 25 == 0:
        print(f"  [{i+1}/{len(selected)}] obs={n_obs} ({time.time()-t0:.0f}s)", flush=True)

print(f"\nobservations with a target, actionables and >=1 actionable-bearing region: {n_obs}")
print(f"regions considered: {tot['ORACLE']:,}   K = {K}")
print(f"lexical gate: {lex_nonzero:,} of {n_obs*K:,} admitted slots had any task-token overlap "
      f"({100*lex_nonzero/max(n_obs*K,1):.1f}%)\n")
print(f"{'gate':14s} {'target-free':>12s} {'critical':>10s} {'fraction':>10s} "
      f"{'sites':>6s} {'agrees with oracle':>19s}")
for name, _ in GATES:
    print(f"{name:14s} {('no' if name=='ORACLE' else 'yes'):>12s} {crit[name]:10,d} "
          f"{100*crit[name]/max(tot[name],1):9.2f}% {len(sites_with[name]):6d} "
          f"{100*agree[name]/max(tot[name],1):18.1f}%")
json.dump(dict(K=K, n_obs=n_obs, regions=tot['ORACLE'],
               crit={k: crit[k] for k, _ in GATES},
               sites={k: len(sites_with[k]) for k, _ in GATES},
               agree={k: agree[k] for k, _ in GATES}),
          open(f'{ROOT}/results/gate_comparison.json', 'w'), indent=1)
print(f"done in {time.time()-t0:.0f}s")
