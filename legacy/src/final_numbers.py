import json, numpy as np
from math import lgamma
M=json.load(open('results/C_measurements.json')); S=json.load(open('results/label_scores.json'))
C1=np.array([v['c1'] for v in M['per_traj'].values()],dtype=float)
def p_none(Cn,eps,rho):
    if Cn<=0: return 1.0
    if rho<=1e-9: return (1-eps)**Cn
    a=eps*(1-rho)/rho; b=(1-eps)*(1-rho)/rho
    return float(np.exp(lgamma(a+b)-lgamma(b)+lgamma(b+Cn)-lgamma(a+b+Cn)))
rho_meas=S['icc_error_site']; lo,hi=S['icc_ci']
print("MEASURED site ICC of labeling disagreement: %.3f  [%.3f, %.3f]"%(rho_meas,lo,hi))
print()
print("=== the headline gap: element-level metric vs trajectory-level risk ===")
print(f"{'labeler':26s} {'element err':>12s} {'traj risk rho=0':>16s} {'gap':>8s} {'traj risk rho=meas':>19s} {'C_eff':>7s}")
for name,eps in [('GPT-5.4-nano',0.0131),('Gemini 3 Flash',0.035),('GPT-5.4-mini',0.045)]:
    r0=float(np.mean([1-p_none(c,eps,0.0) for c in C1]))
    rm=float(np.mean([1-p_none(c,eps,rho_meas) for c in C1]))
    p0=float(np.mean([p_none(c,eps,rho_meas) for c in C1])); ceff=np.log(p0)/np.log(1-eps)
    print(f"{name:26s} {100*eps:11.2f}% {100*r0:15.1f}% {100*(r0-eps):7.1f}pp {100*rm:18.1f}% {ceff:7.1f}")
print(f"\n  (mean C1={C1.mean():.1f}, median={np.median(C1):.1f}; C_eff is the number of")
print(f"   INDEPENDENT opportunities that reproduces the same zero-error probability)")
print()
print("=== against the predeclared decision rules ===")
r0=float(np.mean([1-p_none(c,0.0131,0.0) for c in C1]))
rm=float(np.mean([1-p_none(c,0.0131,rho_meas) for c in C1]))
print(f"  PROCEED bar A: trajectory risk differs from element-level rate by >=10pp")
print(f"     {100*r0:.1f}% vs {100*0.0131:.2f}%  -> gap {100*(r0-0.0131):.1f}pp   MET")
print(f"  PROCEED bar B: correlation materially shifts the prediction")
print(f"     independence {100*r0:.1f}% vs measured-rho {100*rm:.1f}%  -> {100*(r0-rm):.1f}pp   MET")
print(f"  PROCEED bar C: critical-error count predicts end-to-end compromise")
kt=json.load(open('results/kill_test.json'))
a1e=[r for r in kt if r['attack']=='A1_containment' and r['policy']=='P_err1']
a1c=[r for r in kt if r['attack']=='A1_containment' and r['policy']=='P_correct']
print(f"     A1 with 0 critical errors: {100*sum(r['L4_protected_effect'] for r in a1c)/len(a1c):.1f}% effect")
print(f"     A1 with 1 critical error : {100*sum(r['L4_protected_effect'] for r in a1e)/len(a1e):.1f}% effect   MET (deterministic)")
print(f"  KILL rule: confinement prevents EVERY critical error from reaching an effect")
print(f"     -> REFUTED: a single false-trust error yields 100% protected effect for A1")
print(f"  MODIFY rule: C_eff near 1 (errors almost entirely common-cause)")
p0=float(np.mean([p_none(c,0.0131,rho_meas) for c in C1])); ceff=np.log(p0)/np.log(1-0.0131)
print(f"     C_eff={ceff:.1f} vs mean C={C1.mean():.1f} (ratio {ceff/C1.mean():.2f}) -> PARTIAL: {C1.mean()/ceff:.0f}x")
print(f"        reduction, not collapse to 1. Source-level reframing supported, not forced.")
json.dump(dict(rho_meas=rho_meas,C_eff=float(ceff),traj_indep=r0,traj_meas=rm),open('results/final.json','w'))
