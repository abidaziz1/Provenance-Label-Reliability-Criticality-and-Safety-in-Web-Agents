# Pull requests for the 27 Sep work

This session still cannot push, so the work comes as a bundle with two branches. Push both, then open these two PRs against `main`. They touch different files and merge cleanly in either order; after both, the suite gives 47 passed and 1 skipped without the Mind2Web data.

---

## Gate PR: [gate] Gate N passed; the repo is public

- **Head:** `claude/gate-n-public-repo`
- **Base:** `main`

**Body:**

- **[gate] Gate N.** Records your decision of 27 Sep in `research/DECISIONS.md`, `research/CONTRIBUTION_STATEMENT.md`, `ROADMAP.md` and `research/HUMAN_TASKS.md`.
  - P1 is primary.
  - P2 and P3 stay conditional.
  - 1.10, 2.3, 2.6, 3.1, 4.1 and 4.2 are dropped.
  - The coupling go/no-go, the venue call and the mechanism check retire.
- **Public repo.**
  - The README is rewritten for outside readers: current findings with claim IDs, what they do not show, the three withdrawn claims, and third-party terms. Text that assumed a private repo is gone.
  - `THIRD_PARTY_NOTICES.md` carries UCM's MIT notice and Mind2Web's CC BY 4.0 attribution.
  - The email drafts link the repo and leave your name blank; authors' replies stay out of the public repo (`outreach/README.md`).
  - Branch protection is noted as free.
- **Annotator brief.** `annotations/ANNOTATOR_BRIEF.md` is a one-page, plain-language brief you can forward to two annotators.
- **Colab fix.** Commits from Colab now use your GitHub noreply address, so they link to your account.
- **Backlog.** New candidate ideas O4 to O9. O9 notes that UCM's released GitLab marker masks nothing, and logs nothing, when its selectors match nothing; it is a check to run, not a claim.

**Check first:**
- Read `README.md` as a stranger would: it should not overstate anything about Prismata or UCM.
- Check the Gate N row in `research/DECISIONS.md` matches what you decided.
- `python3 -m pytest -q tests` gives 46 passed and 1 skipped without the Mind2Web data (the notebook check needs one shard), 47 passed with it.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01HURbbPXTgKzA9wLDpNPsum

---

## Guardrail PR: [guardrail] Scanner: Stripe keys, Stripe webhook secrets, Resend keys

- **Head:** `claude/guardrail-scanner-more-keys`
- **Base:** `main`

**Body:**

You may supply Stripe or Resend keys later. The secret scanner did not know either format, so a commit containing one would have passed the hooks and CI. This adds three patterns and a test that builds its fake keys at runtime and checks two near-misses. With these patterns, a scan of all 261 blobs in the repo's history and the 168 files inside the uploaded zip found nothing.

**Check first:** `python3 -m pytest -q tests/test_secret_guards.py` gives 8 passed. `python3 scripts/scan_secrets.py --all` prints "secret scan clean".

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01HURbbPXTgKzA9wLDpNPsum
