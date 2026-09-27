# Status

**Updated:** 26 Sep 2026, Cowork session (Claude).
**Phase:** 0 (contribution audit) and 1 (lock down). Next gate: Gate N on Oct 11.

## State

- **Where the work is.** Three branches, delivered to Alam as a git bundle because this session cannot push (HTTP 403 from the session's git proxy; anthropics/claude-code#96075). The PR bodies are in `docs/PR_BODIES_26Sep.md`.
  - `claude/baseline-v2.0`: the kit unpacked at the root, tagged `v2.0-baseline`.
  - `claude/guardrail-llm-batch`: `[guardrail]` changes: the Batch API, verified prices, a new key pattern in the secret scanner.
  - `claude/cowork-run-2`: all research work; stacked on the other two.
- **Phase 0.**
  - N0.1 to N0.4 are done.
  - The contribution statement (N0.5) is drafted. It leads with P1: page archives and site drift remove what structural defenses read.
- **Evidence for P1, all free and pre-registered where noted.**
  - K21: the archive keeps 21 attribute names and no site `data-*`, `href`, `on*`, `tabindex`, `style` or `hidden` on 57 of 57 sites.
  - K22: 24 of 25 UCM Booking hand selectors match nothing on the archive.
  - K25, C7c: on the same live DOM, stripping alone disables 53 of 57 working selectors.
  - K26, C7b: requiring an `href` halves Prismata-style criticality on the archive (ratio 0.48).
- **Reproduction.** Every number from 25 Sep reran identically on 26 Sep. The baseline is byte-identical at `v2.0-baseline`. 47 tests pass.
- **Code tasks done.**
  - 1.15: Batch API, live-tested with Anthropic.
  - 1.4: model IDs and verified prices.
  - 1.13: the notebook git convention.
  - 1.16: notebooks call models through `src/llm.py`; notebook 03 runs as one batch.
  - 1.3: coupling power and the go/no-go.
- **Drafts waiting for Alam.**
  - Emails 1.1 and 1.2.
  - The pre-registration (1.6).
  - The annotation guide and page (1.7).

## Preflight (26 Sep, this session)

| check | result |
|---|---|
| anthropic /v1/models (research key) | 200 |
| gemini /v1beta/models | 200 (free tier; Batch API refused) |
| openai /v1/models | 401 (no key; no credit yet) |
| huggingface Mind2Web | 200 |
| arxiv.org | 200 |
| semantic scholar, openalex | 429 (rate limited) |
| git clone of the private repo | ok with Alam's token |
| git push, GitHub API | refused by the session's git proxy |
| docker | not running |
| CPUs, RAM, free disk | 2, 8.2 GB, 30.9 GB |

## Spend

- API: $0.000272 logged (smoke test; about $0.0001 actually charged on the Claude key), of the $175 to $380 TMLR-route budget.

## Open PRs waiting for Alam

- None opened yet. Push the bundle, then open three PRs in this order: baseline, guardrail, recovery (H8).

## Open needs-human (in order)

1. **H8.** Push the git bundle and open the three PRs, then merge them in order.
2. **H9.** Revoke the unused Stripe, Resend and Slack keys.
3. **N0.5, Gate N by Oct 11.** Read `research/CONTRIBUTION_STATEMENT.md` and decide on P1 to P3 and the proposed drops.
4. **1.1 and 1.2.** Edit and send the two author emails; the affiliation is a placeholder.
5. **1.11.** Name the two annotators. The 1.7 audit batch needs them by Oct 9.

## Next 3 actions (Claude)

1. Write and pre-register the 1.7 item sampler, then build the first audit batch (about 100 exposure-driving seeds).
2. The C1' novelty check against web-measurement studies of third-party content, before Gate N.
3. Pre-register task 2.4 (real-agent pilot) under notebook 03's batch design, ready to run once you approve its budget ($11 to $22 at batch price).
