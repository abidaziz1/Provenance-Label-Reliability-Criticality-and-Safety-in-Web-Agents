# N0.3b: labeler sensitivity of the exposure rates

## Status of this folder

**Not pre-registered.** The 25 Sep adversarial review ran this analysis from its scratchpad (`research/audit/2026-09-25_adversarial_C1prime_C4.md`, Table 1 and appendix `c1p_attr.py`). Its numbers already changed the C1' verdict, so they need a script in the repo that reproduces them. This folder commits that script (`scripts/labeler_sensitivity.py`, logic unchanged) and its output. Treat every number here as exploratory.

- **Claims touched:** NOVELTY_LEDGER C1'; CLAIMS_LEDGER K18 to K20 (as-published labeler) and K24 (new, the stricter-label band).
- **Frame:** Mind2Web revision 17ece8eb89862368edc0cc806acee6fca5163474, shards train_0, train_1 and train_10, first 3 trajectories per site (`c1_robustness.PER_SITE`), 57 sites, 1,163 pages, 145 tasks. Same frame, actionability rule and non-hidden rule as `scripts/unit_ladder.py`.
- **Definitions:** a page (task) is exposed when at least one visible actionable element has an untrusted strict ancestor. Untrusted means the heuristic labeler marks the nearest seeded ancestor E (ads, cross-origin iframes), U (user content) or H (hosted content). Region roots do not count for the control rate; the target counts if it is itself untrusted or inside untrusted content. No gate is involved.
- **Variants:** V0 the labeler as published; V1 no tokens read from `data-*` values; V2 no Hosted rule; V3 no generic user-content tokens (question, answer, qa, feedback); V4 = V1 + V2 + V3; V5 ads and cross-origin iframes only, from class, id and src.
- **Reproduction check (what the rerun must show):** V0 equals the unit-ladder result (9.19% of controls, 38.09% [27.72, 49.05] of pages, 59.31% [47.18, 70.95] of tasks, 7.71% of targets, 40 sites), and the rule re-implementation agrees with `pipeline_v2.gt_provenance` on every sampled node.
- **Construct check:** these variants remove rule families; none is ground truth. The band shows how much of the exposure rate depends on rules we already know produce first-party false positives. Only the blind hand audit (task 1.7) turns it into an error rate.

## Results

Rerun on 26 Sep 2026 from the committed script (93 s). Output: `results/labeler_sensitivity.json`.

**Reproduction check: passed.** The rule re-implementation agrees with `pipeline_v2.gt_provenance` on every sampled node: 0 mismatches. V0 equals the unit ladder. Every cell of the review's Table 1 reproduces exactly.

| Labeler variant | Controls inside untrusted content | Pages exposed [95% CI] | Tasks exposed [95% CI] | Target untrusted or inside | Sites with any |
|---|---:|---|---|---:|---:|
| V0, as published | 9.19% | 38.09% [27.72, 49.05] | 59.31% [47.18, 70.95] | 7.71% | 40 |
| V1, no tokens from `data-*` values | 9.19% | 38.09% [27.72, 49.05] | 59.31% [47.18, 70.95] | 6.62% | 40 |
| V2, no Hosted rule | 2.45% | 30.70% [20.61, 42.33] | 47.59% [35.14, 60.31] | 2.72% | 32 |
| V3, no generic user-content tokens | 8.82% | 36.20% [26.03, 46.93] | 58.62% [46.48, 70.47] | 7.07% | 39 |
| V4, strict (V1 + V2 + V3) | 2.02% | 27.77% [18.00, 39.17] | 45.52% [33.09, 58.11] | 1.00% | 30 |
| V5, ads and cross-origin iframes only | 1.22% | 24.33% [14.88, 35.55] | 39.31% [27.08, 52.32] | 0.54% | 25 |

Detail under V0 (`V0_detail` in the result file):

- 443 exposed pages.
- 808 of 38,477 visible untrusted leaves are critical, and all 808 have only children the labeler seeded as developer content. This is the leaf artifact.
- 8.43% of pages have a critical leaf, against 16.37% if leaves were independent.

## Deviations

- Not pre-registered (see above).

## What this changes

- K24 gets a committed script, a result file and a test (`test_K24_labeler_sensitivity_band`). The C1' band (24% to 31% of pages and 39% to 48% of tasks under stricter labels; 38% and 59% as published) now reruns from a commit.
- Nothing in the review's conclusions changes.
