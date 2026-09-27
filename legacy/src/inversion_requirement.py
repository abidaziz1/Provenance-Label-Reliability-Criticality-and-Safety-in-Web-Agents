"""
GAP ANALYSIS E - what the refined direction actually REQUIRES to be true.

A safety-ranking inversion needs labeler A (better F1) to be WORSE on critical
errors than labeler B. Critical-error rate ~ eps * kappa, where kappa is how much
more likely that labeler's errors are to land on critical positions.

Inversion condition:  eps_A * kappa_A  >  eps_B * kappa_B
                      kappa_A / kappa_B  >  eps_B / eps_A
"""
import numpy as np, json
from scipy.stats import fisher_exact
rng=np.random.default_rng(20260828)
PAIRS=[('nano vs Gemini',0.0131,0.035),('nano vs mini',0.0131,0.045),
       ('Gemini vs mini',0.035,0.045),('near-matched pair',0.030,0.035)]
print("=== differential coupling required for a genuine safety inversion ===")
print(f"{'labeler pair':>20s} {'eps_A':>7s} {'eps_B':>7s} {'required kappa_A/kappa_B':>26s}")
for nm,ea,eb in PAIRS:
    print(f"{nm:>20s} {ea:7.4f} {eb:7.4f} {eb/ea:25.2f}x")
print("\n  A 2.67x DIFFERENTIAL coupling is a strong requirement. It is not enough")
print("  for errors to cluster - the better labeler must cluster onto critical")
print("  positions substantially MORE than the worse one.")

sweep={(d['K'] if d['K'] else 10**6): d for d in json.load(open('results/gate_sweep.json'))}
print("\n=== does a REAL inversion survive at scale, given differential coupling? ===")
print("simulating 20,000 studies; A has eps=1.31%, B has eps=3.50%")
for K,lab in [(21,'task-scoped'),(55,'moderate')]:
    C=sweep[K]['mean_per_traj']
    for kr in (1.0,2.0,2.67,4.0):
        for N in (200,1000):
            a=rng.poisson(N*C*0.0131*kr,20000); b=rng.poisson(N*C*0.035,20000)
            inv=float(np.mean(a>b)); tie=float(np.mean(a==b))
            if N==1000 or kr in (1.0,2.67):
                print(f"  {lab:>12s} kappa_ratio={kr:4.2f} N={N:5d}: "
                      f"A worse on critical errors in {100*inv:5.1f}% of studies "
                      f"(tie {100*tie:4.1f}%)")
print("\n=== the sample size that would SETTLE it ===")
print("To distinguish 'no differential coupling' from 'the 2.67x needed for inversion',")
print("at 80% power, you need enough critical items from BOTH labelers:")
for K,lab in [(21,'task-scoped'),(55,'moderate'),(233,"Codex's implied")]:
    C=sweep[K]['mean_per_traj']
    # need ~108 untrusted items at 2x resolution -> scale to critical items
    need_crit=108
    print(f"  {lab:>16s}: ~{int(np.ceil(need_crit/max(C,0.01))):5d} trajectories per labeler")
