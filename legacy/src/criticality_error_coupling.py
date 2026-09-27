"""
GAP ANALYSIS D - THE DECISIVE TEST.

The power analysis shows that under RANDOM error placement, safety rankings do not
reverse at scale (0.0% at N=1000). The refined research direction therefore only
survives if label errors are NOT independent of criticality - if labelers
systematically err MORE on the positions that matter.

Neither smoke test tested this. Codex placed errors by hand; I planted them
deliberately. But my 131 natural Claude-vs-structural disagreements carry
positional metadata, so the coupling is estimable right now.

H0: P(error | critical-position) == P(error | non-critical-position)
"""
import json, collections, numpy as np
from scipy.stats import fisher_exact, mannwhitneyu

items=json.load(open('results/label_items.json'))
sc=json.load(open('results/label_scores.json'))
lr={r['i']:r for r in sc['rows']}

rows=[]
for i,it in enumerate(items):
    if i not in lr: continue
    depth=it['path'].count('>')+1
    rows.append(dict(i=i, site=it['site'], err=not lr[i]['exact'],
                     ft=lr[i]['false_trust'], gt_unt=lr[i]['gt_unt'],
                     n_act=it['n_actionable_inside'], depth=depth,
                     textlen=len(it['text'])))
n=len(rows)
print(f"n={n} naturally-labeled items with positional metadata\n")

# Criticality proxy 1: does the region contain actionable elements at all?
# (a region with none can never be a containment opportunity)
print("=== PROXY 1: region contains actionable elements (necessary for criticality) ===")
has=[r for r in rows if r['n_act']>0]; non=[r for r in rows if r['n_act']==0]
for nm,g in [('has actionable',has),('no actionable',non)]:
    if g: print(f"  {nm:16s} n={len(g):4d}  error rate {100*sum(x['err'] for x in g)/len(g):5.1f}%")
if has and non:
    odds,p=fisher_exact([[sum(x['err'] for x in has),len(has)-sum(x['err'] for x in has)],
                         [sum(x['err'] for x in non),len(non)-sum(x['err'] for x in non)]])
    print(f"  Fisher OR={odds:.3f}  p={p:.4f}")

# Criticality proxy 2: interactive DENSITY - the more actionable elements a region
# holds, the more capability a mislabel exposes.
print("\n=== PROXY 2: interactive density vs error (continuous) ===")
e=[r['n_act'] for r in rows if r['err']]; ne=[r['n_act'] for r in rows if not r['err']]
print(f"  errored items    : median actionable inside = {np.median(e):6.1f} (n={len(e)})")
print(f"  correct items    : median actionable inside = {np.median(ne):6.1f} (n={len(ne)})")
u,p=mannwhitneyu(e,ne,alternative='two-sided')
print(f"  Mann-Whitney U={u:.0f}  p={p:.4f}")
print(f"  -> if errors concentrate on HIGH-density regions, the coupling is ADVERSE")
print(f"     (labeler fails hardest exactly where a failure exposes most capability)")

# Restrict to the security-relevant direction: false TRUST on untrusted regions
print("\n=== PROXY 2b: restricted to FALSE-TRUST errors on untrusted regions ===")
unt=[r for r in rows if r['gt_unt']]
ft=[r['n_act'] for r in unt if r['ft']]; nft=[r['n_act'] for r in unt if not r['ft']]
print(f"  false-trust items: median actionable = {np.median(ft):6.1f} (n={len(ft)})")
print(f"  correctly flagged: median actionable = {np.median(nft):6.1f} (n={len(nft)})")
if len(ft)>2 and len(nft)>2:
    u,p=mannwhitneyu(ft,nft,alternative='two-sided')
    print(f"  Mann-Whitney U={u:.0f}  p={p:.4f}")

# Criticality proxy 3: DOM depth
print("\n=== PROXY 3: DOM depth vs error ===")
de=[r['depth'] for r in rows if r['err']]; dn=[r['depth'] for r in rows if not r['err']]
print(f"  errored median depth {np.median(de):.1f} vs correct {np.median(dn):.1f}")
u,p=mannwhitneyu(de,dn,alternative='two-sided')
print(f"  Mann-Whitney U={u:.0f}  p={p:.4f}")

# Bootstrap the density difference for false-trust specifically
print("\n=== bootstrap: median interactive-density gap for false-trust errors ===")
rng=np.random.default_rng(20260828)
if len(ft)>2 and len(nft)>2:
    d=[]
    for _ in range(10000):
        d.append(np.median(rng.choice(ft,len(ft)))-np.median(rng.choice(nft,len(nft))))
    lo,hi=np.percentile(d,[2.5,97.5])
    print(f"  observed gap = {np.median(ft)-np.median(nft):+.1f} actionable elements")
    print(f"  95% CI = [{lo:+.1f}, {hi:+.1f}]   crosses zero: {lo<0<hi}")
json.dump(dict(n=n,rows=rows),open('results/coupling.json','w'))
