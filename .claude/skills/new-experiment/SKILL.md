---
name: new-experiment
description: Create a pre-registered experiment folder before running anything that produces a number. Use before every paid run and every analysis that feeds a claim.
argument-hint: "<task-id> <short-slug>"
---
1. Create `experiments/<YYYY-MM-DD>_<task-id>_<slug>/` by copying `experiments/_template/`.
2. Fill README.md BEFORE running: hypothesis, the claim it tests (NOVELTY_LEDGER / CLAIMS_LEDGER row), design, primary outcome, decision rule, sample size and its justification, models with exact IDs, budget in USD, construct check.
3. Estimate cost: run the script once with `IDEA3_DRY_RUN=1` and put the estimate in config.yaml, priced at list price until the Batch API lands (task 1.15). If one run would exceed $25, or the phase budget in ROADMAP.md, open a needs-human issue and wait for approval on that task only.
4. Commit the folder (`prereg(<task-id>): <slug>`) and push it before the first real call. GitHub records the push, which is what dates the pre-registration; put the commit SHA in `prereg_commit` in config.yaml.
5. Run. Open the model client with `LLM.from_experiment(<folder>)` so the cap in config.yaml applies. Results go in the folder's `results/`, logs in `logs/`; llm.py writes `llm_calls.jsonl` and `cost.json`.
6. Fill the README's results and deviations sections, add a row to experiments/README.md, and commit with the headline number in the message.
