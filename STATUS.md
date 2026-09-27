# Status

**Updated:** 27 Sep 2026, Cowork session (Claude).
**Phase:** 1 (lock down P1). Gate N passed on 27 Sep. Next gate: Gate 1 (UCM reproduces), 8 Nov.

## State

- **Gate N passed on 27 Sep.** P1 is the primary contribution: page archives and site drift remove what structural defenses read. P2 and P3 stay conditional on the real-agent pilot (2.4) and the hand audit (1.7). Dropped: 1.10, 2.3, 2.6, 3.1 and Phase 4; the target is TMLR, with DTRAP as the floor.
- **The repo is public.**
  - PRs 1 to 3 are merged in order, and CI passed on every run.
  - A scan of all 261 blobs in its history and the 168 files inside the uploaded zip found no key and no personal contact detail. Commit metadata carries only noreply addresses.
  - The README now states current findings, withdrawn claims and third-party licenses.
- **Evidence for P1.**
  - K21: the archive keeps 21 attribute names.
  - K22: 24 of 25 UCM Booking hand selectors match nothing on the archive.
  - K25: stripping alone disables 53 of 57 working selectors on the same live DOM.
  - K26: requiring an `href` halves Prismata-style criticality.
- **Open question for P1.** Does UCM's own generator still work on stripped pages? Backlog O4 answers it without annotators, for about $7.
- **Drafts waiting for Alam.**
  - The emails (`outreach/`): send the Prismata one; the UCM one is optional. Both now link the public repo and leave your name blank for you to fill in.
  - The annotator brief (`annotations/ANNOTATOR_BRIEF.md`), needed only if P3 stays in play.

## Preflight (26 Sep, this session)

| check | result |
|---|---|
| anthropic /v1/models (research key) | 200 |
| gemini /v1beta/models | 200 (free tier; Batch API refused) |
| openai /v1/models | 401 (no key; no credit yet) |
| huggingface Mind2Web | 200 |
| arxiv.org | 200 |
| semantic scholar, openalex | 429 (rate limited) |
| git clone of the repo | ok (public since 27 Sep) |
| git push, GitHub API | refused by the session's git proxy |
| docker | not running |
| CPUs, RAM, free disk | 2, 8.2 GB, 30.9 GB |

## Spend

- API: $0.000272 logged (smoke test; about $0.0001 actually charged on the Claude key), of the $175 to $380 TMLR-route budget.

## Open PRs waiting for Alam

- This session still cannot push. The Gate N and public-repo work comes as a bundle with two branches, `claude/gate-n-public-repo` and `claude/guardrail-scanner-more-keys`.

## Open needs-human (in order)

1. **H8b.** Push the new bundle and merge its two PRs.
2. **H10.** Protect main; this is free now that the repo is public.
3. **H9.** Revoke the unused Stripe, Resend and Slack keys.
4. **1.1.** Send the Prismata email (recommended). 1.2, the UCM email, is optional.
5. **P3 decision.** Name two annotators if you want P3 tested (`annotations/ANNOTATOR_BRIEF.md`); otherwise P3 becomes a paragraph.
6. **O4.** Say yes or no to the same-page generator test, about $7.
7. **H11.** Choose a license.

## Next 3 actions (Claude)

1. O5, the free benchmark census of defense inputs, and the O9 fail-open construct check (free).
2. O4, pre-registered, once you say yes.
3. The 1.7 item sampler and first audit batch, if you keep P3.
