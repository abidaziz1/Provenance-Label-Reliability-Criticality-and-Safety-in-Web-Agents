# Claims ledger

Every number or claim that may appear in the paper, with its evidence. Gate 0: a claim is `supported` only with a script, a commit, a result file, a passing test and a construct check. `numbers-verifier` checks this file before any document goes to Alam.

Status values: `supported`, `provisional` (evidence exists, review or rerun pending), `pending` (no evidence yet), `withdrawn` (see `research/CORRECTIONS.md`).

Seeded at handoff, 25 Sep 2026. Commit column: fill with the `v2.0-baseline` tag commit in task 0.2.

| ID | Claim (with unit, root rule and gate) | Value | Frame | Result file | Script | Test | Construct check | Commit | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| K1 | Untrusted maximal regions on the root-to-target ancestor chain (strict reading) | 1.73% | 57-site, 1,103 target-resolvable observations | `results/reconcile_v2.json` | `scripts/reconcile.py`, `scripts/analyse_reconcile.py` | none yet (pipeline defects covered by the regression suite) | Matches Prismata sections 1.1 and 2.1 wording | | provisional |
| K2 | Same, region plus untrusted item children | 1.13% | as K1 | as K1 | as K1 | none yet (pipeline defects covered by the regression suite) | as K1 | | provisional |
| K3 | Regions containing an actionable descendant, region root excluded, Prismata's 7 clauses | 49.93% | 57-site, 5,317 regions | `results/descendant_only_v2.json` | `scripts/descendant_only.py` | none yet (pipeline defects covered by the regression suite) | Matches Prismata section 3 wording | | provisional |
| K4 | Same as K3 | 41.58% | 16-site, 2,054 regions | as K3 | as K3 | none yet (pipeline defects covered by the regression suite) | as K3 | | provisional |
| K5 | Same, region root counted | 71.43% (57-site), 75.85% (16-site) | as K3, K4 | as K3 | as K3 | none yet (pipeline defects covered by the regression suite) | Shows the root rule is worth 21.5 to 34.3 points | | provisional |
| K6 | Deployable target-free gate admits more critical regions than the oracle gate | about 1.8x (196 vs 106 critical regions); disagreement 7.3% | 57-site, 410 observations, 2,596 regions, K = 21 | `results/gate_comparison.json` | `scripts/gate_comparison.py` | none yet | Oracle ranks by distance to the task target | | provisional |
| K7 | Criticality across gate width | 0.71% (K of 5 or less) to 75.99% (unbounded) | 16-site | `results/C_gate_v2.json` | `scripts/recompute_C_and_gate.py` | none yet | Root-to-target construction | | provisional |
| K8 | Containment attack (A1): label error, envelope fixed: effect | 0.0% [0.0, 0.0] | 159 paired pages, 27 sites | `results/ablation_v2.json` | `scripts/ablation_v2.py` | none yet | Controller upper bound; label and gate separated | | provisional |
| K9 | Containment attack (A1): label error propagated into the envelope, page-wide vs task-scoped effect | 96.9% [91.9, 100.0] vs 0.0% | as K8 | as K8 | as K8 | none yet | as K8 | | provisional |
| K10 | Influence escape (A2) with every label correct: page-wide vs task-scoped | 43.4% vs 0.0% | as K8 | as K8 | as K8 | none yet | Supersedes 19.5% (16-site) | | provisional |
| K11 | Influence escape (A2), page-wide envelope: label error with the envelope fixed adds effect through exposure | +33.3 points [15.3, 55.2] | as K8 | as K8 | as K8 | none yet | Mechanism: correct E labels prune external content | | provisional |
| K12 | Only 3 of Prismata's 7 actionability clauses fire on Mind2Web archives | links 298,756; form controls 80,531; ARIA roles 23,307; others 0 | 57-site | see `docs/context/02` section 2.1 | `scripts/reconcile.py` | none yet | Archive attribute stripping | | provisional |
| K13 | Agent compliance with a visible injection | pending | 2.4, 3.2 | | | | | | pending |
| K14 | Cross-vendor labeler coupling | pending | 2.2, 3.1 | | | | | | pending |
| K15 | UCM reproduction (F1 and attack success) | pending | 2.5 | | | | | | pending |

No row has its own test yet. Before a row becomes `supported`, add one assertion to `tests/` that recomputes its headline value from the result file (the 33 regression assertions cover the pipeline defects, not these values). On 25 Sep 2026 the point values of K1 to K11 were recomputed from the result files and matched; the intervals in K8 to K11 and the counts in K12 are taken from `docs/context/03` and `docs/context/02` and still need recomputing.
