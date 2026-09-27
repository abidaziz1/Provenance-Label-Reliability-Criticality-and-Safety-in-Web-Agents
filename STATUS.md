# Status

**Updated:** 25 Sep 2026, at handoff to Claude Code.
**Phase:** 0 (setup and contribution audit) and 1 (lock down), both Sep 28 to Oct 11. Next gate: Gate N on Oct 11.

## State
- The repo holds pipeline v2, the 33 audit regressions, the budget and secret guards (17 pytest tests, all passing), every v2 result, the three v2 Colab notebooks, and the context documents (`docs/00_IMPORT_MANIFEST.md`).
- Known gaps, each with a task: no Batch API in `src/llm.py` yet (1.15); the v2 notebooks call model SDKs directly and read `ANTHROPIC_API_KEY` (1.16); no per-claim tests for K1 to K12 yet (N0.1).
- Baseline check from this repo on 25 Sep: `scripts/descendant_only.py` gives 49.93% (57-site) and 41.58% (16-site) descendants-only criticality, byte-identical to the committed results.
- Nothing has run in the new environment yet. Preflight (task 0.1) has not run.

## Spend
- API: $0 of the $175 to $380 TMLR-route budget.

## Open PRs waiting for Alam
- none yet

## Open needs-human
- H0 environment setup from HANDOFF_GUIDE.md (Alam, at handoff)
- Coming soon: H1 alert check, 1.11 team decisions, 1.14 Colab secrets (see research/HUMAN_TASKS.md for dates)

## Next 3 actions (Claude)
1. 0.1 preflight and GitHub checks.
2. 0.2 baseline reproduction in the new environment.
3. N0.1 evidence inventory, then N0.2 prior-art audit starting with C1, C2 and C4.
