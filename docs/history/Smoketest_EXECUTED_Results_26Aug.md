# Idea 3 Smoke Test: EXECUTED Results

**Date:** 26 Aug 2026
**Corpus:** Mind2Web real DOMs — 48 trajectories, 341 observations, 16 sites, 972,737 nodes
**Verdict:** PROCEED, with a reframing. All 3 proceed bars met, kill rule REFUTED.
**Full report:** https://claude.ai/code/artifact/bd38ccda-7765-4923-8b54-28eb5dec5c29

## Headline result

The original thesis (aggregate F1 misleads because errors compound) survives but is the
smaller half. The sharper finding is that **the two attack classes have different binding
constraints, and only one of them is about labels at all.**

| Attack class | Correct labels | One critical false-trust error | Binding constraint |
|---|---|---|---|
| Containment (attacker plants a control inside untrusted content) | **0%** effect | **100%** effect | label accuracy |
| Influence escape, narrow task-scoped envelope | 0% | **0%** | envelope width |
| Influence escape, permissive page-wide envelope | **19.5%** | 70.7% | envelope width |

Containment is label-bound with zero tolerance. Influence escape is envelope-bound: a
correct label does not prevent it, and a narrow envelope prevents it without correct labels.
A defense reporting only labeling metrics is silent on the second class.

## Findings

- **F1** Prismata's "1.2% of untrusted content on critical paths" does not reproduce:
  **35.17%** at node granularity, 77.8% at region granularity. Excluding ads still leaves
  71.45% of 1,478 U/H regions. Sampling difference — Common Crawl is low-interaction,
  e-commerce/travel is where agents deploy. [Measured]
- **F2** The structural-cue argument is computed over signals the labeler cannot see.
  **79.5%** of critical regions carry no explicit cue in the accessibility-tree view.
  Not proof a model can't infer from layout; is proof the claim and the labeler read
  different documents. [Measured]
- **F3** **Airbnb yields ZERO untrusted regions across 31 observations** despite being a pure
  hosted-party marketplace. Cause verified: hashed CSS (`l1j9v1wn`, `_1jndx64e`) vs Amazon's
  `product-image`. A *deterministic* whole-site failure — strongest possible form of the
  common-cause hypothesis. [Measured]
- **F4** C is large and heavy-tailed: mean 35.4, median 13.5, p90 114, max 227 per trajectory.
  Compounding is live. Also: C is 35.4 or 77.8% depending on region vs node granularity, so
  `(1−ε)^m` is undefined until m's unit is pinned. [Measured]
- **F5** Element precision understates trajectory risk by **26.6pp** (1.31% → 27.9%) for
  GPT-5.4-nano; 42.9pp for Gemini, 46.9pp for mini. [Derived]
- **F6** **Correlation moves the estimate the opposite way to the usual intuition.** For
  P(≥1 error) clustering *reduces* it: 27.9% → 7.7% at measured ρ. Independence gets it wrong
  in both directions — overstates how many trajectories are touched, understates severity of
  the touched ones. Beta-binomial verified vs 400k-draw Monte Carlo to 0.0007. [Derived]
- **F7** Label disagreement is site-determined. **ICC 0.240, bootstrap 95% CI [0.065, 0.409]**
  (B=4,000, excludes zero). Airbnb 80% / eventbrite 75% vs 0% at cvs, kohls, ticketcenter,
  agoda, uniqlo. Convergent: no-cue regions err 29.4% vs 9.1% with cue (Fisher OR 0.241,
  **p=0.061** — suggestive, not significant at n=131). [Measured]
- **F8** Kill rule REFUTED. Single critical error → 100% protected effect, no graceful
  degradation. [Measured]
- **F9** Prismata keeps task-relevant user content **read-only, not pruned** ("reviews for a
  purchasing task ... observe but not interact"). Injection reaches the agent's context with a
  *perfectly correct label*. The containment argument covers elements inside the subtree, not
  the injection's influence escaping it. [Measured + Literature]
- **F10** Two instrumentation bugs caught, in the spirit of Idea 2's F8:
  (a) Mind2Web stores third-party frame content as **escaped markup inside text nodes** —
  naive parsing counts `<div ...>` as visible text and misses every interactive element inside
  an ad frame. Fix recovers +2.1% nodes, +1.2% interactive, concentrated in exactly the
  untrusted regions the study is about.
  (b) First influence-escape run scored 35.3% using substring matching that fired on
  `Confirm My Choices` (cookie banner) and `Skip Navigation`. Whole-phrase matching on
  genuinely consequential controls gives the honest 19.5%. [Measured]
- **F11** Citation correction: Prismata Fig. 8 gives GPT-5.4-nano **P=98.69 / R=82.69 /
  F1≈90.7**; the 95.14 F1 is Gemini 3 Flash. Validation is **20 observations, 5 WebArena
  sites, 1 annotator each, ~20h**. Any claim on "95% F1" must name the model and the n. [Literature]

## Against predeclared criteria

| Rule | Status |
|---|---|
| Proceed if trajectory failure differs from prediction by ≥10pp | **MET** — 26.6pp |
| Proceed if correlation materially shifts prediction | **MET** — 20.2pp |
| Proceed if critical-error count predicts compromise | **MET** — 0% → 100%, deterministic |
| Kill if confinement prevents every critical error reaching an effect | **REFUTED** |
| Modify if C_eff near 1 (errors almost entirely common-cause) | **PARTIAL** — C_eff 6.1 vs mean C 35.4, a 6× reduction not a collapse |

## The TWO remaining gaps and exactly what closes them

1. **Cross-vendor labeler independence — needs the OpenAI key you chose.** The measured
   ICC 0.240 is *within one labeler across sites*. Whether errors correlate *between vendors*
   is unmeasured and load-bearing: if two independent labelers fail on the same regions,
   ensembling does not help. ~300 calls, a few cents. GPT-5.4-nano and mini are two of the
   three models in Prismata Fig. 8, so it replicates against their panel. Secondary reason:
   the Claude labeler used here is **not independent of the experimenter** — I wrote the
   ground-truth rules.
2. **Ground truth validity — your 40-item sheet is with you.** The 29.4% raw false-trust rate
   is disagreement between two fallible labelers, **not error against gold truth**, and should
   not be quoted as an error rate until adjudicated. The confusion matrix suggests the
   structural oracle is often the wrong one (15 D→H cases are Amazon marketplace listings,
   Eventbrite organiser events — the model is probably right). Sheet is stratified 22
   disagreements + 18 agreements, reweighted, so it stays unbiased.

## Limitations that do not block proceeding

- Agent compliance assumed, not measured — the controller always follows a visible injection,
  so selection rates are upper bounds. Gate and effect columns are mechanism facts and do not
  depend on this. Same key closes it.
- Mind2Web is 2023-vintage, US-centric, 16 of 57 sites used. C is heavy-tailed enough that
  site selection moves the mean.
- Envelope models bracket rather than reproduce Prismata; the real envelope is an LLM decision
  somewhere between narrow and page-wide. **That spread (0% vs 19.5%) is the largest single
  lever found.**
- WebArena not used — needs self-hosted environments beyond budget.

## Prior-art boundary

**"Confidently Wrong: Severity-Aware Calibration of Prompt-Injection Detectors under Attack
Shift"** (arXiv:2606.22659, Md Anas Biswas) already shows injection-detector errors clustering
by attack family **across two vendors and a fourfold size range**, and ties missed detections
to end-to-end exploit success. That pre-empts part of the correlation claim *for detectors*.
Surviving novelty for Idea 3: provenance/permission labelers rather than injection detectors,
the trajectory-level opportunity count C, and the causal link through mechanical confinement.
Prismata (arXiv:2607.08147) verified independently — unlike AID-Guard in the Idea 2 test, it
resolves on first fetch. No code or data released, hence the reimplementation.

## What the paper should now claim

*Label quality and capability scoping defend disjoint attack classes, and evaluating either
one alone misrepresents the guarantee.* Three consequences:

1. Report criticality-conditioned false-trust rate at a stated granularity, not aggregate F1.
2. Report correlation structure, not just the rate — independence is wrong in both directions.
3. Evaluate the envelope alongside the labeler.

## Next steps

1. Second labeler → cross-vendor ICC on the same 131 items. Blocked on key.
2. Adjudicate ground truth, publish inter-rater agreement, reweight the false-trust rate.
3. Scale C to all 57 sites; report the distribution, not the mean — p90=114 should drive the risk model.
4. Measure where a real task-scoped labeler lands in the 0%–19.5% envelope spread. Paper-sized on its own.
5. Audit "Confidently Wrong" in full before committing to the correlation claim.
