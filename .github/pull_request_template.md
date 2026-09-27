## Summary
<!-- one or two sentences for Alam: what this PR does, with the headline number if there is one -->

- Stacked on (open PRs this includes, or none):
- Markers: <!-- [claim] [gate] [budget] [prereg] [guardrail], or none -->

## Tasks
<!-- one section per roadmap task; copy the block -->

### Task <id>: <title>
- **Check first:** <!-- the one thing Alam should look at, and the file it is in -->
- Experiment folder and pre-registration commit:
- Results: <!-- numbers with n, intervals, frame, and the file each came from -->
- Spend: $___ of $___ budget
- Deviations from the pre-registration: none, or a list
- Construct check: <!-- one line: why this measures what the claim says -->

## Checks
- [ ] `python3 -m pytest -q tests` passes
- [ ] `python3 scripts/scan_secrets.py` is clean
- [ ] Every new number is in research/CLAIMS_LEDGER.md with its evidence file
- [ ] ROADMAP.md, RESEARCH_LOG.md and STATUS.md are updated
- [ ] Nothing in this PR merges itself or changes a guardrail without the `[guardrail]` marker
