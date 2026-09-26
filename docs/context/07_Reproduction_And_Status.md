# Idea 3: Reproduction and Current Status

**Date:** 12 Sep 2026, **substantially corrected 19 Sep 2026.**

> **READ THIS FIRST.** Sections 3, 4 and 5 of the 12 Sep version were wrong and are
> replaced below. The corrections are set out in `Idea3_CORRECTIONS_19Sep2026.md`, the
> definitional resolution in `Idea3_Reconciliation_1.2pct.md`, and every moved number in
> `Idea3_Corrected_Figures.md`. Nothing from the 12 Sep §3 framing should be quoted.

Read alongside `Idea3_Smoketest_EXECUTED_Results.md` (26 Aug) and
`Idea3_Smoketest_Completeness_Audit.md` (28 Aug).

## 1. The smoke test reproduces from public data (unchanged, still true)

The full pipeline was rebuilt as a single Colab notebook
(`Prismata_Label_Reliability_Smoketest.ipynb`, 32 cells) that downloads the three
Mind2Web shards from pinned revision `17ece8eb`, reimplements the labeler, the confinement
layer, the attacks and the statistics, and prints every published figure.

Executed in Google Colab on Python 3.11.15, different hardware, fresh 1.27 GB download.
**All 37 checked values matched verbatim**, including full-precision floats:

| Quantity | Value |
|---|---|
| site ICC of labeling error | 0.23989759651217377 |
| C_eff | 6.058436102064627 |
| trajectory risk, independent | 0.27911735956780537 |
| trajectory risk, measured rho | 0.07678205177267582 |

Gate sweep reproduced exactly (14 critical at K=1 through 1,627 unbounded), and reproduced
again on 19 Sep by an independently written harness.

**This is repeatability, not validity.** The 19 Sep audit made that distinction and it was
the right one: three findings reproduced perfectly and were still wrong, because the
experiment did not measure what it claimed.

**Engineering note:** the original matcher recompiled the same ~78 regexes inside the
per-node loop, consuming >85% of wall-clock on deep DOMs. Precompiling cut a ~1 hour run to
under a minute with byte-identical output.

## 2. Prismata's text, verbatim (unchanged, still true)

arXiv:2607.08147, Villa, Ozdarendeli, Tan, Popa, posted 9 Jul 2026.

- **Composition is explicit:** `cap(e,task) = min(cap_gate(e,task), cap_biba(e,task))`
  (§2.3). The gate-width sweep measures a curve their own formula implies.
- **The Biba rule constrains labels relative to the PARENT, not the truth:** "Once an
  element's origin label is resolved, it is locked; trust labels cannot exceed their
  parent's (no-write-up)." The paper makes no assumption that the labeler is correct.
- **They concede Case 3 and defend it with a rarity claim:** injection on the critical path
  with no preceding cue, 94 of 90,408 sampled paths = 0.10% (0.017% best-practice sites).

## 3. REPLACED: the 1.2% is now explained

The 12 Sep version claimed the gap was a deployment-distribution artifact. It is not:
Prismata's corpus is 72.4% Mind2Web, the same dataset we used. That framing was retracted
on 19 Sep.

The gap is definitional and has now been located. Full working in
`Idea3_Reconciliation_1.2pct.md`; the short version:

- Their §3 sentence reports the 1.2% as untrusted paths that "contain an actionable
  descendant". Measured that way on our corpus, under their own actionable definition and
  their wording (descendants only, region root excluded), the rate is **49.93%**.
- Their §1.1 and §2.1 define the critical path as the ancestor chain to *the* element the
  task targets. Measured that way, our rate is **1.13% to 1.73%** depending on unit, which
  **brackets their 1.2%**.
- Their number is reproducible under one of the two definitions their own paper gives for
  it, and the choice between those definitions moves the residual-risk argument forty-fold.

Three candidate explanations were eliminated by measurement: the actionability definition
(0.25 points), the page sampling (moves the rate *up*, to 80.82%), and the unit granularity
(worth about six-fold, not forty).

### The superseded comparison table

The 12 Sep table quoted 77.83% regions, 79.46% no-cue and 95.27% U/H no-cue against
Prismata's 1.2%. All three rows are withdrawn:

| Row | Why withdrawn |
|---|---|
| 77.83% vs 1.2% | different definitions. Like-for-like is 49.93% vs 1.2%, with the rest explained |
| 79.46% no cue "in the labeler's input" | measured over a view with class names removed. Prismata's labeler reads class names. Retraction 2 of 19 Sep |
| 95.27% U/H no cue | same construction, same problem |
| 0% → 100% consequence | produced by a gate grant, not a label error. Retraction 3 of 19 Sep |

## 4. REPLACED: decision state

The 12 Sep version said all three proceed bars met and the kill rule refuted. That rested
on a confounded arm.

| Item | 12 Sep | 19 Sep |
|---|---|---|
| Proceed bar C ("critical error count predicts compromise, 0%→100%") | MET | **WITHDRAWN.** The arm granted the attacker's element into the envelope |
| Kill rule ("kill if confinement prevents every critical error reaching effect") | REFUTED | **NOT REFUTED.** With the gate held fixed, a label error produces 0% effect in both envelopes |
| Modify rule (C_eff 6.1 vs mean C) | PARTIAL | PARTIAL. Mean C is 26.3 on corrected figures, not 35.4 |

**What replaces the retracted claim is sharper.** An effect requires two simultaneous
failures: a wrong label **and** a gate wide enough to admit the mislabeled control. The
19 Sep ablation confirms it. With the envelope recomputed from the erroneous labels rather
than granted by hand, a page-wide envelope returns to a high effect rate and a task-scoped
one stays at zero. That contrast, derived rather than assumed, is the confinement-width
result and it is the paper's spine.

**The strongest surviving evidence needs no planted error at all:** influence escape, every
label correct, 19.5% effect under a page-wide envelope and 0% under a task-scoped one.

## 5. REPLACED: next steps

The blockers in the 12 Sep version are no longer the binding ones. Current order, from
`Idea3_CORRECTIONS_19Sep2026.md` §8 with item 0 now done:

0. ~~Reconcile the 1.2%.~~ **Done, 19 Sep.** No budget needed.
1. ~~Repair and freeze the measurement setup.~~ **Done, 19 Sep.** Six defects fixed, a
   seventh found, 33 regression assertions, every affected figure recomputed with reasons.
   Three Colab notebooks rebuilt as v2.
2. **Build independent ground truth.** Sample heuristic-negative regions and agreement
   cases, not only disagreements. Needs people, not a key. This is now the top blocker.
3. **Run the corrected gate ablation as a designed experiment**, including the
   envelope-derived arm. The 19 Sep run is the deterministic-controller version; the agent
   version is notebook 03 v2.
4. **Only then size the confirmatory study**, from measured rates. Not from 29.4%, which is
   inter-labeler disagreement and was never an error rate.

**One thing the team should ask for directly:** Prismata's labeler output on a shared page
set. It would settle the remaining caveat in the reconciliation in a single exchange.

## 6. Artifacts

- Reconciliation: `Idea3_Reconciliation_1.2pct.md`
- Corrected figures: `Idea3_Corrected_Figures.md`
- Corrections and retractions: `Idea3_CORRECTIONS_19Sep2026.md`
- Notebooks v2: `01_corpus_fidelity_and_structure_only_detection_v2.ipynb`,
  `02_cross_vendor_coupling_at_power_v2.ipynb`, `03_agent_compliance_pilot_v2.ipynb`.
  **The v1 notebooks are superseded and should be deleted, not run.**
- Reproduction notebook: `Prismata_Label_Reliability_Smoketest.ipynb` (still reproduces;
  its §3-derived framing is the part that was wrong, not its arithmetic)
- Full report (12 Sep): https://claude.ai/code/artifact/f2ef31f3-7b1a-4702-82af-62ce8f797870
  **Contains the three retracted claims. Do not circulate without the corrections doc.**
