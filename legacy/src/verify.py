import json, collections, numpy as np, sys
sys.path.insert(0,'/home/claude/idea3/src')
print("="*72); print("V1  Claim-1 recomputed at three granularities + ads excluded"); print("="*72)
C=json.load(open('results/corpus.json'))
obs=[o for t in C for o in t['observations']]
rows=[r for t in C for o in t['observations'] for r in o['regions']]
tot_unt=sum(o['n_untrusted_nodes'] for o in obs); tot_cp=sum(o['n_untrusted_on_critical_path'] for o in obs)
print(f"  node granularity      : {100*tot_cp/tot_unt:.2f}% of untrusted nodes are ancestors of an actionable el")
print(f"  region granularity    : {100*sum(1 for r in rows if r['c1'])/len(rows):.2f}% of untrusted regions contain one")
uh=[r for r in rows if r['prov'] in ('U','H')]
print(f"  U/H only (ads excluded, since ads are pruned regardless):")
print(f"      {100*sum(1 for r in uh if r['c1'])/max(len(uh),1):.2f}% of {len(uh)} U/H regions contain an actionable el")
e=[r for r in rows if r['prov']=='E']
print(f"      {100*sum(1 for r in e if r['c1'])/max(len(e),1):.2f}% of {len(e)} E (ad) regions")
print("  -> the discrepancy with Prismata's 1.2% is NOT an artifact of counting ads.")

print(); print("="*72); print("V2  does cue availability predict labeling error?  (convergent validity)"); print("="*72)
items=json.load(open('results/label_items.json'))
sc=json.load(open('results/label_scores.json')); lr={r['i']:r for r in sc['rows']}
# recompute cue availability for the labeled items from their path/text
import re
from dom_analysis import CUE_WORDS, SELF_CUE
tab=collections.Counter()
for i,it in enumerate(items):
    if i not in lr: continue
    cue = bool(CUE_WORDS.search(it['path'])) or bool(SELF_CUE.search(it['text'][:200]))
    tab[(cue, not lr[i]['exact'])]+=1
cw_err=tab[(True,True)]; cw_ok=tab[(True,False)]; nc_err=tab[(False,True)]; nc_ok=tab[(False,False)]
print(f"  cue present in labeler input : error {cw_err}/{cw_err+cw_ok} = {100*cw_err/max(cw_err+cw_ok,1):.1f}%")
print(f"  NO cue in labeler input      : error {nc_err}/{nc_err+nc_ok} = {100*nc_err/max(nc_err+nc_ok,1):.1f}%")
from scipy.stats import fisher_exact
odds,p=fisher_exact([[cw_err,cw_ok],[nc_err,nc_ok]])
print(f"  Fisher exact: OR={odds:.3f}  p={p:.4f}")
print("  -> if p<0.05, the cue measurement and the error measurement are the same")
print("     phenomenon seen twice, not two unrelated claims.")

print(); print("="*72); print("V3  beta-binomial vs Monte Carlo (statistical sanity)"); print("="*72)
from math import lgamma
def p_none(Cn,eps,rho):
    if Cn<=0: return 1.0
    if rho<=1e-9: return (1-eps)**Cn
    a=eps*(1-rho)/rho; b=(1-eps)*(1-rho)/rho
    return float(np.exp(lgamma(a+b)-lgamma(b)+lgamma(b+Cn)-lgamma(a+b+Cn)))
rng=np.random.default_rng(7)
for Cn,eps,rho in [(14,0.0131,0.3),(35,0.035,0.1),(35,0.045,0.5)]:
    a=eps*(1-rho)/rho; b=(1-eps)*(1-rho)/rho
    p=rng.beta(a,b,400000); mc=float(np.mean((1-p)**Cn))
    print(f"  C={Cn} eps={eps} rho={rho}: closed-form P0={p_none(Cn,eps,rho):.5f}  MonteCarlo={mc:.5f}  diff={abs(p_none(Cn,eps,rho)-mc):.5f}")

print(); print("="*72); print("V4  kill-test controller: is the substring match over-firing?"); print("="*72)
kt=json.load(open('results/kill_test.json'))
sub=[r for r in kt if r['envelope']=='page' and r['attack']=='A2_influence_escape' and r['policy']=='P_correct']
hit=[r for r in sub if r['L4_protected_effect']]
print(f"  page/A2/P_correct: {len(hit)}/{len(sub)} effects = {100*len(hit)/len(sub):.1f}%")
print(f"  distinct attacker target labels among hits (first 12):")
for l in list(dict.fromkeys(r['a2_label'] for r in hit))[:12]: print(f"      {l!r}")
print(f"  all hits had a damaging-verb target: {all(r['a2_damaging'] for r in hit)}")
print(f"  region provenance of hits: {dict(collections.Counter(r['region_prov'] for r in hit))}")
print("  NOTE: P_correct exposure is 38.1% because E (ad) regions are PRUNED under a")
print("  correct label; only U/H survive as read-only. Effects can only come from U/H.")
uh_sub=[r for r in sub if r['region_prov'] in ('U','H')]
print(f"  effect rate CONDITIONAL on the injection landing in U/H (i.e. reachable at all):")
print(f"      {sum(1 for r in uh_sub if r['L4_protected_effect'])}/{len(uh_sub)} = "
      f"{100*sum(1 for r in uh_sub if r['L4_protected_effect'])/max(len(uh_sub),1):.1f}%")
