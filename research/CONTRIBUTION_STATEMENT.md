# Contribution statement (draft for Gate N)

Status: DRAFT by Claude, 26 Sep 2026, task N0.5. Alam approves or rewrites it at Gate N (Oct 11). Nothing here is a supported claim yet. Numbers carry their claims-ledger IDs and are provisional until each row passes Gate 0.

## The paper in one paragraph

Structural defenses against prompt injection in web agents decide trust from the DOM. UCM masks untrusted regions with CSS selectors. Prismata gates each action by the ancestor chain of the element it touches. Both, and every evaluation of them, depend on which page representation the defense reads. We measure that dependence, and it is large. The archive behind Mind2Web, a widely used web-agent dataset, deletes the attributes these defenses read: no site-authored `data-*`, `href`, `on*`, `tabindex`, `style` or `hidden` survives on any of 57 sites. That deletion alone disables 93% of UCM's working Booking selectors on the same live page. We then separate the two ways a provenance error hurts under a gate: exposure and admission. Finally, we report how often agents meet actionable controls inside untrusted content, per page and per task. That is the quantity a per-node statistic hides.

## Primary contributions

Each has one sentence, its evidence, the test that would falsify it, and the tasks that complete it.

### P1. Page archives and site drift remove what structural defenses read (C7 with C8)

**Sentence.** The Mind2Web archive keeps 21 attribute names and no site-authored `data-*`, `href`, `on*`, `tabindex`, `style` or `hidden` on 57 of 57 sites (K21). On the same live Booking DOM, reducing attributes to that set disables 53 of the 57 UCM selectors that work live (K25). Selectors written for Booking also break over time: 19% to 23% on one page (C8, exploratory).

- **Audit verdict.** NOVEL AS MEASUREMENT for both C7 and C8. Online-Mind2Web and WebCanvas measure task drift, not dropped defense inputs. Wrapper breakage itself is known (Kushmerick 2000; Lerman et al. 2003).
- **Evidence now.**
  - K21, attribute census. Rerun 26 Sep, identical.
  - K22 and K23: 24 of 25 hand and 68 of 68 LLM selectors match nothing on 131 archived Booking pages.
  - K25: stripping alone, same DOM (C7c).
- **Reader who acts on it.**
  - A benchmark builder, who must say which defense inputs a corpus keeps.
  - A defense evaluator, who must not reuse selectors or actionability rules across representations.
  - The reviewer of the next paper like Prismata, who should ask which DOM the headline number came from.
- **Falsification tests.**
  - (a) C7b, pre-registered 26 Sep. If requiring an `href` for links moves Prismata-style per-node criticality by less than 20%, P1 loses its Prismata side and speaks about selector-based defenses only.
  - (b) Task 2.8. UCM's own generator may write selectors on archived Booking pages whose F1 against human labels is within 0.05 of its live F1. Then the practical damage is limited to reusing selectors, and P1 must say so in its first sentence.
  - (c) Task 2.7. If fewer than a quarter of the captured live sites carry `data-*` attributes inside the regions UCM's generator selects, Booking is an outlier. P1 then becomes a case study, not a general result.
- **Tasks that complete it.**
  - C7b ($0, needs the kit).
  - 2.7 live capture (Colab; Booking's homepage returned HTTP 403 to this sandbox).
  - 2.8 ($3 to $13).
  - 3.5 selector breakage across sites (about $11).

### P2. A provenance error harms through exposure as well as admission, and the two can be separated (C3 sub-result)

**Sentence.** In a worst-case controller bound on 159 Mind2Web pages, one wrong provenance label changes influence escape by different amounts depending on the channel. The change is 96.9 points [91.8, 100.0] when the envelope is recomputed from the wrong labels (K9). It is 33.3 points [15.0, 55.7] through exposure alone, with the admitted action set unchanged (K11). It is 0.0 points when the injection asks for a control that the fixed envelope does not admit (K8).

- **Audit verdict.** C3 is INCREMENTAL overall. Its exposure sub-result is NOVEL AS MEASUREMENT. Closest work: Prismata's confinement guarantee, and UCM Appendix E, where one mislabeled element gives 6±5% attack success with real agents.
- **Evidence now.** K8, K9 and K11, with site-bootstrap intervals from `scripts/ablation_contrasts.py`.
- **Caveats.**
  - These are upper bounds from a controller that obeys every visible, admitted instruction.
  - Only the page-wide arms stand. The narrow arms use the annotated target as the envelope, which is an oracle (C4 withdrawn as stated).
- **Reader who acts on it.** A defense designer choosing between masking (acts on exposure) and gating (acts on admission). The number says a gate alone leaves the exposure channel open under a wide envelope.
- **Falsification test.** Task 2.4, real agents, pre-registered. Suppose agents follow a visible injection in under 5% of trials in the exposure-only cell (fixed envelope, un-pruned injection). Then the channel exists in the bound only (ROADMAP stop condition 2), and P2 drops to a supporting mechanism result.
- **Tasks that complete it.**
  - 2.4 real-agent pilot ($11 to $22 with the Batch API).
  - 3.2 three model families.
  - 3.4, to learn whether a Prismata-style LLM gate chooses envelopes wide enough for the channel to matter.

### P3 (conditional). How often agents meet actionable controls inside untrusted content, per page and per task (C1')

**Sentence.** A visible actionable control sits inside ad, user or hosted content on 24% to 38% of Mind2Web pages and in 39% to 59% of tasks, depending on labeler strictness (K19; `experiments/2026-09-25_N0.3b_labeler-sensitivity/`). About 17% of pages remain once five sites whose "ads" are first-party promotions are set aside. A per-node statistic cannot show this.

- **Audit verdict.** NOVEL AS MEASUREMENT at most, and descriptive. It has had no novelty audit of its own against web-measurement studies of third-party content prevalence (adversarial review, row 12).
- **Why it is conditional.** The labeler over-labels: the 9.19% control and 7.71% target figures are mostly first-party false positives. The band itself rests on heuristic labels.
- **Falsification test.** The blind hand audit in task 1.7 (about 100 exposure-driving seeds, at most 3 per site), under a pre-registered kill rule. Keep P3 only if the audited per-task exposure has a 95% lower bound above 25%. Otherwise it becomes one paragraph of the measurement section.
- **Tasks that complete it.**
  - The C1' novelty check, before Gate N, $0.
  - 1.7 hand audit, about 3 hours of annotation.
  - 3.6 site-macro averages and leave-one-site-out.

**Recommendation.** Lead with P1. It is the only contribution with evidence that does not rest on our labeler or on a controller bound, and every task that completes it is free or under $15. Keep P2 if 2.4 clears 5%. Decide on P3 after the hand audit.

## Supporting results (in the paper, not claimed as contributions)

- **How the choice of measurement changes Prismata-style numbers.**
  - Unit: 1.6% to 19.6% across our units.
  - Whether the region root counts: 21.5 to 34.3 points (K3 to K5).
  - Oracle against target-free gate: 1.85x (K6).

  This is the methods section. It explains why we do not claim that Prismata's 1.2% fails to reproduce: its unit and labels are unknown until the authors answer (task 1.1).
- **C5**, the four-layer factorization, as method.
- **C10**, the gap between the controller bound and real agents, needed for credibility.

## Withdrawn or dropped

- **C1**, "the 1.2% is a definitional artifact". Prismata states one definition.
- **C2**, "the published gate is an oracle". The oracle was ours.
- **C4 as stated.** Its narrow envelope is the annotated target. It can return only through task 3.4 with a deployable gate and real agents.
- **C9**, criticality-conditioned verification. INCREMENTAL, with high scoop risk: SIEVE, CausalArmor.
- **E1, E2, E9** from the external review (`research/BACKLOG_IDEAS.md`).

## What the paper does not claim

- That Prismata's 1.2% is wrong. We ask the authors for their unit, representation and labels.
- That UCM fails on archives. We show that its published selectors do not survive archiving. Its generator on archived pages is task 2.8.
- Any error rate for our labeler before the hand audit. Before it, we report agreement rates only.

## Title options

1. What Structural Prompt-Injection Defenses Read: Archive Fidelity, Selector Decay and Exposure in Web-Agent Evaluation
2. Evaluating DOM-Level Trust Boundaries for Web Agents on Archived and Live Pages
3. Archived Pages Are Not Live Pages: Measuring Structural Prompt-Injection Defenses for Web Agents

## Every roadmap task, mapped

"All" means infrastructure that every contribution needs.

| Task | Feeds | Decision |
| --- | --- | --- |
| 0.1, 0.2, N0.1 to N0.6 | all | keep |
| 1.1 Prismata email | P1 (which representation and link rule), supporting (unit, labels) | keep, send first |
| 1.2 UCM email | P1 (capture date, saved HTML), Gate 1 | keep |
| 1.3 notebook 02 coupling power | C6 only | keep only if C6 survives the Oct 30 go/no-go |
| 1.4 model IDs | P2 (paid runs) | keep |
| 1.6 pre-registration | all | keep |
| 1.7 annotation guide and page | P3 (hand audit), supporting (labeler precision) | keep, refocused on exposure-driving seeds first |
| 1.8 attribute survival | P1 | done (K21) |
| 1.9 UCM self-hosted sites | Gate 1, P2 on UCM (3.3) | keep |
| 1.10 other 8 shards | C6 only | drop unless coupling goes ahead |
| 1.11 team decisions | all | keep |
| 1.12 competitor watch | all | keep |
| 1.13 notebook git retrofit | infrastructure for 2.7 | keep |
| 1.14 Colab token | P1 (2.7) | keep |
| 1.15 Batch API | P2 (cost) | keep |
| 1.16 notebook plumbing | P2 (paid runs) | keep |
| 2.1 human annotation pilot, 300 regions | supporting (labeler precision), C6 | keep at 100 exposure items first (1.7); extend to 300 only if C6 stays |
| 2.2 vendor labeling pilot | P3 (a Prismata-style LLM labeler in the sensitivity band), C6 | keep, re-scoped to the audited items |
| 2.3 Gemini arm | C6 | drop unless coupling goes ahead |
| 2.4 real-agent pilot | P2 | keep, top paid priority |
| 2.5 UCM reproduction | Gate 1, P1 (F1 baseline for 2.8) | keep |
| 2.6 UCM on WebArena GitLab | Gate 1 fallback | drop unless 2.5 fails |
| 2.7 live capture | P1, C8 | keep, top free priority |
| 2.8 UCM detector on archive vs live | P1 (falsification test b) | keep |
| 3.1 coupling study | C6 | drop unless the Oct 30 go |
| 3.2 real agents, 3 families | P2 | keep |
| 3.3 mislabel by criticality on UCM sites | P2 (two-system contrast) | keep if Gate 1 passes |
| 3.4 LLM-chosen envelope | P2 (does the channel matter in practice), C4 revival | keep |
| 3.5 UCM deployment cost and breakage | P1, C8 | keep |
| 3.6 sensitivity analyses | all | keep |
| 4.1, 4.2 mechanism (C9) | none | drop: C9 is INCREMENTAL with high scoop risk, so the TDSC route has no mechanism to rest on |
| 5.1 to 5.6, 6.1 to 6.4 | all | keep |

Dropping 1.10, 2.3, 2.6, 3.1 and 4.1 to 4.2 by default saves $2 to $7 (3.1), $45 to $120 (2.6, optional anyway) and $40 to $100 (Phase 4). It also saves up to 44 annotation hours unless coupling goes ahead.

## Gate N issue (text to open when the repo is reachable)

**Title:** Gate N: approve the contribution statement

**Body:**
- Please read `research/CONTRIBUTION_STATEMENT.md` and `research/NOVELTY_LEDGER.md`.
- Decide:
  - [ ] P1 as the lead contribution, with falsification tests (a) to (c)
  - [ ] P2, conditional on the 2.4 pilot clearing 5% in the exposure-only cell
  - [ ] P3: keep conditional on the hand audit, or move to supporting now
  - [ ] the drops in the task table (1.10, 2.3, 2.6, 3.1, 4.1, 4.2)
  - [ ] a working title
- Phase 3 spend waits for this issue to close.
