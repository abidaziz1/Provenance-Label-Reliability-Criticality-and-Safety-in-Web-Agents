# Research log

Dated entries, newest at the bottom. Each entry: what was tried, what was found (with numbers and files), what was decided, what surprised us. Entries before 25 Sep are a summary reconstructed from `docs/context/` and `docs/history/`.

## 2026-08-26: smoke test
Prismata label-reliability smoke test on Mind2Web (`docs/history/Smoketest_EXECUTED_Results_26Aug.md`). Many of its numbers were later superseded.

## 2026-08-28: completeness audit of the smoke test
`docs/history/Smoketest_Completeness_Audit_28Aug.md`.

## 2026-09-12: 57-site frame reproduced
145 trajectories, 1,163 observations, 57 sites, 2,460,488 nodes, reproduced from the pinned dataset revision on independent hardware; 37 of 37 values matched (`docs/context/07`).

## 2026-09-18: UCM found
Untrusted Content Masking (arXiv:2607.05277) ships MIT code and makes the same structural bet as Prismata. The paper becomes a two-system comparison (`docs/context/06`).

## 2026-09-19: independent audit, corrections, reconciliation, corrected ablation
- The audit withdrew three findings and confirmed six code defects plus a seventh (`docs/context/05`, `docs/history/Independent_Research_Audit_19Sep.md`).
- The 1.2% reconciled: Prismata's figure matches the root-to-target reading (1.13% to 1.73%) and not the actionable-descendant reading (49.93%) (`docs/context/02`).
- Corrected ablation at scale, 5,088 trials: a label error with the envelope fixed gives 0.0%; propagated into a page-wide envelope 96.9%, task-scoped 0.0% (`docs/context/03`).
- The published gate is oracle-informed; a deployable gate admits about 1.8x more critical regions (`docs/context/04`).
- Surprise: under a page-wide envelope a label error adds 33.3 points of influence escape through exposure, because correct labels prune external content.

## 2026-09-24: submission roadmap
38 tasks, seven gates, $175 to $480 API budget, TMLR primary (`docs/context/01`).

## 2026-09-25: handoff to Claude Code
- Repo built with code, results, context, guardrails, skills and subagents. Tests pass; secret scan clean; `scripts/descendant_only.py` rerun from the repo reproduces its committed results byte for byte.
- Alam's direction: the primary focus is finding the true novelty and contribution. Phase 0 (novelty audit) added ahead of Phase 3 spend; Gate N on Oct 11.
- An external AI review suggested eight extensions; all parked for triage in N0.4 except the random-gate control, which goes into the pre-registration (`research/BACKLOG_IDEAS.md`).

## 2026-09-25: Phase 0 in a Cowork session (Claude)
- The repo could not be reached from the session: its git proxy refused pushes (HTTP 403) and GitHub API calls. Work was committed locally on `claude/cowork-run-1`.
- 0.2: `reconcile.py` and `descendant_only.py` reran byte-identical. N0.1: one test per claims row K1 to K12; `scripts/ablation_contrasts.py` gave the K9 and K11 intervals, [91.8, 100.0] and [15.0, 55.7].
- N0.2 novelty audit: C1 withdrawn (Prismata states one definition); C2 withdrawn as a claim about Prismata (the oracle was ours); C7 and C8 NOVEL AS MEASUREMENT; C9 and C10 INCREMENTAL.
- N0.3 adversarial review: the leaf-level "reproduction" of the 1.2% is a labeler artifact (808 of 808 critical leaves exist only through relabeled nav, menu, header or footer children); the 9.19% and 7.71% figures are mostly first-party false positives; C1' survives as descriptive; C4 is fatal as stated (its narrow envelope is the oracle target).
- 1.8: the archive keeps 21 attribute names; no site `data-*`, `href`, `on*`, `tabindex`, `style` or `hidden` survives on any of 57 sites.
- C7: 92% of UCM's hand and 96% of its LLM Booking selectors use `data-*`; on 131 archived Booking pages, 24 of 25 hand and 68 of 68 LLM selectors that match UCM's captures match nothing.

## 2026-09-26: reset, recovery, C7c, C7b, the code tasks (Claude)
- The workspace was reset overnight; the 12 local commits of 25 Sep were lost before any push. Everything whose text survived in the session was rebuilt, sent to Alam as a zip and saved to the claude.ai project. Reading the pasted keys back out of the transcript was refused by the permission system and not retried; Alam supplied the kit zip and the keys again.
- The session can clone the repo with Alam's token but still cannot push or call the GitHub API (open issue anthropics/claude-code#96075). Work is delivered as a git bundle; Alam pushes it (H8).
- 0.1 preflight: Anthropic and Gemini keys authorized (200); OpenAI 401 (no key); 2 CPUs, 8 GB RAM. 0.2: baseline byte-identical at 9b8c760 (`v2.0-baseline`).
- Every 25 Sep number was rerun and reproduces exactly: K16 to K25, and the adversarial review's Table 1 through the now-committed `scripts/labeler_sensitivity.py`.
- Fact checks through an extraction model: UCM Table 2 gives Reddit 0.997, Booking 0.879, GitLab 0.840; Claude Sonnet 4.5 wrote its selectors; the paper gives no capture date and does not discuss archives. Prismata does not state its Mind2Web data format, link rule, instance definition or per-corpus split.
- C7c (pre-registered in the project at 12:46 UTC): on the same live Booking DOM, stripping to the archive's attributes disables 53 of 57 working UCM selectors (hand 11 of 13). The homepage was blocked (HTTP 403).
- C7b (pre-registered at 8577256): requiring an `href` for links halves Prismata-style criticality on the archive, G3 19.57% to 9.40% (ratio 0.48; exploratory interval [0.32, 0.64]). It does not explain the 1.2% alone.
- 1.15 and 1.4 (guardrail PR): Batch API in `src/llm.py`; verified prices; AQ.-format Google keys now caught by the secret scanner. Smoke test: $0.000272 logged; an Anthropic batch ran end to end; Google refused a batch on the free-tier key.
- 1.13, 1.16, 1.3, 1.4 (notebooks): git convention, calls through `src/llm.py`, notebook 03 as one batch job, coupling power and go/no-go in notebook 02; a test rebuilds all three notebooks byte for byte.
- Drafts for Alam: N0.4 triage, N0.5 contribution statement, emails 1.1 and 1.2, the pre-registration (1.6), the annotation guide and page (1.7).
- Untrusted content: no page text was printed; the live captures stay in `data/`.

## 2026-09-27: Gate N passed; repo public (Claude)
- **Merges.** Alam pushed the 26 Sep bundle and merged PRs 1 to 3 in order, with merge commits; CI passed on all five runs.
- **Repo check.**
  - Main's tree equals the reviewed branch, and 47 tests pass on main.
  - A scan of all 261 blobs in history, including inside the uploaded kit zip, found no key and no personal email or phone number. The scan also covered Stripe, Resend and the `AQ.` Google key formats.
- **Gate N (Alam).** P1 is primary; P2 and P3 are conditional; the drops are approved (DECISIONS, 27 Sep).
- **Now public.** Rewrote the README around current findings, withdrawn claims and third-party licenses (Mind2Web CC BY 4.0, UCM MIT). Removed text that assumed a private repo. Added the annotator brief. Fixed the Colab commit email to the owner's GitHub noreply address.
- **Scanner.** Added Stripe and Resend key patterns (guardrail branch), because Alam may supply those keys later.
- **Backlog.** New candidate ideas O4 to O8; O4 (same-page generator test) and O5 (benchmark census) are the strongest next steps for P1.
