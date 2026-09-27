# Research log

Dated entries, newest at the bottom. Each entry: what was tried, what was found (with numbers and files), what was decided, what surprised us. Entries before 25 Sep are a summary reconstructed from `docs/context/` and `docs/history/`.

## 2026-08-26: smoke test
Prismata label-reliability smoke test on Mind2Web (`docs/history/Smoketest_EXECUTED_Results_26Aug.md`). Many of its numbers were later superseded.

## 2026-08-28: completeness audit of the smoke test
`docs/history/Smoketest_Completeness_Audit_28Aug.md`.

## 2026-09-12: 57-site frame reproduced
145 trajectories, 1,163 observations, 57 sites, 2,460,488 nodes, reproduced from the pinned dataset revision on independent hardware; 37 of 37 values matched (`docs/context/07`).

## 2026-09-18: UCM found
Untrusted Content Masking (arXiv:2607.05277) ships MIT code and makes the same structural bet as Prismata. The paper becomes a two-system comparison (`docs/context/06`).

## 2026-09-19: independent audit, corrections, reconciliation, corrected ablation
- The audit withdrew three findings and confirmed six code defects plus a seventh (`docs/context/05`, `docs/history/Independent_Research_Audit_19Sep.md`).
- The 1.2% reconciled: Prismata's figure matches the root-to-target reading (1.13% to 1.73%) and not the actionable-descendant reading (49.93%) (`docs/context/02`).
- Corrected ablation at scale, 5,088 trials: a label error with the envelope fixed gives 0.0%; propagated into a page-wide envelope 96.9%, task-scoped 0.0% (`docs/context/03`).
- The published gate is oracle-informed; a deployable gate admits about 1.8x more critical regions (`docs/context/04`).
- Surprise: under a page-wide envelope a label error adds 33.3 points of influence escape through exposure, because correct labels prune external content.

## 2026-09-24: submission roadmap
38 tasks, seven gates, $175 to $480 API budget, TMLR primary (`docs/context/01`).

## 2026-09-25: handoff to Claude Code
- Repo built with code, results, context, guardrails, skills and subagents. Tests pass; secret scan clean; `scripts/descendant_only.py` rerun from the repo reproduces its committed results byte for byte.
- Alam's direction: the primary focus is finding the true novelty and contribution. Phase 0 (novelty audit) added ahead of Phase 3 spend; Gate N on Oct 11.
- An external AI review suggested eight extensions; all parked for triage in N0.4 except the random-gate control, which goes into the pre-registration (`research/BACKLOG_IDEAS.md`).
