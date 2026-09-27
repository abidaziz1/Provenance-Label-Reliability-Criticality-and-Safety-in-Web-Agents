> Historical import manifest. Some setup files were retired during reviewer preparation; this records the original kit, not the current tree.

# Import manifest

What was imported into this repo at handoff on 25 Sep 2026, where it came from, and the order to read it in. The documents in `docs/context/` and `docs/history/` were copied byte for byte from the dated Idea 3 project archive and the 19 Sep audit report. They are frozen: never edit them. Corrections go in `research/CORRECTIONS.md`; new work goes in `research/` and `experiments/`.

## Read in this order

| # | File | Date | Source name | Read it for |
| --- | --- | --- | --- | --- |
| 1 | `docs/context/05_CORRECTIONS_19Sep2026.md` | 19 Sep | `Idea3_CORRECTIONS_19Sep2026.md` | What was withdrawn and why. Read before quoting any older number |
| 2 | `docs/context/02_Reconciliation_1.2pct.md` | 19 Sep | `Idea3_Reconciliation_1.2pct.md` | The forty-fold definitional gap (candidate C1) |
| 3 | `docs/context/03_Corrected_Ablation_Results.md` | 19 Sep | `Idea3_Corrected_Ablation_Results.md` | The four-arm ablation, exposure vs admission (C3, C4, C5) |
| 4 | `docs/context/04_Corrected_Figures.md` | 19 Sep | `Idea3_Corrected_Figures.md` | Corrected figure values, oracle vs deployable gate (C2) |
| 5 | `docs/context/01_Submission_Roadmap.md` | 24 Sep | `Idea3_Submission_Roadmap.md` | The 38 tasks, gates, budget and venue audit behind ROADMAP.md |
| 6 | `docs/context/06_Paper_Plan.md` | 18 Sep, partly superseded 24 Sep | `Idea3_Paper_Plan.md` | Framing, UCM's reported numbers, workstreams |
| 7 | `docs/context/08_PreWork_Before_Team_Start.md` | 19 Sep | `Idea3_PreWork_Before_Team_Start.md` | Pre-work items and the notebook baselines |
| 8 | `docs/context/07_Reproduction_And_Status.md` | 12 Sep, corrected 19 Sep | `Idea3_Reproduction_And_Status.md` | How the 57-site frame reproduced on independent hardware |
| 9 | `docs/history/Independent_Research_Audit_19Sep.md` | 19 Sep | the independent audit report | The audit that withdrew three findings; its bar for novelty |
| 10 | `docs/history/Smoketest_Completeness_Audit_28Aug.md` | 28 Aug | `Idea3_Smoketest_Completeness_Audit.md` | History only |
| 11 | `docs/history/Smoketest_EXECUTED_Results_26Aug.md` | 26 Aug | `Idea3_Smoketest_EXECUTED_Results.md` | History only; many numbers here are superseded |

## Known stale values

Listed in `research/CORRECTIONS.md`. The main ones: 19.5% page-wide influence escape is the 16-site value (57-site: 43.4%); 74.65% vs 1.2% is withdrawn (use 49.93% vs 1.2%); the "my sandbox" reference in doc 01 describes the original 24 September environment; doc 01's key-sending procedure is replaced by `docs/OPERATIONS.md`.

## Code and results

| Path | Origin | Notes |
| --- | --- | --- |
| `src/pipeline_v2.py`, `src/score_v2.py` | `fix/` in the 19 Sep workspace | Unchanged. The corrected pipeline and scorer |
| `scripts/*.py` (analysis) | `fix/` and `roadmap/` | Paths rewritten to repo-relative; outputs unchanged. `scripts/descendant_only.py` rerun here on 25 Sep: byte-identical |
| `tests/counterexamples_suite.py` | `fix/test_counterexamples.py` | 33 assertions for the audit's defects, wrapped by `tests/test_regression_suite.py` |
| `results/*.json`, `*.log` | `fix/` | v1 and v2 outputs of the reconciliation, ablation, gate and descendant runs |
| `results/roadmap/` | `roadmap/` | Budget and power calculations behind ROADMAP.md |
| `results/legacy/` | earlier `results/`, `scale/`, `audit/` | Pre-correction outputs, kept for provenance |
| `notebooks/colab/*_v2.ipynb` | built 19 Sep | Rebuilt from `notebooks/builders/` (depth-2 paths) |
| `legacy/` | the August and early-September code | Not runnable as is; see `legacy/README.md` |

## Written at handoff

The imported tree included the research records, analysis code, tests, notebooks, experiments, annotations, outreach drafts, and repository configuration. Reviewer-facing setup material was consolidated or retired in PR #6; dated research inputs and outputs remain available for audit. The notebook builders gained fixed cell IDs so rebuilds are byte-identical; notebook content is unchanged.
