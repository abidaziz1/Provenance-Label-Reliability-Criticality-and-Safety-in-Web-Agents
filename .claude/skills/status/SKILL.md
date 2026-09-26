---
name: status
description: Report where the Idea 3 project stands. Use at the start of a session or when Alam asks for status.
---
1. Read STATUS.md, ROADMAP.md, `research/HUMAN_TASKS.md` and `research/DECISIONS.md`.
2. List open needs-human issues and open PRs: `gh issue list --label needs-human --state open` and `gh pr list --state open`. REST fallback: `gh api 'repos/{owner}/{repo}/issues?labels=needs-human&state=open'` and `gh api 'repos/{owner}/{repo}/pulls?state=open'`. If both fail, say so and use HUMAN_TASKS.md and STATUS.md.
3. Report, in under 15 lines: current phase and the next gate date; tasks done since the last session; open PRs waiting for Alam's review; open needs-human items with their age; any human-task row whose need-by date falls within 14 days (flag these first); spend so far against the budget (sum `experiments/*/cost.json`); the next 3 tasks you will do without Alam.
