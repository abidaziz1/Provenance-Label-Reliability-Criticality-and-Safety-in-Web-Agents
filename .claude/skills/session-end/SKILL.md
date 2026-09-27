---
name: session-end
description: Close a work session cleanly so the next session (or Alam) can pick up. Use before stopping, before a long wait, and when context is getting full.
---
1. Run `python3 -m pytest -q tests` and `python3 scripts/scan_secrets.py`. Fix failures or record them.
2. Rewrite STATUS.md: phase, what changed this session with numbers and ledger IDs, open PRs waiting for Alam (number, one line each, what to check first), open needs-human items with need-by dates, spend to date, the next 3 actions.
3. Append a dated entry to RESEARCH_LOG.md (what you tried, what you found, what you decided, what surprised you).
4. Commit and push. Update the PR body (one section per task) and mark it ready for review if the tests pass. Never merge it.
5. In chat, give Alam a 5-line summary: done, found, needs from him, next.
