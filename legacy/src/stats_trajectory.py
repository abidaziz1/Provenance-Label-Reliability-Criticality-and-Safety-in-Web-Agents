"""Trajectory reliability statistics: independence vs correlated-error risk,
using the empirically measured C distribution and Prismata's reported error rates."""
import json, numpy as np, collections
from math import lgamma

M=json.load(open('results/C_measurements.json'))
per=M['per_traj']
C1=np.array([v['c1'] for v in per.values()],dtype=float)
C2=np.array([v['c2'] for v in per.values()],dtype=float)
sites=[v['site'] for v in per.values()]

# Prismata Fig.8 allowed-element precision -> false-trust rate = 1 - precision
EPS={'GPT-5.4-nano (P=98.69%)':0.0131,'Gemini 3 Flash (P~96.5%)':0.035,
     'GPT-5.4-mini (P~95.5%)':0.045}

def p_none_betabin(C,eps,rho):
    """P(zero false-trust errors in C correlated Bernoulli trials)."""
    if C<=0: return 1.0
    if rho<=1e-9: return (1-eps)**C
    a=eps*(1-rho)/rho; b=(1-eps)*(1-rho)/rho
    return float(np.exp(lgamma(a+b)-lgamma(b)+lgamma(b+C)-lgamma(a+b+C)))

print("=== P(at least one critical false-trust error) per trajectory ===")
print("Empirical C1 (containment opportunities): mean=%.1f median=%.1f p90=%.1f max=%d"%(
      C1.mean(),np.median(C1),np.percentile(C1,90),int(C1.max())))
print("Empirical C2 (exposure opportunities):    mean=%.1f median=%.1f p90=%.1f max=%d"%(
      C2.mean(),np.median(C2),np.percentile(C2,90),int(C2.max())))
print()
print(f"{'labeler':28s} {'rho':>6s} {'median C':>9s} {'mean C':>8s} {'corpus-avg':>11s}")
rows=[]
for name,eps in EPS.items():
    for rho in (0.0,0.1,0.3,0.5,0.8):
        med=1-p_none_betabin(np.median(C1),eps,rho)
        mn =1-p_none_betabin(C1.mean(),eps,rho)
        avg=float(np.mean([1-p_none_betabin(c,eps,rho) for c in C1]))
        rows.append((name,rho,med,mn,avg))
        print(f"{name:28s} {rho:6.2f} {100*med:8.1f}% {100*mn:7.1f}% {100*avg:10.1f}%")
print("\n=== the predeclared 10pp bar: independence vs correlated ===")
print("proceed rule: observed trajectory failure differs from independence prediction by >=10pp")
print(f"{'labeler':28s} {'indep(rho=0)':>13s} {'rho=0.1':>9s} {'rho=0.3':>9s} {'rho=0.5':>9s} {'rho=0.8':>9s} {'max gap':>9s}")
for name,eps in EPS.items():
    vals=[float(np.mean([1-p_none_betabin(c,eps,r) for c in C1])) for r in (0.0,0.1,0.3,0.5,0.8)]
    gap=max(abs(v-vals[0]) for v in vals)
    print(f"{name:28s} {100*vals[0]:12.1f}% {100*vals[1]:8.1f}% {100*vals[2]:8.1f}% "
          f"{100*vals[3]:8.1f}% {100*vals[4]:8.1f}% {100*gap:8.1f}pp")

print("\n=== effective independent opportunity count ===")
print("C_eff = log(P0)/log(1-eps), i.e. how many INDEPENDENT trials reproduce the")
print("same zero-error probability under correlation rho")
for name,eps in EPS.items():
    print(f"  {name}")
    for rho in (0.1,0.3,0.5,0.8):
        p0=float(np.mean([p_none_betabin(c,eps,rho) for c in C1]))
        ceff=np.log(p0)/np.log(1-eps)
        print(f"     rho={rho:.1f}: P(no error)={100*p0:5.1f}%  C_eff={ceff:6.1f}  "
              f"(vs mean C={C1.mean():.1f}, ratio {ceff/C1.mean():.2f})")

print("\n=== site-level concentration of opportunity (measured, not assumed) ===")
bs=collections.defaultdict(float)
for s,c in zip(sites,C1): bs[s]+=c
tot=sum(bs.values())
srt=sorted(bs.values(),reverse=True)
print(f"  top-1 site = {100*srt[0]/tot:.1f}% of all C1; top-3 = {100*sum(srt[:3])/tot:.1f}%; "
      f"top-5 = {100*sum(srt[:5])/tot:.1f}%")
def gini(x):
    x=np.sort(np.array(x,dtype=float)); n=len(x)
    return float((2*np.arange(1,n+1)-n-1).dot(x)/(n*x.sum()))
print(f"  Gini across 16 sites = {gini(list(bs.values())):.3f}")
# between-site variance share of C1 (one-way random effects on log1p scale)
import itertools
grp=collections.defaultdict(list)
for s,c in zip(sites,C1): grp[s].append(np.log1p(c))
k=len(grp); n=len(C1)
gm=np.mean([np.log1p(c) for c in C1])
ssb=sum(len(v)*(np.mean(v)-gm)**2 for v in grp.values())
ssw=sum(sum((x-np.mean(v))**2 for x in v) for v in grp.values())
msb=ssb/(k-1); msw=ssw/(n-k); n0=n/k
icc=(msb-msw)/(msb+(n0-1)*msw)
print(f"  ICC of log1p(C1) by site = {icc:.3f}  (share of variance in opportunity")
print(f"     count attributable to WHICH SITE you are on, not which task)")
json.dump(dict(icc_site=icc,gini=gini(list(bs.values())),
               C1_mean=float(C1.mean()),C1_median=float(np.median(C1))),
          open('results/stats.json','w'))
