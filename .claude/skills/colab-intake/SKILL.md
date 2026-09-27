---
name: colab-intake
description: Take in results Alam produced in Colab (pushed to a colab/<task-id> branch, large files on a data/<task-id> branch) and turn them into verified, recorded results. Use when Alam says a Colab run is done or a colab/ branch appears.
argument-hint: "<task-id>"
---
1. `git fetch origin colab/<task-id>` (and `data/<task-id>` if the notebook produced large files). Read the notebook's commit messages: they carry the headline numbers.
2. Check the run against its pre-registration in `experiments/<...>_<task-id>_<slug>/README.md`: model IDs, sample sizes, conditions, seeds. List every deviation.
3. Recompute each headline number from the raw result files with the experiment's analysis script. Run the numbers-verifier subagent on the notebook's summary.
4. Large files from `data/<task-id>`: reassemble split parts, check the SHA-256 values in the branch's `MANIFEST.json`, unpack into `data/` (gitignored). Never merge a `data/` branch into anything.
5. Merge `colab/<task-id>` into your working branch, move the results into the experiment folder if the notebook wrote them elsewhere, and fill the experiment README's results and deviations sections.
6. Update `research/CLAIMS_LEDGER.md`, ROADMAP.md, `research/HUMAN_TASKS.md` and RESEARCH_LOG.md. Close the issue with a comment linking the PR (`gh issue close <n> -c ...`, or REST `gh api -X PATCH repos/{owner}/{repo}/issues/<n> -f state=closed`). Cover the intake in your PR with its own "Check first" line.
