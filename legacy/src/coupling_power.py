"""How much coupling could my n=131 test actually have detected? And what would
it take to settle the question properly?"""
import numpy as np
from scipy.stats import fisher_exact
rng=np.random.default_rng(20260828)

def power_fisher(n_crit,n_noncrit,p_crit,p_noncrit,B=4000,alpha=0.05):
    hits=0
    for _ in range(B):
        a=rng.binomial(n_crit,p_crit); b=rng.binomial(n_noncrit,p_noncrit)
        try:
            _,p=fisher_exact([[a,n_crit-a],[b,n_noncrit-b]])
            if p<alpha: hits+=1
        except Exception: pass
    return hits/B

BASE=0.294   # measured false-trust rate on untrusted items in my sample
print("=== power of the coupling test I just ran (15 critical-ish / 36 other) ===")
print(f"{'risk ratio':>11s} {'P(err|critical)':>16s} {'power':>8s}")
for rr in (1.5,2,3,4,6):
    pw=power_fisher(15,36,min(BASE*rr,0.99),BASE)
    print(f"{rr:10.1f}x {min(BASE*rr,0.99):15.1%} {pw:8.1%}")
print("\n  -> my test could not reliably detect even a 3x coupling. Reporting")
print("     'no coupling found' from it would be a false-negative claim.")

print("\n=== labeled untrusted items needed to detect coupling at 80% power ===")
print(f"{'risk ratio':>11s} {'items needed (1:2 crit:noncrit)':>34s}")
for rr in (1.5,2,3,4):
    lo,hi=20,4000
    need=None
    while lo<=hi:
        mid=(lo+hi)//2
        pw=power_fisher(mid,2*mid,min(BASE*rr,0.99),BASE,B=1500)
        if pw>=0.80: need=3*mid; hi=mid-1
        else: lo=mid+1
    print(f"{rr:10.1f}x {(str(need) if need else '>12000'):>34s}")

print("\n=== translating that into trajectories ===")
import json
sweep={(d['K'] if d['K'] else 10**6): d for d in json.load(open('results/gate_sweep.json'))}
print("  a trajectory yields ~43.8 untrusted regions, of which the critical share is:")
for K,lab in [(21,'task-scoped'),(55,'moderate'),(233,"Codex's implied")]:
    C=sweep[K]['mean_per_traj']
    print(f"    {lab:>16s}: {C:5.2f} critical/traj -> ~{int(np.ceil(300/max(C,0.01)))} trajectories "
          f"to accumulate 300 critical items")
