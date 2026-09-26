# Idea 3: plan to land the paper in a strong journal

**Date:** 18 Sep 2026, **corrected 19 Sep 2026, partly superseded 24 Sep 2026.**
**Target:** TMLR primary, IEEE TDSC stretch, ACM DTRAP floor (changed 24 Sep; see `Idea3_Submission_Roadmap.md`). The 19 Sep target in §9 was DTRAP primary.
**Build window:** 5 months, submission target late February 2027
**Team:** 2, not 6. See §7.
**Verdict:** Submit, but not the paper we have been describing. The framing must change,
and it changed twice: once on 18 Sep for the right reason, once on 19 Sep because three
findings were withdrawn.

> **SUPERSEDED IN PART, 24 Sep 2026.** `Idea3_Submission_Roadmap.md` and its living Claude
> Doc now own the task list, dates, gates, budget and venue. They replace §8 (sequencing),
> §9 (venue) and §11 (this week) below. The venue moved to TMLR primary after a precedent
> check: DTRAP and TOPS each published no LLM or agent security paper in the audit year,
> while TMLR reviews for correctness and has agent-security precedent. The framing,
> evidence, workstreams and claim in this plan still stand.

> **CORRECTION HEADER, 19 Sep 2026.** An independent audit withdrew three findings this
> plan cited as evidence. Read `Idea3_CORRECTIONS_19Sep2026.md`,
> `Idea3_Reconciliation_1.2pct.md` and `Idea3_Corrected_Figures.md` before quoting any
> number here. The changes are marked inline. The plan's *structure* survives intact; its
> evidence list is smaller and, in one place, points the opposite way.

---

## 1. Short answer

Yes, this is publishable in a good journal. No, not as "Prismata's numbers do not
reproduce." That version is a single-system critique of a reimplementation, it is the
weakest paper available from this evidence, and as of 19 Sep it is also **factually wrong**:
their number does reproduce, under one of the two definitions their own paper gives for it.

The publishable paper is a comparative measurement across the structural-labeling approach,
on the distribution where web agents get deployed, with two methodological results at its
core: **confinement width** determines outcomes more than label accuracy, and **the
definition of "critical path" moves the residual-risk argument by forty-fold**.

## 2. What changed in September

Two things, a week apart.

**18 Sep: a second system exists, and it ships code.** Untrusted Content Masking (UCM),
arXiv:2607.05277, Nikolić, Zverev, Rando, Jagielski, Debenedetti, Tramèr, 6 July 2026.
Same structural bet as Prismata: the DOM encodes enough to separate trusted from untrusted
without reading content. **MIT-licensed and public** at
`github.com/ethz-spylab/untrusted-content-masking`.

| UCM reports | Value | Bearing on this work |
|---|---|---|
| Boundary F1, Reddit | 0.997 ± 0.003 | Easy case |
| Boundary F1, Booking | 0.879 ± 0.020 | They name **non-semantic class names** as the reason. Independent corroboration of our F3 |
| Boundary F1, GitLab | 0.840 ± 0.008 | Far below Prismata's 98.69% precision claim |
| Undermasking | 0.0% to 8.5% | Site-dependent, consistent with our clustering result |
| Deployment cost | 15 to 30 hand-written CSS selectors per site | Nobody has measured how this scales or rots |
| Mislabeling sensitivity (App. E) | one mislabel, GitLab only, WASP only: ASR 6 ± 5% vs undefended 17 ± 8% | "A single mislabel collapses UCM's safety margin to roughly the heuristic defense regime, not to the undefended one" |
| Corpus | 10 self-built sites + 41 GitLab templates | Not the deployment distribution |
| Critical fraction of untrusted regions | not measured | **Unoccupied** |
| Dependence on action-set width | not measured | **Unoccupied** |
| Error clustering by site | not measured | **Unoccupied** |

**Do not overstate the disagreement.** UCM constrains the channel as well as the label: its
Quarantined Model returns only bool, int, float, enum or date, so a mislabeled region cannot
propagate free-form instructions. Prismata keeps task-relevant untrusted content read-only
but textual. Two systems, two confinement widths. That contrast is the paper.

**19 Sep: an independent audit withdrew three of our findings.** The deployment-distribution
explanation for the 1.2% gap (Prismata's corpus is 72.4% Mind2Web, the same dataset we
used); the "labeler cannot see the cue" framing (their labeler reads class names; ours was
measured on a view without them); and the single-label-error result (the arm granted the
attacker's element into the envelope, so the 0%→100% came from the gate, not the label).
Six code defects were confirmed and a seventh found. All are now fixed and every affected
figure recomputed.

## 3. Where the work actually stands

Solid, and worth protecting:

- 145 trajectories, 1,163 observations, **57 sites**, 2,460,488 nodes, reproducing from a
  pinned public dataset revision on independent hardware. 37 of 37 values matched verbatim
  in the Colab run, including full-precision floats. Re-reproduced 19 Sep by an
  independently written harness.
- **The definitional reconciliation (new, 19 Sep).** Prismata's 1.2% is computed under one
  definition of "critical path" and described under another; the two differ forty-fold on
  the dataset supplying 72% of their corpus. This is now the paper's cleanest single
  contribution, it cost nothing, and it is not rebuttable by email because it is derived
  from their own two sentences.
- The gate-width sweep. Criticality moves ~107x (0.71% to 75.99% corrected, 0.67% to 77.44%
  as published) as a function of the action gate, on real DOMs, derived from Prismata's own
  `cap = min(cap_gate, cap_biba)`. Neither published system states its gate assumption.
  **Added 19 Sep:** the published gate is *oracle-informed* (it ranks by distance to the
  task target, which a defender does not have). A deployable target-free gate admits ~1.8x
  more critical regions and disagrees with the oracle on 7.3%. Report both.
- The four-layer attack decomposition across 984 trials, separating exposure, selection,
  gate admission and effect. Better instrumentation than either paper's robustness check.
- **Influence escape, which needs no planted label error at all:** 19.5% effect under a
  page-wide envelope with every label correct, 0% under a task-scoped one. This is now the
  strongest surviving evidence for the confinement-width thesis.
- Airbnb returning zero untrusted regions across 31 observations because of hashed CSS. UCM
  independently hit the same wall on Booking. The sharpest case is rentalcars at a 0.126
  semantic class ratio, not Airbnb.
- Mind2Web strips `data-*` (0.44 to 1.37 per 1k nodes against 1,469 to 5,925 class
  attributes, one surviving name), which invalidates a naive UCM head-to-head on the archive
  and is itself a reportable corpus-fidelity result.
- Seven instrumentation defects caught and fixed, most of them moving numbers against the
  hypothesis.

**WITHDRAWN from this list (was in the 18 Sep version):**

| Claim | Status |
|---|---|
| "77.83% of untrusted regions contain an actionable element against Prismata's 1.2%" | superseded. Like-for-like is **49.93% vs 1.2%**, and the remainder is explained by the critical-path definition |
| "79.46% of critical regions carry no cue in the labeler's input" | withdrawn. Measured on a view with class names removed; their labeler reads class names |
| "95.27% for user and hosted content once ads are excluded" | withdrawn, same construction |
| "0% to 100% on one label error" | withdrawn. Produced by a gate grant. With the gate held fixed, a label error yields 0% effect in both envelopes |

Missing, ordered by how badly each kills the submission:

| Gap | Consequence if unfixed |
|---|---|
| No real agent anywhere in our evidence | Fatal. UCM ran real Claude and GPT-5.4 agents. Notebook 03 v2 is built and unblocked |
| Only one defense exercised, and it is our reimplementation | Fatal for a generality claim. UCM's public code removes the excuse |
| No mechanism or protocol contribution | Hits TDSC's avoid line directly |
| Ground truth is rules written by the experimenter | **Now the top blocker.** Every disagreement number is inter-labeler, not error |
| No modern corpus | The 2023-vintage criticism lands. 57 sites is done; live capture is not |
| Coupling is unmeasured and the pilot could not have seen it | Only fatal if the paper is built on ranking inversions. See §5 |
| No disclosure record with either author group | Security venues ask every time. **The reconciliation makes this urgent:** asking Prismata which definition produced the 1.2% is both courteous and the fastest route to certainty |
| Envelope width bracketed, not measured | Still the largest lever in the study |

## 4. Reviewer kill test

The strongest single rejection available against the paper **as it stands today**.

| Venue | Strongest rejection |
|---|---|
| ACM TOPS | An evaluation of one reimplemented system on one corpus with a simulated agent. The definitional finding is a good note, not a paper |
| IEEE TDSC | No dependability mechanism. Its avoid line names this case explicitly |
| USENIX Security | You never ran either real system. UCM's code has been public since July |
| IEEE S&P | The always-compliant controller assumes the result |
| NDSS | Mind2Web is 2023-vintage static HTML |
| IEEE TIFS | No forensics, signal or privacy core |
| TMLR | No learning contribution |
| **any** | **Added 19 Sep:** "Three of your findings were withdrawn after an internal audit six months before submission. Why should we trust the rest?" The answer must be a frozen, tested, version-controlled measurement setup and a corrections record shipped with the artifact. Both now exist |

## 5. The three candidate papers

**Paper A, dead: "Prismata does not reproduce."** Now also false. Do not build this.

**Paper B, do not build on it: the ranking-inversion paper.** Needs differential criticality
coupling of ~2.67x. The 131-item pilot had 98% power at 3x, 43% at 2x, 14% at 1.5x, and all
three proxies came back null with one pointing the wrong way. **Corrected 19 Sep:** the
pilot's power was computed from a 29.4% *disagreement* rate. At a 5% false-trust base rate
its power was about 15%, not 80%, so the null was uninformative. Demote to one honest
section.

**Paper C, build this: confinement width as the identifying variable, with the definitional
result as the opening move.**

Claim: for this family of defenses, injection safety is determined by how narrowly the
agent's action and output channel is constrained, not by how accurately page content is
labeled, and no published evaluation reports the quantity that decides it — in part because
the field does not agree on what the quantity is.

Evidence in hand:
- the definitional reconciliation (forty-fold, from their own text, costs nothing);
- the gate-width curve, in both oracle and deployable forms;
- influence escape at 19.5% vs 0% with every label correct;
- **the corrected ablation:** a label error alone produces exposure and nothing else; an
  effect requires the error *and* a gate that admits the mislabeled control. With the
  envelope recomputed from the erroneous labels, a page-wide envelope returns to a high
  effect rate and a task-scoped one stays at zero.

Evidence available from UCM: a system with materially worse labeling F1 (0.840) that
degrades to 6% rather than collapsing, because its channel is type-constrained.

The corrected version of this claim is **stronger** than the withdrawn one. "One error
breaks it" is a fragility claim that invites "then fix the labeler". "An error is harmless
until the gate is wide" is an architectural claim that the labeler cannot answer.

## 6. The four workstreams

### WS1. Run the real systems (1 engineer, highest priority, unblocked today)

1. Clone UCM, reproduce their reported numbers on their own benchmark first. If that fails,
   stop and resolve it before anything else.
2. Run **their** boundary detector on **our** 57-site corpus. **Constraint found in
   pre-work:** Mind2Web strips `data-*`, which is the signal their prompts lean on, so the
   archive handicaps them and any poor F1 would be an artifact. Notebook 01 v2 measures this
   and gates the comparison on it. A live-page corpus is required for a fair head-to-head.
3. Re-run their mislabeling sensitivity with mislabels placed **by criticality**, on both
   corpora, and with the envelope treated as a separate factor rather than folded into the
   label. Their n=1 becomes our n in the hundreds.
4. Keep the Prismata reimplementation as the second data point, labeled a reimplementation
   in every table.

Deliverable: one harness running both defenses over both corpora emitting the same
four-layer record. This harness is the artifact contribution.

### WS2. Real agents in the loop (1 engineer)

Notebook 03 v2 is the pilot. Four policy arms with the label error and the gate separated,
paired injection-free controls, one truncation point, seeded site order, and the
deterministic controller run on identical trials so the mechanism-to-behaviour gap is
measured rather than quoted. Three model families for the headline conditions.

### WS3. Corpus, sampling frame and ground truth (shared)

57 sites is done. Still needed: one modern corpus, the C distribution rather than the mean
(p90 is 72 against a mean of 26.3 on corrected figures), and a pre-registered site selection.

**Promoted to top blocker, 19 Sep:** independent human ground truth, sampling
heuristic-negative regions and agreement cases, not only disagreements. Until this exists,
every labeling number in the paper is inter-labeler agreement.

Also in scope: measure UCM's deployment cost. 15 to 30 hand-written selectors per site,
across 57 sites, and how fast they rot across redesigns.

### WS4. Mechanism (1 engineer, the part that clears TDSC)

Criticality-conditioned verification: compute the gate-admitted set first, then spend a
second labeling call only on untrusted regions inside it. On the corrected corpus that is
about 1.1 regions per trajectory at a task-scoped gate against 26.3 unbounded, so the budget
is small and bounded. Evaluate on coverage, added latency, false-block rate and residual
effect rate.

State the boundary honestly: this reduces exposure for the containment class and does
nothing for influence escape, which only the envelope controls.

## 7. The resource conflict

Idea 2 has 6 engineers committed for 7 months to TDSC with an April 2027 submission, and its
critical path runs through credential acquisition that cannot be compressed. Idea 3 cannot
have those people.

1. **Two engineers, five months, in parallel.** Feasible: no credentials, no sandbox
   accounts, no vendor negotiation. Recommended.
2. Sequence after Idea 2 submits. Costs six months in a fast-moving area where a competing
   group has the code and the motive.
3. Cut to the measurement alone and target DTRAP. Lower ceiling, lower effort.

Do not send both papers to TDSC concurrently.

## 8. Sequencing and gates

> **Superseded 24 Sep** by the phase tables and gates in `Idea3_Submission_Roadmap.md`
> (Gate 1 on 8 Nov 2026, Gate 2 on 6 Dec 2026, TMLR submission 19 Feb 2027). Kept for history.

| Month | Work | Milestone |
|---|---|---|
| 0 | ~~Reconcile the 1.2%; repair the measurement setup~~ **done 19 Sep** | Definitional result in hand |
| 1 | WS1 steps 1–2; disclosure emails out; corpus pre-registration; human ground truth pilot | **Gate 1** |
| 2 | WS1 steps 3–4; WS3 live corpus | Cross-system numbers on both corpora |
| 3 | WS2 agent runs, 3 model families | **Gate 2** |
| 4 | WS4 mechanism build and evaluation | Mechanism measured |
| 5 | Writing, artifact packaging, internal adversarial review, dated re-run | Submit |

**Gate 1, end of month 1.** UCM's own numbers reproduce from their code on their benchmark.
If not, the comparative framing is unsafe and the ceiling drops.

**Gate 2, end of month 3.** Real agents show a measurably different effect rate from the
always-compliant controller, reported whichever way it goes.

**Gate 3, continuous.** Weekly arXiv watch on both author groups. If either publishes the
deployment-distribution measurement first, repackage as reproduction plus mechanism.

**Gate 0, added 19 Sep, standing.** No finding enters the paper without a regression test
and a named construct-validity check. Three findings were withdrawn because reproduction
discipline was mistaken for validity. `fix/test_counterexamples.py` is the start of that
suite.

## 9. Venue

> **Superseded 24 Sep.** Current route: TMLR primary, IEEE TDSC stretch (only if the
> mechanism lands), ACM DTRAP floor. Reason: the venue audit's precedent count shows DTRAP
> and ACM TOPS each published no LLM or agent security paper in the audit year, while TMLR
> accepts on evidence and reader value rather than novelty, charges no fees, and has
> agent-security precedent. Details in `Idea3_Submission_Roadmap.md`. The table below is the
> 19 Sep version, kept for history.

**Changed 19 Sep.** The audit's DTRAP-first recommendation is better calibrated than the
18 Sep TOPS-first one, given what happened to three findings. Measurement with operational
relevance and a corrections record is a DTRAP paper. Promote to TOPS only if WS1 and WS2
both land.

| Venue | Grade | Fit |
|---|---|---|
| **ACM DTRAP** | B+ | **Primary.** Measurement with operational relevance is its stated best-for |
| **ACM TOPS** | A | **Secondary.** Empirical security of LLM systems with generalizable insight. Needs WS1 and WS2 |
| **IEEE TDSC** | A+ | Only if WS4 lands. Its avoid line names "an LLM benchmark with no dependable or secure-systems contribution". Also collides with Idea 2 |
| USENIX Security / NDSS | conference | Best fit by shape if a conference deadline is acceptable |
| Computers & Security | excluded | Never. Its author guide excludes security of AI/ML systems outright |

**Corrected 19 Sep:** the "100% ACM waiver" claim in the 18 Sep version is unverified and is
withdrawn until someone checks current policy directly. The venue data behind this table is
a 10 July 2026 snapshot; verify scope and fees at submission.

## 10. Proposed claim and title

Working title: *Confinement Width, Not Label Accuracy: Re-evaluating Structural Trust
Boundaries for Web Agents on the Deployment Distribution*

Alternative, now viable on its own: *What Counts as a Critical Path? A Definitional Audit of
Residual Risk in Structural Trust Boundaries*

Claim, written to what the evidence supports after the gates pass:

> Structural trust-boundary defenses for web agents report per-element labeling quality and
> aggregate attack success, and neither quantity identifies the safety of a task. We show
> first that the field's central residual-risk statistic is definitionally unstable: the same
> published number is computed under one definition of "critical path" and described under
> another, and on the dataset supplying 72% of that corpus the two readings differ by
> forty-fold. We then measure two published systems across N sites drawn from the deployment
> distribution, and find that the fraction of untrusted content that is security-relevant is
> not a constant but a function of the agent's action gate, moving two orders of magnitude
> across the gate widths the two systems implicitly assume. Labeling quality degrades from F1
> 0.99 to F1 X on commercial sites, and the degradation clusters by site. A single label
> error produces exposure and no effect while the gate is held fixed; an effect requires the
> error and a gate wide enough to admit the mislabeled control, and the two systems differ
> in exactly that width. We give a criticality-conditioned verification pass that spends a
> bounded second labeling budget only inside the gate-admitted set.

Do not claim either system is broken, that our reimplementation is the system, that 29.4% is
an error rate before adjudication, that ranking inversions occur, or that a single label
error defeats confinement.

## 11. This week

> **Superseded 24 Sep** by Phase 1 of `Idea3_Submission_Roadmap.md` (tasks 1.1 to 1.12,
> Sep 28 to Oct 11). Kept for history.

1. **Email Prismata's authors and ask which definition produced the 1.2%.** This is now the
   single highest-value message in the project. It is courteous, it is the fastest route to
   certainty, and their answer is load-bearing either way.
2. Email UCM's authors to say we are evaluating their public artifact on a different corpus.
3. Clone UCM and reproduce one of its reported numbers. A day of effort, everything in §6
   depends on it.
4. Start the human ground-truth pilot. It is the top blocker and it needs people, not a key.
5. Pre-register the 57-site selection and the criticality definition — **including whether
   the region root counts as an actionable descendant**, which is worth 21.5 to 34.3 points.
6. Decide the team question in §7.
7. Set the weekly arXiv watch on both groups and on the WASP and WebArena citation graphs.

## 12. What would make me say do not submit

- UCM's numbers do not reproduce from their code and they do not respond to contact.
- Real agents comply with visible injections so rarely that every effect rate collapses.
- Either group, or a third, publishes the deployment-distribution measurement first.
- **Added 19 Sep:** another construct-validity failure of the same class as the three found
  on 19 Sep. One round is a process that worked. Two is a process that does not.

None of those is true today. All four become more likely every month this waits.
