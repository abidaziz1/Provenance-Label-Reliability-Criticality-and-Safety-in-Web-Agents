"""Paired contrasts between policy arms of the gate ablation, with site-cluster bootstrap intervals
(claims K8, K9, K11).

Rewritten on 26 Sep 2026: the 25 Sep version was lost with the workspace before it was pushed.
Same interface: load(), pairs_for(), site_bootstrap(), compute(); writes
results/ablation_v2_contrasts.json.

A pair is the same page (key) under two policies, same envelope and attack, injected arm only.
delta_L4 is the mean over pairs of L4(policy A) - L4(policy B). The interval resamples sites with
replacement (B = 10,000, seed 20260919) and takes the 2.5th and 97.5th percentiles of the
pair-weighted mean difference.
"""
from pathlib import Path
import collections, json, sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "results" / "ablation_v2.json"
OUT = ROOT / "results" / "ablation_v2_contrasts.json"
SEED, B = 20260919, 10_000
CONTRASTS = [("P_err1_fixedgate", "P_correct"), ("P_err1_derived", "P_err1_fixedgate"),
             ("P_err1_derived", "P_correct"), ("P_none", "P_correct")]


def load(path=SRC):
    return json.load(open(path))


def pairs_for(rows, envelope, attack, a, b):
    idx = {}
    for r in rows:
        if r["arm"] == "injected" and r["envelope"] == envelope and r["attack"] == attack:
            idx[(r["policy"], r["key"])] = r
    out = []
    for (pol, key), ra in idx.items():
        if pol != a:
            continue
        rb = idx.get((b, key))
        if rb is not None:
            out.append((ra["site"], int(bool(ra["L4"])) - int(bool(rb["L4"]))))
    return out


def site_bootstrap(pairs, seed=SEED, b=B):
    by = collections.defaultdict(list)
    for s, d in pairs:
        by[s].append(d)
    sites = sorted(by)
    sums = np.array([sum(by[s]) for s in sites], dtype=float)
    cnts = np.array([len(by[s]) for s in sites], dtype=float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(sites), size=(b, len(sites)))
    means = sums[idx].sum(1) / cnts[idx].sum(1)
    return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))], len(sites)


def compute(rows):
    res = []
    for env in ("narrow", "page"):
        for atk in ("A1", "A2"):
            for a, b in CONTRASTS:
                pairs = pairs_for(rows, env, atk, a, b)
                if not pairs:
                    continue
                ci, n_sites = site_bootstrap(pairs)
                res.append({"envelope": env, "attack": atk, "contrast": f"{a} - {b}", "n_pairs": len(pairs),
                            "n_sites": n_sites, "delta_L4": sum(d for _, d in pairs) / len(pairs), "ci95": ci})
    return res


def main():
    res = compute(load())
    json.dump(res, open(OUT, "w"), indent=1)
    for c in res:
        print(f"{c['envelope']:6s} {c['attack']} {c['contrast']:36s} n={c['n_pairs']:3d} sites={c['n_sites']:2d} "
              f"delta={100*c['delta_L4']:6.1f} [{100*c['ci95'][0]:5.1f}, {100*c['ci95'][1]:5.1f}]")


if __name__ == "__main__":
    sys.exit(main())
