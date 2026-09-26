"""NB2 v2 budget and feasibility, measured rather than guessed:
(1) the power table exactly as the notebook computes it, and
(2) how many critical items the target-free gate actually yields on the 57-site frame."""
from pathlib import Path as _Path
ROOT = _Path(__file__).resolve().parents[1]
import json, sys, collections, re, gc, time
import numpy as np
from scipy.stats import fisher_exact
sys.path.insert(0, str(ROOT / 'src'))
from pipeline_v2 import *
import pipeline_v2 as P
from lxml import html as LH

rng = np.random.default_rng(20260919)
ALPHA, POWER_TARGET, TARGET_RR = 0.05, 0.80, 2.67
def power_fisher(nc, no, pc, po, B=1500):
    a_ = rng.binomial(nc, pc, B); b_ = rng.binomial(no, po, B); h = 0
    for x, y in zip(a_, b_):
        _, p = fisher_exact([[int(x), nc - int(x)], [int(y), no - int(y)]]); h += p < ALPHA
    return h / B
def need_n(base, rr, deff=1.0):
    pc = min(base * rr, 0.99); lo, hi, best = 20, 4000, None
    while lo <= hi:
        mid = (lo + hi) // 2
        if power_fisher(mid, 2 * mid, pc, base) >= POWER_TARGET: best = 3 * mid; hi = mid - 1
        else: lo = mid + 1
    return int(np.ceil(best * deff)) if best else None
DEFF = 1 + (8 - 1) * 0.240
print(f"design effect {DEFF:.2f}")
print(f"{'base':>6s} {'n indep':>8s} {'n clustered':>12s} {'critical needed':>16s}")
power = {}
for br in (0.02, 0.05, 0.10, 0.20):
    ni = need_n(br, TARGET_RR); nc = int(np.ceil(ni * DEFF)) if ni else None
    power[br] = (ni, nc)
    print(f"{br:6.0%} {str(ni):>8s} {str(nc):>12s} {str(nc//3 if nc else None):>16s}", flush=True)

STOP = set("a an the of for to in on and or with your you my me is are be at by from this that it as i we us our".split())
def toks(s): return {w for w in re.findall(r"[a-z0-9]+", (s or "").lower()) if len(w) > 2 and w not in STOP}
def elab(e): return (gattr(e,"aria_label") or gattr(e,"title") or gattr(e,"alt") or rendered_text(e)[:60] or e.get("value") or "")
def g_lex(acts, task, k):
    tt = toks(task)
    return {id(e) for e in sorted(acts, key=lambda e: -(len(tt & toks(elab(e))) / max(len(tt | toks(elab(e))), 1)))[:k]}

FILES = [f'{ROOT}/data/mind2web/data/train/train_{i}.json' for i in (0, 1, 10)]
bysite = collections.defaultdict(list)
for f in FILES:
    for t in json.load(open(f)): bysite[t['website']].append(t)
    gc.collect()
res = {}
for per_site, cap, maxp in ((3, 60, 6), (3, 120, 12), (6, 200, 20)):
    sel = [x for s in sorted(bysite) for x in sorted(bysite[s], key=lambda t: t['annotation_id'])[:per_site]]
    items = crit = 0; csites = collections.Counter(); per = collections.Counter(); t0 = time.time()
    for t in sel:
        site = t['website']
        for act in t['actions'][:maxp]:
            if per[site] >= cap: break
            tid = P.target_id(act)
            if not tid: continue
            try: tree = LH.fromstring(act['raw_html'])
            except Exception: continue
            deep_parse(tree); host = host_for(site); nodes = tree.xpath('//*')
            seeds = {}
            for el in nodes:
                l, _ = gt_provenance(el, host)
                if l: seeds[el] = l
            prov = {}
            for el in nodes:
                if el in seeds: prov[el] = seeds[el]
                else:
                    p_ = el.getparent(); prov[el] = prov[p_] if (p_ is not None and p_ in prov) else 'D'
            acts = [e for e in nodes if is_actionable(e)]
            if not acts: continue
            adm = g_lex(acts, t['confirmed_task'], 21)
            for el in nodes:
                if per[site] >= cap: break
                if prov[el] == 'D': continue
                p = el.getparent()
                if p is not None and prov.get(p, 'D') != 'D': continue
                txt = rendered_text(el)
                if not (60 <= len(txt) <= 1200): continue
                inside = [d for d in el.iterdescendants() if isinstance(d.tag, str) and is_actionable(d)]
                if is_actionable(el): inside.append(el)
                if not inside: continue
                c = any(id(d) in adm for d in inside)
                items += 1; crit += c; per[site] += 1
                if c: csites[site] += 1
    res[f"{per_site}traj_cap{cap}_pages{maxp}"] = dict(items=items, critical=crit, sites_with_critical=len(csites),
                                                      top=csites.most_common(5))
    print(f"frame {per_site} traj/site, cap {cap}, {maxp} pages/task: items={items} critical={crit} "
          f"sites_with_critical={len(csites)} top={csites.most_common(4)} ({time.time()-t0:.0f}s)", flush=True)
json.dump(dict(power={str(k): v for k, v in power.items()}, feasibility=res),
          open(f'{ROOT}/results/roadmap/budget_nb2.json', 'w'), indent=1)
