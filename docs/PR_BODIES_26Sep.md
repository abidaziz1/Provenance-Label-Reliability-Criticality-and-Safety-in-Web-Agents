# Pull requests for the 26 Sep work

The Cowork session could not open PRs: its git proxy and the GitHub API refuse writes to this repository. Push the bundle, then open these three PRs in order, pasting each body. Merge each with a merge commit before opening the next. Or open all three at once, with PR 2 and PR 3 based on the branch before them.

---

## PR 1: v2.0 baseline: unpack the Idea 3 kit

- **Head:** `claude/baseline-v2.0`
- **Base:** `main`

**Body:**

Unpacks `idea3-claude-code-kit.zip` (uploaded to main as a single file in 7c571ed) at the repo root, so the repo has the layout `CLAUDE.md` and the skills expect. No file inside the kit changes. The zip leaves the tree and stays in history. Tag `v2.0-baseline` points at this commit (9b8c760).

**Check first:** `python3 -m pytest -q tests` gives 17 passed. `git diff 7c571ed 9b8c760 --stat` shows 168 files added and the zip removed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01HURbbPXTgKzA9wLDpNPsum

---

## PR 2: [guardrail] Batch API in src/llm.py, verified prices, AQ.-format key detection

- **Head:** `claude/guardrail-llm-batch`
- **Base:** `main`, after PR 1

**Body:**

This PR changes guarded files (`src/llm.py`, `scripts/scan_secrets.py`) and nothing else.

- **1.15, Batch API.** `LLM.submit_batch` and `LLM.collect_batch` support Anthropic Message Batches, the Gemini Batch API and the OpenAI Batch API.
  - A batch is priced at the provider's batch rate (50% of list) from each request's prompt length and `max_tokens`. It is checked against budget minus spent minus reserved before anything is sent.
  - A submitted batch is recorded in the experiment's `batches.json` and counts as reserved spend until it is collected. That lets a later session collect it, and stops two submissions from overcommitting.
  - Cost is logged per request from the returned usage.
  - A refused submission is logged, with its error redacted.
  - `complete()` now respects reservations too.
- **1.4, prices.** Added Claude Sonnet 4.6 ($3/$15) and `gemini-3-flash-preview` ($0.50/$3.00), both checked on the official pricing pages on 26 Sep. Also added a price for a dated model ID such as `claude-haiku-4-5-20251001`, taken from its undated entry.
- **Secret scanner.** Google now issues API keys that start with `AQ.`; the scanner and `redact()` missed them. Both catch them now.

**Check first:**
- `python3 -m pytest -q tests` gives 27 passed.
- Read `submit_batch` for the budget check. The reservation holds back direct calls too.
- `tests/test_llm_batch.py` covers all three providers with mocks.
- The live test is in the recovery PR, `experiments/2026-09-26_1.15_api-smoke-test/`. An Anthropic batch ran end to end. Google refused a batch on the free-tier Gemini key.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01HURbbPXTgKzA9wLDpNPsum

---

## PR 3: Phase 0 recovery and 26 Sep results: C7 measured, C7b and C7c, code tasks, drafts for Gate N

- **Head:** `claude/cowork-run-2`
- **Base:** `main`, after PRs 1 and 2; stacked on both

**Body:**

The 25 Sep work was lost with the cloud workspace before it could be pushed. This PR rebuilds it, reruns every number (all reproduce exactly), and adds the 26 Sep work. The experiments whose pre-registration commits were lost are marked exploratory (`research/CORRECTIONS.md`).

One task per commit:

- **N0.2, C1 robustness and unit ladder** (`exp(N0.2)`).
  - Check first: `experiments/2026-09-25_N0.2_*/` READMEs are marked "Reconstructed".
  - Check first: K16 to K20 reproduce.
- **N0.2, N0.3, N0.3b, novelty verdicts, adversarial review, labeler sensitivity.**
  - Check first: `research/NOVELTY_LEDGER.md`.
  - Check first: `scripts/labeler_sensitivity.py` reproduces the review's Table 1 cell for cell.
- **1.8, attribute census.** Check first: K21, 21 names, no site `data-*` on 57 of 57 sites.
- **C7, UCM selectors on the archive.** Check first: the corrected reading in the README, which is about reusing selectors, not UCM run on archives.
- **C7c, stripping versus drift, live.** Pre-registered in the claude.ai project before the first page load.
  - Check first: 53 of 57 live-matching selectors are disabled by stripping alone.
- **prereg(C7b) and exp(C7b).** Check first: the ratio is 0.48 (rule: at or below 0.5). The exploratory interval [0.32, 0.64] leaves "at least 2x" open.
- **1.15, smoke test.** Check first: `llm_calls.jsonl`; the spend is $0.000272 logged.
- **N0.1, per-claim tests.** Check first: `tests/test_claims.py` covers K1 to K12 and K16 to K26. The K9 and K11 intervals are now [91.8, 100.0] and [15.0, 55.7].
- **N0.4, N0.5, triage and draft contribution statement.** Check first: `research/CONTRIBUTION_STATEMENT.md`. **It needs your decision at Gate N.**
- **1.1, 1.2, 1.6, email drafts and pre-registration draft.** Check first: `outreach/`, and `research/PREREGISTRATION.md` H1 to H6.
- **1.7, annotation guide and page.** Check first: `tests/test_annotation_page.py` feeds hostile page text through the builder.
- **1.13, 1.16, 1.3, 1.4, notebooks.**
  - Check first: `tests/test_notebooks.py` rebuilds all three notebooks byte for byte.
  - Check first: notebook 03's batch scoring matches direct scoring on real pages.
- **Records.** STATUS, RESEARCH_LOG, ROADMAP, the ledgers, CORRECTIONS, DECISIONS, HUMAN_TASKS and the indexes.

**Tests:** `python3 -m pytest -q tests` gives 47 passed. Scripts that need data: `python3 scripts/fetch_mind2web.py`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01HURbbPXTgKzA9wLDpNPsum
