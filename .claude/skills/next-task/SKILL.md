---
name: next-task
description: Pick the next unblocked roadmap task Claude can do and carry it to a reviewed-ready commit in the session PR. Use when told to continue, or after finishing a task.
argument-hint: "[optional task id, e.g. 1.8]"
---
1. If $ARGUMENTS names a task, take it. Otherwise take the earliest ROADMAP.md task that meets all of these:
   - its owner starts with `C` (for "C drafts, A sends" and similar, do Claude's part and hand the rest over with the human-task skill; for mixed rows such as 2.3, 3.2, 5.5 and 5.6, do Claude's part);
   - its inputs exist, and any key it needs shows 200 in the latest preflight table in STATUS.md;
   - its gate has passed according to `research/DECISIONS.md`: Phase 3 needs Gate N, 3.1 needs a go at the Oct 30 coupling check, Phase 4 needs the Dec 13 venue call to choose TDSC;
   - no open PR already claims it (check PR titles and bodies).
   Phase 0 comes before any Phase 3 spend.
2. `git fetch origin`. Stack on every open work PR of yours (not competitor-watch PRs), oldest first, and merge `origin/main`. Locally, create `task/<id>-<slug>`; in a cloud session, stay on the session's branch.
3. Make sure a PR exists for this branch and names the task (open a draft now if none exists: `gh pr create --draft`, or REST `gh api repos/{owner}/{repo}/pulls -f title=... -f head=<branch> -f base=main -F draft=true -F body=@<file>`).
4. If the task runs anything paid or produces a reported number, scaffold it with the new-experiment skill first. No paid call outside `src/llm.py`.
5. Do the work. Commit at each checkpoint; every message starts with the task ID and carries the result, e.g. `exp(2.4): NB3 pilot, compliance 31% (n=640)`.
6. Run `python3 -m pytest -q tests` and `python3 scripts/scan_secrets.py`.
7. Update ROADMAP.md status, `research/CLAIMS_LEDGER.md` and RESEARCH_LOG.md in the same branch.
8. Update the PR body: one section per task with "Check first", results, spend and deviations. Title: the task IDs and results in a few words, plus `[claim]`, `[gate]`, `[budget]`, `[prereg]` or `[guardrail]` if the PR changes one (those go in a session of their own). Edit with `gh pr edit`, or REST `gh api -X PATCH repos/{owner}/{repo}/pulls/<n> -F body=@<file>`. Never merge.
9. If something only Alam can do blocks the task, use the human-task skill and move on instead of waiting.
