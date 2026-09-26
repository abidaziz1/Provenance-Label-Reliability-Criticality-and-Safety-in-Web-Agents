# Novelty ledger

Phase 0 decides what this paper claims. Each candidate below gets a verdict from a fresh literature search (`novelty-auditor`), survives or dies under attack (`adversarial-reviewer`), and only then can enter `research/CONTRIBUTION_STATEMENT.md`.

## The four tests

A candidate becomes a primary contribution only if it passes all four:

1. **New.** Verdict NOVEL or NOVEL AS MEASUREMENT against the closest 3 to 6 works, quoted.
2. **True.** Evidence that reruns from a commit, with a construct check, and no fatal row from the adversarial review.
3. **Needed.** A named reader changes what they do because of it: a defense designer, a benchmark builder, or a reviewer of the next paper like Prismata.
4. **Feasible.** The missing evidence comes from a task in ROADMAP.md inside the budget and before Feb 7.

## Starting hypothesis (to test, not to defend)

Written at handoff on 25 Sep 2026. The audit may overturn it.

Both published structural defenses report residual risk under assumptions they leave unstated: which reading of "critical path" is used, whether the gate knows the task target, how wide the action envelope is, and whether an archive preserves the page features the defense relies on. On real DOMs the critical-path reading moves the headline number about 40-fold and the envelope width decides between 0.0% and 96.9% effect (controller upper bounds); the oracle gate is worth about 1.8x; the archive's effect is not yet measured. The most defensible contribution is the measurement of those assumptions, with confinement width shown to matter more than label accuracy. The principle of confinement itself is 50 years old (Lampson 1973; Saltzer and Schroeder 1975), so a paper that claims a new principle will be rated KNOWN. The mechanism in Phase 4 is the only candidate for a systems contribution, and it does not exist yet.

The bar was set by the 19 Sep independent audit: the measurements must "predict or explain actual security outcomes beyond existing least-privilege reasoning" (`docs/history/Independent_Research_Audit_19Sep.md`). Every candidate below is judged against that sentence.

## Candidates

Verdicts start as UNVERIFIED. "Prior-art seeds" are leads for the auditor, not verified citations: open each one before relying on it.

### C1. The 1.2% is a definitional artifact

- **Claim.** Prismata's 1.2% residual-risk figure matches the root-to-task-target reading of "critical path" (our measurement 1.13% to 1.73%) and not the "contains an actionable descendant" reading its own Section 3 states (49.93%), a forty-fold gap on the dataset that supplies 72% of their corpus.
- **Evidence.** Measured. `docs/context/02_Reconciliation_1.2pct.md`; `results/reconcile_v2.json`; `results/descendant_only_v2.json` (57-site 49.93%, 16-site 41.58%; with the region root counted 71.43% and 75.85%); scripts `scripts/reconcile.py`, `scripts/analyse_reconcile.py`, `scripts/descendant_only.py`. `scripts/descendant_only.py` rerun from this repo on 25 Sep: byte-identical; rerunning `scripts/reconcile.py` is part of task 0.2.
- **Construct risk.** Our labeler is a class-name heuristic and theirs is an LLM. Their labels could produce spans shaped so that the loose reading gives 1.2%; at their density of 23.10 units per page that needs 98.8% leaves or text-only units.
- **What upgrades it.** The authors' answer (1.1); their labeler output on shared pages; the human labels from 2.1.
- **Prior-art seeds.** Prismata itself (arXiv:2607.08147); reproducibility-study norms in ML (for example the ML Reproducibility Challenge reports); measurement-validity work in security evaluation.
- **Likely reviewer line.** "An erratum on one paper, not a contribution." Counter only if C2, C4 and C7 show the same class of problem is general.
- **Verdict.** UNVERIFIED.

### C2. The published criticality gate is an oracle

- **Claim.** The criticality gate that yields the published residual risk ranks by distance to the task target, which a deployed defender does not know; a deployable target-free gate admits about 1.8x more critical regions and disagrees with the oracle on 7.3% of regions.
- **Evidence.** Measured. `results/gate_comparison.json`, `scripts/gate_comparison.py`, `docs/context/04_Corrected_Figures.md`.
- **Construct risk.** Our target-free gate is one design; a better deployable gate could close part of the gap. The claim must be "this oracle assumption is unstated and worth 1.8x under a reasonable deployable gate", not "every deployable gate is worse by 1.8x".
- **What upgrades it.** 3.6 with two or three deployable gate designs; 3.4 with an LLM-chosen envelope.
- **Prior-art seeds.** Oracle-assumption critiques in adversarial ML evaluation (for example Carlini et al. 2019, "On Evaluating Adversarial Robustness"); task-scoped privilege in agent defenses (Progent, arXiv:2504.11703; CaMeL, arXiv:2503.18813).
- **Verdict.** UNVERIFIED.

### C3. A label error needs a second failure to cause harm

- **Claim.** For the containment attack, with the envelope held fixed, a label error produces exposure and zero effect (0.0%, interval [0.0, 0.0], 159 paired pages, 27 sites); when the same error propagates into a page-wide envelope the effect is 96.9% [91.9, 100.0], and under a task-scoped envelope it stays 0.0%. The one single-failure path runs through exposure: under a page-wide envelope a label error raises influence escape by 33.3 points [15.3, 55.2] by making pruned external content visible.
- **Evidence.** Measured with a deterministic worst-case-compliant controller, so these are upper bounds. `docs/context/03_Corrected_Ablation_Results.md`, `results/ablation_v2.json`, `scripts/ablation_v2.py`.
- **Construct risk.** Controller, not a real agent. The 19 Sep audit found the earlier version of this arm changed the label and the gate at once; the v2 arms separate them, and the adversarial review must confirm that in the code.
- **What upgrades it.** 2.4 and 3.2 (real agents), 3.3 (the same contrast on UCM).
- **Prior-art seeds.** Defense-in-depth and fault-tree reasoning (Vesely et al., Fault Tree Handbook, NUREG-0492, 1981); CaMeL and FIDES (arXiv:2505.23643) separate data from control flow; AgentDojo (NeurIPS 2024) reports utility and attack success but not this decomposition.
- **Verdict.** UNVERIFIED.

### C4. Confinement width governs residual effect more than label accuracy

- **Claim.** Across gate widths, measured criticality moves about 107x (0.71% at K of 5 or less to 75.99% unbounded, 16-site frame), and with every label correct a page-wide envelope admits influence escape at 43.4% against 0.0% task-scoped (57-site frame). Width is the dominant parameter, and neither published system states its width.
- **Evidence.** Measured. `results/C_gate_v2.json`, `scripts/recompute_C_and_gate.py`, `results/ablation_v2.json`. The 19.5% value in older docs is the 16-site figure; 43.4% supersedes it.
- **Construct risk.** "Width" must be defined so that a reader can compute it for another system. A random gate of the same width is needed to separate width from which elements are admitted (external review item 7; added to 3.6 and the pre-registration).
- **What upgrades it.** 3.6 with the random-gate control; 3.4 (a measured operating point); 3.3 (UCM's typed channel as a narrow width).
- **Prior-art seeds.** Lampson, "A Note on the Confinement Problem", CACM 1973; Saltzer and Schroeder, "The Protection of Information in Computer Systems", 1975 (least privilege); Progent; IsolateGPT (NDSS 2025); Willison's dual LLM pattern (2023).
- **Likely reviewer line.** "Least privilege, restated." Survives only as NOVEL AS MEASUREMENT: the quantification in this defense class, plus the finding that published results depend on an unstated width.
- **Verdict.** UNVERIFIED.

### C5. A four-layer factorization of attack effect

- **Claim.** Effect factors exactly as P(effect) = P(exposed) x P(selected | exposed) x P(admitted | selected) x P(effect | admitted), each layer measurable separately, which locates where a defense fails and separates mechanism from agent behaviour.
- **Evidence.** Instrumented in `scripts/ablation_v2.py` (columns L1 to L4 in `docs/context/03`).
- **Construct risk.** A chain-rule identity is not new by itself. The value is in the instrumentation and in what it reveals (C3); on its own this rates INCREMENTAL at best.
- **Prior-art seeds.** Liu et al., "Formalizing and Benchmarking Prompt Injection Attacks and Defenses", USENIX Security 2024; WASP (arXiv:2504.18575) separates intermediate and end-to-end attack success; InjecAgent (ACL Findings 2024).
- **Verdict.** UNVERIFIED. External review items 1 and 2 (the width metric and the risk product) belong here or in C4.

### C6. Cross-vendor labelers fail on the same items

- **Claim.** Pending. Whether LLM trust labelers from different vendors make correlated errors, which decides whether ensembling labelers helps.
- **Evidence.** None yet. Pilot 2.2; confirmatory 3.1 only on a go at Oct 30. Planning uses design effect 2.68 (ICC 0.24, 8 items per site), but that ICC is heuristic-versus-LLM disagreement from the 26 Aug smoke test (95% interval 0.065 to 0.409), to be re-estimated from human labels.
- **Construct risk.** Needs human ground truth (2.1); a disagreement rate is not an error rate.
- **Prior-art seeds.** Knight and Leveson, "An experimental evaluation of the assumption of independence in multiversion programming", IEEE TSE 1986; Kim et al., "Correlated Errors in Large Language Models", ICML 2025.
- **Likely verdict.** NOVEL AS MEASUREMENT at most. Optional for the paper.
- **Verdict.** UNVERIFIED.

### C7. Web archives strip what structural defenses read

- **Claim.** Mind2Web archives strip `data-*`, `onclick`, `tabindex`, `contenteditable` and label targets: only 3 of Prismata's 7 actionability clauses ever fire on the archive (links 298,756 matches, form controls 80,531, interactive ARIA roles 23,307). Evaluations of structure-based defenses on archives therefore test a different input than deployment gives them.
- **Evidence.** Partly measured: `docs/context/02` section 2.1. `data-*` survival per site: 1.8 (all 57 sites); live comparison: 2.7 and 2.8. Hashed class names defeat the heuristic on Airbnb (zero untrusted regions over 31 observations); UCM reports the same problem on Booking.
- **Prior-art seeds.** Mind2Web (NeurIPS 2023) preprocessing description; web-archive fidelity studies (the Memento literature); WebArena.
- **Verdict.** UNVERIFIED.

### C8. Selector-based masking costs and decays

- **Claim.** Pending. How many CSS selectors UCM-style masking needs per site across 57 sites, and how many break between the 2023 archive and 2026 live pages.
- **Evidence.** None yet. Task 3.5 (about $11) after 2.7.
- **Prior-art seeds.** Wrapper maintenance in web extraction (Kushmerick, "Wrapper verification", World Wide Web, 2000); locator fragility in web testing (Leotta et al., ROBULA+, 2016). The phenomenon is known; the number for this defense class may not be.
- **Verdict.** UNVERIFIED.

### C9. Criticality-conditioned verification

- **Claim.** Pending, TDSC route only. A second labeling call on untrusted regions inside the gate-admitted set cuts residual effect at a bounded cost (about 1.2 regions per trajectory at K = 21, against 25 with no gate).
- **Evidence.** None. Tasks 4.1 and 4.2.
- **Prior-art seeds.** Task Shield (arXiv:2412.16682); MELON (ICML 2025); LlamaFirewall AlignmentCheck (arXiv:2505.03574); spotlighting (arXiv:2403.14720); model cascades and selective verification. The delta, if any, is the gate-conditioned cost bound.
- **Verdict.** UNVERIFIED. Likely INCREMENTAL unless the cost bound is new.

### C10. The gap between mechanism and behaviour

- **Claim.** Pending. How far real agents from 3 model families fall below the controller's upper bounds on the same conditions.
- **Evidence.** None yet. 2.4 (pilot) and 3.2 (confirmatory). Gate 2.
- **Prior-art seeds.** AgentDojo; WASP; EIA (ICLR 2025); pop-up attacks on computer agents (arXiv:2411.02391); Greshake et al., AISec 2023.
- **Verdict.** UNVERIFIED. Needed to make C3 and C4 credible to an ML audience, not a contribution by itself.

## Verdict table (fill in during N0.2 and N0.3)

| ID | Verdict | Closest work | Delta in one line | Fatal attack? | Upgrade task | Keep as |
| --- | --- | --- | --- | --- | --- | --- |
| C1 | UNVERIFIED | | | | 1.1, 2.1 | |
| C2 | UNVERIFIED | | | | 3.4, 3.6 | |
| C3 | UNVERIFIED | | | | 2.4, 3.2, 3.3 | |
| C4 | UNVERIFIED | | | | 3.3, 3.4, 3.6 | |
| C5 | UNVERIFIED | | | | none | |
| C6 | UNVERIFIED | | | | 2.2, 3.1 | |
| C7 | UNVERIFIED | | | | 1.8, 2.7, 2.8 | |
| C8 | UNVERIFIED | | | | 3.5 | |
| C9 | UNVERIFIED | | | | 4.1, 4.2 | |
| C10 | UNVERIFIED | | | | 2.4, 3.2 | |

"Keep as" is one of: primary contribution, supporting result, method section, discussion, drop.
