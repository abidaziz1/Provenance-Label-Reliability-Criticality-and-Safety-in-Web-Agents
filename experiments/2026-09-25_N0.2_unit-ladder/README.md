# N0.2: exposure per element, page and task (candidate C1')

## Status of this file

**Reconstructed on 26 Sep 2026.** The original README (pre-registration in local commit 30178d3, results in a5eb3aa) was lost with the workspace before any push. The pre-registration cannot be checked, so treat this experiment as exploratory. The script, `scripts/unit_ladder.py`, survived unchanged. Rerunning it needs `src/pipeline_v2.py` from the kit.

## What it measures

Whether an agent meets a visible actionable element inside untrusted content, per element, page and task. Same frame, labels and actionability rule as `scripts/c1_robustness.py`. The page and task rates get site-cluster bootstrap intervals (B = 10,000, seed 20260925).

## Results recorded on 25 Sep (tests in `tests/test_claims.py`)

| Measure | Value | Claim |
| --- | --- | --- |
| Frame | 1,163 pages, 145 tasks, 57 sites | |
| Visible actionable elements with an untrusted strict ancestor | 9.19% | K18 |
| Pages exposed | 38.09% [27.72, 49.05] | K19 |
| Tasks exposed | 59.31% [47.18, 70.95] | K19 |
| Targets untrusted or inside untrusted content | 7.71% | K20 |

## After the adversarial review

- The 9.19% and 7.71% figures are mostly first-party false positives from the heuristic labeler. Stricter labels give 1.2% to 2.5% and 0.5% to 2.7%.
- The page and task rates survive at lower levels under stricter labels: 24% to 31% of pages (about 17% without five first-party-promotion sites, per a review snippet that was never committed) and 39% to 48% of tasks. See `experiments/2026-09-25_N0.3b_labeler-sensitivity/`.
- The per-page cap for Prismata's Mind2Web half is 38.35% (1,086 / 2,832) for any critical path and 3.32% (94 / 2,832) for Case 3. The 25 Sep README used the pooled 19.17%; see `research/CORRECTIONS.md`.
