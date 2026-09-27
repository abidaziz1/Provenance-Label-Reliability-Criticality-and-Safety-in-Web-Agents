"""
GAP ANALYSIS C - is the proposed next-stage study even powered to see the effect?

Codex's mandatory gate 5 specifies "at least 50 trajectories across at least 10
sites". Nobody checked whether that is enough to OBSERVE a natural critical
false-trust error, let alone estimate a rate or detect a ranking inversion.
"""
import json, numpy as np
from math import comb, factorial
rng=np.random.default_rng(20260828)
sweep={ (d['K'] if d['K'] else 10**6): d for d in json.load(open('results/gate_sweep.json'))}
EPS={'GPT-5.4-nano (1-P=1.31%)':0.0131,'Gemini 3 Flash (~3.5%)':0.035,'GPT-5.4-mini (~4.5%)':0.045}
GATES=[(5,'very narrow'),(21,'task-scoped'),(55,'moderate'),(233,"Codex's implied"),(10**6,'unbounded (my C1)')]

print("=== expected NATURAL critical false-trust events per trajectory ===")
print(f"{'gate':>22s} {'crit/traj':>10s} " + "".join(f"{n.split(' ')[0]:>16s}" for n in EPS))
for K,lab in GATES:
    C=sweep[K]['mean_per_traj']
    row=f"{lab:>22s} {C:10.2f} "
    for n,e in EPS.items(): row+=f"{C*e:16.4f}"
    print(row)

print("\n=== trajectories needed to observe >=5 natural critical errors (80% power) ===")
def n_for_events(rate,k=5,power=0.80):
    for N in range(10,200001,10):
        lam=N*rate
        p_ge=1-sum(np.exp(-lam)*lam**i/factorial(i) for i in range(k))
        if p_ge>=power: return N
    return None
print(f"{'gate':>22s} " + "".join(f"{n.split(' ')[0]:>18s}" for n in EPS))
for K,lab in GATES:
    C=sweep[K]['mean_per_traj']; row=f"{lab:>22s} "
    for n,e in EPS.items():
        N=n_for_events(C*e)
        row+=f"{(str(N) if N else '>200k'):>18s}"
    print(row)

print("\n=== what Codex's proposed 50-trajectory pilot would actually yield ===")
for K,lab in GATES:
    C=sweep[K]['mean_per_traj']
    e=0.0131
    lam=50*C*e
    p0=np.exp(-lam)
    print(f"  {lab:>22s}: expected critical errors = {lam:6.2f}   "
          f"P(observe ZERO) = {100*p0:5.1f}%")

print("\n=== ranking-inversion detectability ===")
print("Two labelers, A better on F1. Does the SAFETY ranking reverse?")
print("Simulating 20,000 paired studies at N trajectories, errors placed at random.")
for K,lab in [(21,'task-scoped'),(233,"Codex's implied"),(10**6,'unbounded')]:
    C=sweep[K]['mean_per_traj']
    for N in (50,200,1000):
        inv=0; ties=0
        for _ in range(20000):
            # A has genuinely lower error rate than B (1.31% vs 3.5%)
            a=rng.poisson(N*C*0.0131); b=rng.poisson(N*C*0.035)
            if a>b: inv+=1
            elif a==b: ties+=1
        print(f"  {lab:>16s} N={N:5d}: safety ranking REVERSES {100*inv/20000:5.1f}% "
              f"of studies, TIED (both zero or equal) {100*ties/20000:5.1f}%")
