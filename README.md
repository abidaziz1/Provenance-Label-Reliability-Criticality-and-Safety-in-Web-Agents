# Idea 3: structural trust boundaries for web agents

A measurement study of two structural defenses against indirect prompt injection in web agents: Prismata (arXiv:2607.08147) and Untrusted Content Masking (UCM, arXiv:2607.05277). Private research repo. Target: TMLR, February 2027.

## Where it stands (25 Sep 2026)

| Result | Value | Evidence |
| --- | --- | --- |
| Prismata's 1.2% under the root-to-target reading of "critical path" | 1.13% to 1.73% (our measurement) | `docs/context/02`, `results/reconcile_v2.json` |
| Same corpus under the "actionable descendant" reading its Section 3 states | 49.93% | `results/descendant_only_v2.json` |
| Containment attack: label error with the envelope fixed / propagated page-wide / propagated task-scoped | 0.0% / 96.9% / 0.0% (controller upper bounds) | `docs/context/03`, `results/ablation_v2.json` |
| Deployable gate vs the oracle gate the published figure assumes | about 1.8x more critical regions admitted | `results/gate_comparison.json` |

All values are provisional (ledger IDs in `research/CLAIMS_LEDGER.md`). What the paper will claim is being decided now: `research/NOVELTY_LEDGER.md`.

## Layout

| Path | What |
| --- | --- |
| `CLAUDE.md` | Operating brief for Claude Code |
| `HANDOFF_GUIDE.md` | Setup steps for Alam |
| `ONBOARDING_PROMPT.md` | Prompts to start, resume and steer sessions |
| `STATUS.md`, `ROADMAP.md`, `RESEARCH_LOG.md` | Where things stand, the plan, the history |
| `research/` | Novelty and claims ledgers, decisions, corrections, human tasks, pre-registration, backlog |
| `docs/context/`, `docs/history/` | Imported project documents, frozen (`docs/00_IMPORT_MANIFEST.md`) |
| `docs/OPERATIONS.md`, `docs/EXTERNAL_SERVICES.md` | Environment, access, secrets, money |
| `src/` | Pipeline v2, scorer v2, budgeted LLM client |
| `scripts/` | Analyses, data fetch, preflight, secret scan |
| `tests/` | Audit regressions, budget guard, secret guards |
| `notebooks/` | Colab notebooks and their builders |
| `experiments/` | One folder per run from 25 Sep on |
| `results/` | Outputs up to 25 Sep, frozen |
| `legacy/` | Pre-correction code, provenance only |

## Quick check

```bash
pip install -r requirements.txt
python3 -m pytest -q tests          # 17 tests, no data needed
python3 scripts/fetch_mind2web.py   # 1.27 GB, pinned revision
python3 scripts/descendant_only.py  # about 3 minutes; reproduces 49.93% and 41.58%
```
