# Novelty ledger

Phase 0 decides what this paper claims. Each candidate gets a verdict from a fresh literature search (novelty auditor), survives or dies under attack (adversarial reviewer), and only then can enter `research/CONTRIBUTION_STATEMENT.md`.

Audit reports: `research/audit/2026-09-25_C1_C2_C10.md`, `research/audit/2026-09-25_C3_C4_C5.md`, `research/audit/2026-09-25_C6_C7_C8_C9.md`. Analyses: `experiments/2026-09-25_N0.2_c1-robustness/`, `experiments/2026-09-25_N0.2_unit-ladder/`.

## The four tests

A candidate becomes a primary contribution only if it passes all four:

1. **New.** Verdict NOVEL or NOVEL AS MEASUREMENT against the closest works, quoted.
2. **True.** Evidence that reruns from a commit, with a construct check, and no fatal row from the adversarial review.
3. **Needed.** A named reader changes what they do because of it: a defense designer, a benchmark builder, or a reviewer of the next paper like Prismata.
4. **Feasible.** The missing evidence comes from a task in ROADMAP.md inside the budget and before Feb 7.

The bar set by the 19 Sep independent audit: the measurements must "predict or explain actual security outcomes beyond existing least-privilege reasoning" (`docs/history/Independent_Research_Audit_19Sep.md`).

## What the 25 Sep audit changed

1. **C1 as written is false.** Prismata states one definition, three times (§1.1, §2.2 and §3; the critical-path sentence is in §2.2, not §2.1): an untrusted path instance is critical when it has a non-hidden actionable descendant, where "that element" is every interactive element on the page, not the task target. The "task-target reading" was our hypothesis, never Prismata's text. Whether the 1.2% reproduces depends on the unit: on our pages the rate runs from 1.6% (leaves, a labeler artifact) to 19.6% (every visible untrusted node). The question is open until we have Prismata's unit and labels.
2. **C2 was about our own method.** The oracle (ranking by distance to the task target) is in our 18 Sep gate-width reconstruction, not in Prismata. Prismata's gate is `cap_gate(e) = ActionGate(path(e), task)`: task-scoped through an LLM, with no annotated target. The 1.8x is a correction to our instrument.
3. **A new candidate, C1', replaced C1** and passed its pre-registered test, but the adversarial review then reduced it to a descriptive result (below).
4. **C4 as stated rests on the same oracle.** Its task-scoped envelope is the annotated target; the adversarial review rated it fatal as stated.
5. **Prismata does define a task-scoped gate** and reports its precision against an expert, so "neither system states its envelope width" is wrong. What neither reports is the realized width or risk as a function of width.

## What 26 Sep added

1. **The workspace reset lost the 25 Sep commits before any push.** The free C7 measurements were rerun from public data and reproduce exactly (K21, K22, K23). The pre-registration commits for the 25 Sep experiments are gone, so those experiments count as exploratory.
2. **C7's confound is resolved for the stripping side (C7c).** On the same live Booking DOM, reducing attributes to the archive's 21 names disables 53 of the 57 UCM selectors that match live (93.0%; hand 11 of 13). Stripping alone suffices.
3. **A C7 claim was too broad.** Reused selectors fail on archives, but UCM writes selectors from the page it sees, so "UCM masks nothing on archives" is not shown. Task 2.8 tests UCM's generator on archived pages.
4. **First decay datapoint for C8.** On Booking's hotel page, 13 of 16 hand selectors and 46 of 60 LLM selectors that matched UCM's capture still match on 26 Sep 2026. The interval is unknown: UCM records no capture date.

## Candidates

Verdicts: NOVEL, NOVEL AS MEASUREMENT (principle known, quantification new), INCREMENTAL, KNOWN, or WITHDRAWN.

### C1'. Per page and per task, agents meet untrusted content around actionable elements far more often than a per-node statistic suggests

- **Status after adversarial review: survives only as a reduced, descriptive result.** Under stricter heuristic labels, 24% to 31% of Mind2Web pages (about 17% after excluding five sites whose "ads" are first-party promotions) and 39% to 48% of tasks have a visible control inside ad, user or hosted content. Prismata reports no per-page or per-task rate.
- **Withdrawn parts.** "The 1.2% reproduces at leaf granularity" (a labeler artifact: all 808 critical leaves exist because nested nav, menu, header or footer nodes are relabeled trusted); "the 1.2% is a per-leaf rate" (Prismata's unit is an LLM-flagged untrusted node, 23.10 per page, against our 143.55); the 18x and 28x ratios (they change unit and criterion at once; at a fixed criterion, node to page is 1.9x to 2.4x); the 9.19% element and 7.71% target rates as stated (mostly first-party false positives; stricter labels give 1.2% to 2.5% and 0.5% to 2.7%).
- **Open question it leaves.** Prismata's 1.2% ranges over 1.6% to 19.6% of our untrusted units depending on the unit, so whether it reproduces depends on the density of nodes its labeler flags. Only Prismata's labels (task 1.1) or human labels settle it.
- **Evidence.** `experiments/2026-09-25_N0.2_c1-robustness/`, `experiments/2026-09-25_N0.2_unit-ladder/`, `research/audit/2026-09-25_adversarial_C1prime_C4.md`.
- **What upgrades it.** Fix the known labeler false positives (storefront, answer, adv, UUID and page-wrapper seeds) under a pre-registered rule; a blind hand audit of about 100 exposure-driving labels; a per-page Case-3 estimate; Prismata's unit definition and per-corpus counts.
- **Verdict.** NOVEL AS MEASUREMENT at most, descriptive; not a primary contribution in its current form.

### C1. The 1.2% is a definitional artifact

- **Verdict. WITHDRAWN (25 Sep).** See "What the 25 Sep audit changed", item 1. Replaced by C1'.

### C2. The published criticality gate is an oracle

- **Verdict. WITHDRAWN as a claim about Prismata (25 Sep).** The oracle is our reconstruction's. Kept as a method correction: our 18 Sep gate-width curve used distance to the annotated target; a target-free version admits about 1.8x more critical regions (K6). Any reuse of the gate-width curve must say which gate it uses.

### C3. A label error needs a second failure to cause harm

- **Verdict.** INCREMENTAL; the exposure sub-result (+33.3 points [15.0, 55.7] from a label error that un-prunes external content under a page-wide envelope) is NOVEL AS MEASUREMENT.
- **Closest work.** Prismata's own guarantee that mislabelings are confined to elements whose critical paths contain the injection; UCM Appendix E, one mislabeled element, 6±5% attack success with real agents.
- **Damaging reviewer line.** The 0.0% cell holds by construction for a deterministic controller that cannot act outside a fixed envelope.
- **Adversarial note (25 Sep).** Its task-scoped arms use the same oracle envelope as C4 (the annotated target), so only the page-wide contrasts, including the exposure channel, stand.
- **Keep as.** Supporting result, with the exposure channel as its point.

### C4. Envelope width governs residual effect more than label accuracy

- **Verdict.** NOVEL AS MEASUREMENT (the principle is least privilege, KNOWN since Saltzer and Schroeder 1975). First width dose-response for DOM-level web-agent gates with every label correct.
- **Evidence.** With correct labels, influence escape 43.4% page-wide vs 0.0% task-scoped (controller upper bound); criticality 0.71% to 75.99% across K on our (oracle-ranked) sweep, which must be redone with a target-free or LLM-chosen gate (task 3.4).
- **Damaging reviewer line.** "Wider envelope, more worst-case harm" is a tautology for a controller that obeys every admissible injection.
- **Adversarial review (25 Sep): fatal as stated.** The task-scoped envelope in `scripts/ablation_v2.py` is the annotated target, the same oracle withdrawn for C2, so its 0.0% holds by construction (the attacker's element is never the target); the gate never decides anything (L3 equals L2 in every arm); "more than label accuracy" is not shown, since the label-error effect +33.3 [15.0, 55.7] contains the width effect 43.4. The two-point dose-response and heuristic "correct" labels also need fixing. C4 is WITHDRAWN until re-run with a deployable envelope (task 3.4) and real agents.
- **What crosses the least-privilege bar (from the audit).** Real agents with an adaptive attacker on the 159 pages, crossing envelope width x label error x whether the target lies inside the envelope; fit the layers on half the sites, pre-register held-out attack success, and beat a least-privilege-only predictor. The key cell keeps the admitted action set identical and uses a label error that only un-prunes content.

### C5. A four-layer factorization of attack effect

- **Verdict.** INCREMENTAL. The product is the chain rule; WASP (intermediate vs end-to-end), RedTeamCUA (attempt rate vs success) and ARE already stage attacks. Keep as method.
- **External review items.** The Confinement Width metric is INCREMENTAL (Manadhata and Wing's attack-surface metric, restricted to the admitted envelope). Risk = LabelError x GateWidth x ActionImpact is KNOWN (NIST SP 800-30) and our data contradict it: it predicts zero risk at zero label error, and we measure 43.4%.

### C6. Cross-vendor labelers fail on the same items

- **Verdict.** NOVEL AS MEASUREMENT, close to INCREMENTAL. Kohli (arXiv:2605.29800, May 2026) finds 9 LLM judges from 7 families give about 2 independent votes; Kim et al. (ICML 2025) on correlated errors. New only for untrusted-marked-trusted errors on DOM regions. 300 regions may give too few joint errors (the Oct 30 go/no-go decides).

### C7. Web archives change what structural defenses read

- **Evidence (25 Sep, free).** The Mind2Web archive keeps 21 attribute names and no site-authored `data-*`, `href`, `on*`, `tabindex`, `style` or `hidden` on 57 of 57 sites (`experiments/2026-09-25_1.8_attr-survival/`). UCM's own Booking selectors: 92% of hand and 96% of LLM selectors use a `data-*` attribute; 24 of 25 hand and 68 of 68 LLM selectors that match on UCM's captures match nothing on 131 archived Booking pages (`experiments/2026-09-25_C7_ucm-selectors-on-archive/`).
- **Stripping versus drift (26 Sep, C7c, free).** On the same live DOM, the archive's attribute whitelist disables 53 of the 57 UCM Booking selectors that work live (hand 11 of 13, LLM 42 of 44). The four survivors rest on classes or `aria-label`. `experiments/2026-09-26_C7c_live-strip-vs-drift/`.
- **Limit.** This shows that selectors do not survive archiving. It does not show that UCM fails on archives, because UCM regenerates selectors from the page it sees (task 2.8). UCM's paper, as extracted on 26 Sep (check against the PDF), discusses neither archives nor selector stability, and names non-semantic class names as the reason Booking scores lowest (F1 0.879, §7.2).
- **The Prismata side (26 Sep, C7b, pre-registered).** Prismata's §3 actionability list names links, onclick handlers, editable regions and tabindex; the archive removes `href`, `onclick`, `contenteditable` and `tabindex` everywhere. Requiring an `href` for a link cuts Prismata-style criticality per visible untrusted node from 19.57% to 9.40% (ratio 0.48, exploratory site interval [0.32, 0.64]); trusting the stored `is_clickable` flag restores 20.57%. It does not explain the 1.2% alone: 9.40% is still about 8 times the published figure (K26, `experiments/2026-09-26_C7b_actionability-on-archive/`).
- **Verdict.** NOVEL AS MEASUREMENT. Online-Mind2Web and WebCanvas measure task drift, not dropped defense inputs. Prismata's own 1.2% is computed on archived Common Crawl and Mind2Web pages. Note from 25 Sep: the archive strips `onclick` but keeps a browser-computed `is_clickable` flag and rendered bounding boxes; adding `is_clickable` changes our rates by at most 0.2 points.

### C8. Selector-based masking costs and decays

- **First signal (25 Sep, free).** All 23 hashed class tokens in UCM's Booking selectors occur 0 times in the 2023 Booking archive; confounded with archive stripping for Booking. The live half needs 2.7 and 3.5.
- **Live datapoint (26 Sep, exploratory).** 16 of those 23 tokens occur on today's Booking pages. On the hotel page, 3 of 16 hand selectors and 14 of 60 LLM selectors that matched UCM's capture no longer match (19% to 23%), over an interval UCM does not record. One site, one page; the homepage capture was blocked (HTTP 403).
- **Verdict.** NOVEL AS MEASUREMENT; breakage itself is KNOWN (Kushmerick 2000; Lerman et al. 2003; Hammoudi et al. 2016; EasyList studies). A broken masking selector unmasks untrusted content, and UCM also generates selectors with an LLM, so decay must cover both. Task 3.5.

### C9. Criticality-conditioned verification

- **Verdict.** INCREMENTAL, high scoop risk: SIEVE (arXiv:2512.06716) and CausalArmor (arXiv:2602.07918) publish the mechanism. Only the trigger is new. Candidate for merging into C6 (pick the second labeler by measured coupling). Phase 4 should not rest on it.

### C10. The gap between mechanism bounds and real agents

- **Verdict.** INCREMENTAL. WASP's "security by incompetence" (2025) names the phenomenon. Becomes NOVEL AS MEASUREMENT only if the gap changes a conclusion, for example if the ranking of the two defenses flips between the bound and real agents.

## Verdict table

| ID | Verdict | Closest work | Delta in one line | Keep as |
| --- | --- | --- | --- | --- |
| C1' | descriptive only, after adversarial review | Prismata §3 | 17% to 31% of pages and 39% to 48% of tasks expose a visible control inside untrusted content (stricter heuristic labels) | P3 in the draft statement, conditional on its own novelty check and the 1.7 hand audit |
| C1 | WITHDRAWN | Prismata §1.1, §2.2, §3 | Prismata states one definition; whether 1.2% reproduces depends on its unit (1.6% to 19.6% on our units) | drop; ask the authors (1.1) |
| C2 | WITHDRAWN (about Prismata) | Prismata §2.2 | The oracle was ours | method correction |
| C3 | INCREMENTAL (exposure sub-result NOVEL AS MEASUREMENT) | Prismata's guarantee; UCM App. E | Exposure is the only single-failure channel | exposure sub-result is P2 in the draft statement, conditional on task 2.4 |
| C4 | WITHDRAWN as stated (oracle envelope) | Saltzer and Schroeder 1975; Progent | Needs a deployable envelope and real agents | re-test in 3.4 and 3.2 |
| C5 | INCREMENTAL | WASP; RedTeamCUA | Adds exposure and admission layers | method section |
| C6 | NOVEL AS MEASUREMENT (near INCREMENTAL) | Kohli 2026; Kim et al. 2025 | Joint untrusted-as-trusted errors on DOM regions | optional, on a go |
| C7 | NOVEL AS MEASUREMENT, measured | Online-Mind2Web; WebCanvas | 24 of 25 UCM Booking selectors match nothing on the archive; stripping alone disables 53 of 57 on the same live DOM | primary contribution P1 (draft statement) |
| C8 | NOVEL AS MEASUREMENT, first datapoint | Lerman et al. 2003; Kushmerick 2000 | Selector decay unmasks untrusted content; 19% to 23% on one Booking page | part of P1 (3.5) |
| C9 | INCREMENTAL | SIEVE; CausalArmor | Only the trigger is new | drop or merge into C6 |
| C10 | INCREMENTAL | WASP | Bound vs real per defense | needed for credibility, not a contribution |

