# Experiment protocol

Rules for analyses that produce a research number, including notebook runs and reconstructed experiments.

## Folder

```text
experiments/<YYYY-MM-DD>_<task-id>_<slug>/
  README.md        pre-registration, then results and deviations
  config.yaml      models, sizes, seeds, budget, data revision, script paths
  run.py           or a pointer to the script in scripts/ with its arguments
  results/         outputs; never overwritten, a rerun writes a new file
  logs/            stdout and stderr
  llm_calls.jsonl  written by src/llm.py: one line per call, no prompt text, no keys
  cost.json        written by src/llm.py
```

Register every folder in `experiments/README.md`.

## Before the run

1. Fill the README's pre-registration part: hypothesis, the claim it tests (ledger IDs), design, primary outcome, decision rule, sample size with its justification, exact model IDs, budget.
2. Dry-run with `IDEA3_DRY_RUN=1` and write the cost estimate into `config.yaml`. Over $25 for one run, or over the phase budget: needs-human issue, then wait on that task only.
3. Commit the folder as `prereg(<task-id>): <slug>` and push it before the first real call. GitHub's record of the push, not the commit's own timestamp, dates the pre-registration; put the SHA in `prereg_commit`.

## During the run

- Fix seeds and record them. Record model IDs exactly as the API returns them, the date, and temperature or other settings.
- Every paid call goes through `src/llm.py`, opened with `LLM.from_experiment(<folder>)`. Use the Batch API wherever calls are independent (50% cheaper) once task 1.15 adds it to `src/llm.py`.
- Commit checkpoints with the running numbers in the message.

## After the run

- Fill results and deviations in the README. A deviation is anything that differs from the pre-registration: sizes, models, filters, exclusions, analysis.
- Recompute headline numbers from raw files with the committed analysis script; never type a number by hand.
- Add or update rows in `research/CLAIMS_LEDGER.md`. Add a regression test for each headline number that enters the paper.

## Statistics

- The unit is the page or the item; sites cluster errors. Planning uses ICC 0.24 (design effect 2.68 at 8 items per site), which is heuristic-versus-LLM label disagreement from the 26 Aug smoke test with a 95% interval of 0.065 to 0.409 (design effect up to 3.86). Re-estimate it from human labels. Report site-clustered bootstrap 95% intervals, resampling sites.
- Paired designs: every injected trial has a no-injection control on the same page.
- Name the frame (16-site or 57-site, shards, trajectories per site) next to every number.
- A disagreement rate between labelers is not an error rate. Error rates need human labels.
- Controller results are upper bounds; say so wherever they appear.
- Correct for multiple comparisons when testing more than one primary outcome, or pre-register one primary outcome per experiment.

## The three checks from 19 Sep

Before a result is called supported, check it for the three patterns that sank three findings:

1. **One arm changes two things.** The old error arm changed the label and the gate at once.
2. **Measured on the wrong input.** A measurement on our restricted view was reported as the other system's input.
3. **Reproduction taken as validity.** A number that reproduces can still measure the wrong construct.

## Criticality numbers

State all three every time: the unit (maximal region, region plus items, block node, leaf path, node), whether the region root counts, and the gate (target-free or oracle, with K).
