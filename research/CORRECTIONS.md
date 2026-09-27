# Corrections

Any change to a number or claim that was already written down, anywhere. Never edit an old number silently: log it here, then fix the document and mark the fix in place.

The full record of the 19 Sep 2026 corrections is `docs/context/05_CORRECTIONS_19Sep2026.md`. Read it before quoting any number from a document dated before 19 Sep.

| Date | Where | Was | Now | Why | Evidence |
| --- | --- | --- | --- | --- | --- |
| 2026-09-19 | all docs | 74.65% vs 1.2% | 49.93% vs 1.2% (descendants only, 57-site) | The root rule and the critical-path definition | `docs/context/02` |
| 2026-09-19 | all docs | "0% to 100% on one label error" | withdrawn; replaced by K8 and K9 in the claims ledger | The error arm changed the label and the gate at once | `docs/context/03`, `docs/context/05` |
| 2026-09-19 | all docs | "79.46% of critical regions carry no cue" and "95.27% once ads are excluded" | withdrawn | Measured on a view without class names; Prismata's labeler reads class names | `docs/context/05` |
| 2026-09-19 | gate curve | 0.67% to 77.44% (as published) | 0.71% to 75.99% (corrected) | Pipeline fixes | `docs/context/04` |
| 2026-09-19 | influence escape, page-wide, correct labels | 19.5% | 43.4% | 19.5% is the 16-site frame; 43.4% is the 57-site frame with a broader damaging-control set | `docs/context/03` section 3 |
| 2026-09-25 | Prismata citations in our docs | critical-path definition cited as §2.1; "90,408 instances" attributed to §1.1 | §2.2 (Action gate); §1.1 says "over 90,000"; 90,408 = 65,416 Mind2Web + 24,992 Common Crawl is in §3 | Fact check against arXiv:2607.08147v1 | `research/audit/2026-09-25_C1_C2_C10.md` |
| 2026-09-25 | C1 and claims row K1 | the 1.2% "matches the root-to-target reading" Prismata gives in §1.1 and §2.1; "a forty-fold definitional gap" | Prismata states one definition three times (§1.1, §2.2, §3): an untrusted path is critical when it has a non-hidden actionable descendant. The root-to-target reading was our hypothesis. C1 withdrawn | N0.2 novelty audit | `research/audit/2026-09-25_C1_C2_C10.md`, `research/NOVELTY_LEDGER.md` |
| 2026-09-25 | C2 | "the published criticality gate is oracle-informed" | The oracle (distance to the annotated target) is in our 18 Sep reconstruction. Prismata's gate is `ActionGate(path(e), task)` through an LLM. Kept only as a correction to our own instrument (K6) | N0.2 novelty audit | as above |
| 2026-09-25 | Claims rows K9 and K11 | intervals [91.9, 100.0] and [15.3, 55.2] | [91.8, 100.0] and [15.0, 55.7] from `scripts/ablation_contrasts.py` (site bootstrap, B = 10,000, seed 20260919); the old intervals had no committed script | N0.1 per-claim tests | `results/ablation_v2_contrasts.json` |
| 2026-09-25 | C1' leaf result | the 1.2% "reproduces" at leaf granularity (1.58% to 2.10%) | A labeler artifact: every one of the 808 critical leaves exists because a nested nav, menu, header or footer child is relabeled trusted | Adversarial review (N0.3) | `research/audit/2026-09-25_adversarial_C1prime_C4.md` |
| 2026-09-25 | C1' ratios | exposure is 18 to 28 times the per-node rate | Those ratios change unit and criterion at once; at a fixed criterion, node to page is 1.9x to 2.4x | Adversarial review | as above |
| 2026-09-25 | C4 and claims rows K9, K10 | task-scoped envelopes give 0.0% | The narrow envelope is the annotated target, an oracle, so 0.0% holds by construction. C4 withdrawn as stated | Adversarial review | as above |
| 2026-09-25 | Novelty ledger, C1' | "1.58% to 2.10%, below the 1.66% ceiling" | 2.10% is above 1.66% | Adversarial review | as above |
| 2026-09-25 | Unit-ladder README | per-page cap compared against the pooled 19.17% (1,086 / 5,664) | For Mind2Web the caps are 38.35% (1,086 / 2,832) for any critical path and 3.32% (94 / 2,832) for Case 3 | Adversarial review | as above |
| 2026-09-26 | Every 25 Sep experiment | "pre-registered" (local commits 78e50c7, 30178d3, a020f52, 979f808) | The cloud workspace was reset before any push, and those commits are gone; nobody can check the pre-registrations. The four experiments count as exploratory | Workspace reset, 26 Sep | `research/DECISIONS.md`, 26 Sep |
| 2026-09-26 | C7 README, reading | Booking's class names changed "between the 2023 capture and UCM's 2026 pages" | UCM records no capture date: its URLs carry a 1 Jul 2025 check-in, and its repo starts on 7 Jul 2026 | Reading UCM's `sites/booking/site.py` | `experiments/2026-09-25_C7_ucm-selectors-on-archive/README.md` |
| 2026-09-26 | C7 README, reading | "an evaluation of UCM-style masking on Mind2Web's Booking pages would mask almost nothing, so it would measure an undefended agent" | True only for an evaluation that reuses published or live-written selectors. UCM writes selectors from the page it sees; its behavior on archived pages is task 2.8 | Writing the C7c pre-registration | as above |
| 2026-09-26 | ROADMAP 2.5 | "boundary F1 on Booking, Reddit and GitLab ... (0.997, 0.879, 0.840)" | UCM Table 2: Reddit 0.997±0.003, Booking 0.879±0.020, GitLab 0.840±0.008 | Fact check against arXiv:2607.05277v1 (through an extraction model; check against the PDF) | `ROADMAP.md` |

## Known stale spots in the imported docs

These documents were imported as they stood on 24 and 25 Sep. They are not edited, so the stale values stay in them:

- `docs/context/05`, `06` and `07` quote 19.5% for page-wide influence escape. Use 43.4% (57-site) and name the frame.
- `docs/context/01` says "my sandbox" for the original 24 September environment. Capabilities here come from `scripts/preflight.py`.
- `docs/context/01` describes sending keys in chat. That procedure is replaced by environment variables (`docs/OPERATIONS.md`).
