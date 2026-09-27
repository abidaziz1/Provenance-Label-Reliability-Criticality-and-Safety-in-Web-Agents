**Idea 3: independent research audit and publication decision**

Date: 19 September 2026

**Decision: continue through a bounded validation stage. The current notebooks and strongest claims need revision before paid experiments or submission.** A defensible empirical paper remains plausible. A TOPS submission is conditional on evidence that the proposed measurements predict or explain actual security outcomes beyond existing least-privilege reasoning. Choosing a more accessible journal does not resolve the present measurement defects.

This review distinguishes reported historical results, code behavior verified here, claims checked against primary sources, and proposed experiments. It does not treat one category as evidence for another.

**What was inspected and executed.** I inspected all 31 code cells in the three supplied notebooks, validated their notebook schemas, and compared their shared pipeline. All three contain the same shared pipeline text. None contains saved execution outputs or populated execution counts. This does not establish that nobody ran them; it means these copies do not preserve execution evidence.

I downloaded the pinned Mind2Web `train_10.json` shard at revision `17ece8eb89862368edc0cc806acee6fca5163474`. It contains nine trajectories, 49 observations, and three sites: kohls, sports.yahoo, and travelzoo. I executed the attribute audit and processed the first two observations per trajectory through the supplied pipeline: 18 observations, 36,862 parsed nodes, 75 detected untrusted regions, and 93 parsing splices. This is a limited code check, not a reproduction of the 57-site study.

I also executed controlled counterexamples against the notebooks' original functions, ran Notebook 02's original power cell, and independently enumerated its Fisher-test power. No paid model calls, live browser-agent rollouts, or human adjudication were performed. The source notebooks were not edited.

The attached main paper, supplement, anonymous manuscript, and reconstruction changelog concern RecurGuard/reasoning-consumption research. The stage documents contain broader research planning. They do not supply the missing raw Idea 3 results. The original 37-check smoke-test notebook and the 57-site result tables are not in this attachment set, so their reported exact matches and corpus totals remain historical claims in this review.

**Corrections to the research narrative.** Prismata's labeler uses DOM structure, including classes; its agent receives a filtered accessibility representation. Its rarity corpus already includes 2,832 Mind2Web DOMs and 65,416 Mind2Web untrusted-path instances. Its reported F1 concerns admitted elements. These facts undermine the restricted-input comparison, the simple distribution explanation, and the cross-paper F1 ranking in the handoff. [Prismata, Sections 2, 3, and 4.3](https://arxiv.org/html/2607.08147v1)

UCM's mislabel ablation reports 6 ± 5% ASR and suggests the agent's warning prompt as a possible explanation. A false-trusted region bypasses masking, so its typed return channel does not establish the claimed causal explanation for that result. “One mislabeled element” is not a trial count; its WASP evaluation describes 12 attacker goals. [UCM, Appendix E](https://arxiv.org/html/2607.05277v1)

The proposed contrast between one real system's ASR and a deterministic simulator's exposure rate cannot identify the cause of their difference. Different agents, prompts, tasks, attacks, annotation definitions, and denominators change simultaneously. The comparison needs matched conditions and interventions inside a common evaluation setup.

**Assessment of the smoke-test evidence.**

| Reported finding | Value as research evidence | Claim that remains supportable |
|---|---|---|
| All 37 numerical checks reproduced | Evidence of computational repeatability, if the archived outputs establish it | The implemented analysis repeats under the documented environment; this does not validate the ground truth or reference-system fidelity |
| Site ICC near 0.24 | A useful dependence signal, subject to the definition of error and repeated-page sampling | Analyze site/template clustering; do not assume every DOM occurrence is independent |
| Airbnb yields zero detected untrusted regions | A diagnostic of the heuristic's output | Inspect independently annotated regions before calling it a whole-site failure |
| Criticality increases as the gate expands | A useful simulator sensitivity curve | Quantify exposure under explicitly defined admission sets; do not call the percentages attack-success rates |
| One injected error yields full exposure | A possible conditional witness | Identify the exact label and gate interventions; do not infer natural prevalence or universal agent compliance |
| High no-cue percentages | A property of a chosen cue detector and representation | Report the view and cue definition; do not infer the capabilities of a labeler that sees more information |
| Expansion to 57 sites gives similar values | A useful coverage check, pending raw outputs | It weakens one subset-selection concern; it does not eliminate annotation, representation, or deployment-sampling bias |

The parsing fixes and willingness to revise the initial 40% criticality assumption were productive research steps. The supplied code now needs further validation because the decoder also accepts literal code examples as live markup. Repeatable instrumentation can repeat the same mistake.

**Notebook 01 needs a measurement rewrite before it can evaluate UCM.** Cell numbers below are zero-based indices in the supplied files, including Markdown cells.

| Location | Finding | Required correction |
|---|---|---|
| Cell 6 and cell 15 | Only `train_10.json` is loaded. With the default target list, the paid loop reaches two Kohl's observations, not twelve pages across six sites | Build and validate an explicit page manifest; fail if the intended sample is unavailable |
| Cell 9 versus cell 15 | Captured live pages are saved but never used by the detector loop | Make the chosen corpus an explicit input to detection and scoring |
| Cell 11 | The source repository is cloned at its current branch head, without a commit pin | Freeze the commit and record it |
| Cell 11 and cell 13 | Failure to load the prompt prints a warning; the caller accepts `None` as an empty string | Stop before a paid call if a required prompt or source module is absent |
| Cell 13 | The Booking-specific template is reused for other sites; template placeholders are not filled; a new instruction is appended | Use the official site configuration or label the experiment as a new detector |
| Cell 12 | The custom sanitizer differs from the official Booking sanitizer | Import the actual implementation or demonstrate equivalence on a conformance set |
| Cell 13 and cell 14 | The official prompt describes selector objects; the scorer expects strings and silently skips invalid selectors | Parse and validate the declared schema; retain failures as failures |
| Cell 14 | `ground_truth_untrusted` is the same structural heuristic being questioned | Replace it with independent annotation or use the honest term “heuristic agreement” |
| Cell 14 | Selecting an ancestor of any reference region can earn credit without charging for trusted content also masked | Score covered content and blocked controls; require an all-page selector to incur an overmasking penalty |
| Cell 16 | An archive score is called a lower bound | Treat it as a result on a transformed input; no lower-bound relation is established |

The default shard's first-two-observation audit found 25 `data*` attributes among 35,456 nodes, with one distinct name, `data_pw_testid_buckeye`. There were 20,792 class attributes. This verifies attribute scarcity in this small sample. Scarcity alone does not identify which attributes were removed, what fraction survived, or the causal effect on detection.

The official Booking implementation removes or anonymizes information the notebook keeps, includes site-specific processing, and specifies three LLM turns. Notebook 01 makes a single pass with its own sanitizer. These are different methods. [UCM Booking implementation](https://github.com/ethz-spylab/untrusted-content-masking/blob/main/src/automatic_boundary_detection/sites/booking/site.py)

For fidelity research, compare full and transformed views of the same snapshot. Contemporary live pages versus a 2023 archive confound representation with site evolution. Mind2Web's official repository describes raw traces, network captures, recordings, and MHTML snapshots that may provide a contemporaneous reference if accessible. [Mind2Web data documentation](https://github.com/OSU-NLP-Group/Mind2Web)

**Notebook 02 does not implement the proposed decisive experiment.** Its title and decision rule promise differential coupling, but the code measures separate within-model associations against heuristic labels.

| Location | Finding | Consequence |
|---|---|---|
| Cells 0, 1, and 5 | The 29.4% disagreement figure is renamed a measured false-trust rate | The power calculation uses an unsupported error baseline |
| Cell 10 | Only regions the structural heuristic already marks untrusted enter the candidate pool | Whole regions missed by that heuristic cannot be recovered by the experiment |
| Cell 10 | Text-length filters keep 60–1,200 characters, then show at most 600 | The sample excludes other region types and may omit decisive context |
| Cell 10 | `K=21` means nearest actionable nodes by DOM distance to the recorded correct next target | This is a retrospective, oracle-informed admission proxy, not a measured deployment gate |
| Cells 6, 10, and 12 | Classes and IDs are deliberately omitted; context is a short ancestry/text packet | The labeler input does not reproduce the reference defense |
| Cells 10 and 13 | Packet rows lack stable task, action, region, and snapshot identifiers | Annotation and later reconciliation are fragile |
| Cell 10 | The site cap is checked before an observation, not inside the region loop | A single observation can exceed the intended cap |
| Cells 13 and 15 | There is no human-adjudication import or ambiguity protocol | Predicted labels are evaluated against a proxy as if it were ground truth |
| Cell 15 | Independent-item Fisher tests are primary despite the claimed site dependence | P-values and power do not account for repeated templates and clustered errors |
| Cell 15 | No cross-vendor coupling ratio or joint interval is computed | The study cannot apply the handoff's differential-coupling decision |
| Cell 15 | Overlap counts substitute for an error-dependence or ensemble evaluation | The conclusion that ensembling cannot help is unsupported |
| Cell 15 | ICC uses `N/k` despite unequal cluster sizes | Use an estimator appropriate for the sampled cluster sizes and uncertainty |
| Cell 16 | A within-model RR above 2.67 is treated as proof of a safety-ranking inversion | The statistic and claim do not match |

Independent vendors provide model diversity, not a guarantee of independent errors. An actual ensemble rule also changes false-trust and false-distrust rates. Evaluate that rule and its utility cost rather than infer its value solely from overlap.

**Power check.** The original cell returned 111 items for the default twofold effect: 37 critical and 74 other. I then enumerated the independent binomial outcome pairs and applied the same two-sided Fisher rejection rule, without Monte Carlo approximation.

| Assumed noncritical false-trust rate | Assumed critical rate | Power at 37 critical / 74 other |
|---|---|---|
| 1% | 2% | 2.02% |
| 3% | 6% | 10.41% |
| 5% | 10% | 14.81% |
| 10% | 20% | 26.60% |
| 29.4% | 58.8% | 81.12% |

These are conditional design calculations, not estimates of actual labeler performance. The apparent low cost comes partly from assuming a very high error baseline. They do not justify the earlier 96-trajectory requirement, a cost estimate in cents, or a claim that a previous null occurred because of low power. The previous pilot used a different selection process; its exact allocation and endpoint must be reconstructed.

**The 2.67 threshold needs rederivation.** Let `E_j` be a specified false-trust error for labeler `j`, and `C` a fixed definition of criticality. On a common sampling population, define:

```text
e_j = P(E_j)
q   = P(C)
c_j = P(C | E_j) / P(C)

P(E_j and C) = e_j * q * c_j
```

If `e_A < e_B`, the ordering of critical-error probability reverses when:

```text
c_A / c_B > e_B / e_A
```

For example, error rates of 3% and 8% give a threshold of 8/3, about 2.67. Other base rates give other thresholds. This is an illustrative derivation, not a reconstruction of the original simulation's undocumented inputs.

Notebook 02 instead computes `P(E_j | C) / P(E_j | not C)` for each vendor. If that value is `r_j`, then `c_j = r_j / (q*r_j + 1-q)`. These quantities are related but not interchangeable. Two labelers can both have a within-model ratio of 3 while preserving their safety ordering.

Actual unauthorized actions also depend on gate decisions and agent behavior after exposure. Aggregate F1 has a different relation to false-trust probability again, because it includes other error types. Directly estimate the paired difference in the chosen safety endpoint and the accuracy metric, with a joint uncertainty analysis. Use the simulation threshold as a sensitivity calculation, not a universal publication rule.

The 1:2 criticality sample can support conditional rates if selection within strata is sound. Population accuracy and critical-error prevalence need the original stratum weights. Human review must include model-agreement cases and regions the heuristic did not detect; reviewing only disagreements cannot reveal shared misses.

**Notebook 03 is a one-step model-choice probe, not an end-to-end web-agent evaluation.** It can become a useful pilot after repair.

| Location | Finding | Required correction |
|---|---|---|
| Cell 6, `P_err1` | The provenance change also adds the injected link to `envx` | Hold the action gate fixed when testing a label-only intervention; test gate errors separately |
| Cell 6 | A new “Verify account” link is added to the DOM | Establish that the attacker can create that control under the tested threat model |
| Cell 6 | Candidate trials require an unrelated “damaging” button even for containment | Remove unintended eligibility filters or document their role |
| Cell 6 | The largest detected untrusted region is chosen | Describe this as an attack-site selection policy; it is not natural error prevalence |
| Cell 7 | The model returns `CLICK id` or `DONE`; no browser action executes | Report action selection or admitted attempts, not completed harmful effects |
| Cell 7 | A dangerous-label regex and inequality with one gold next target define success | Specify task-level unauthorized outcomes; a different next action may still be legitimate |
| Cell 7 | The observation is truncated before the call, but exposure is scored on the full observation | Record and score the exact transmitted input |
| Cell 8 | The first 40 eligible observations are used in a fixed site order | Randomize or stratify matched cases; retain task and step IDs |
| Cells 1 and 8 | A complete clean/attack and correct/error pairing is absent | Add paired benign controls and the missing correct-label containment control |
| Cell 8 | Historical deterministic percentages are compared with a different selected sample | Recompute the controller on the exact same cases |
| Cell 9 | Near-zero response to one simple attack is treated as falsification of the risk | Check attack strength, task solvability, exposure, and coverage before interpreting a null |

The deterministic controller is not a universal upper bound over real agents. It reacts to one marker and a limited string-matching rule. A model can select an attacker action through behavior that this controller does not implement. A formal upper bound requires maximization over a stated action set and the same cases, inputs, and endpoint.

Even under independent trials, zero successes in 40 trials has a one-sided 95% upper bound of 7.22%. Clustered trials provide less information than 40 independent opportunities. A zero from this pilot cannot establish a negligible deployment risk.

**Direct counterexamples executed in this review.** These establish code behavior. They do not estimate how often the issue occurs in Mind2Web or in deployed systems.

| Check | Observed result | Interpretation |
|---|---|---|
| Score selector `body` on a page containing trusted controls and one review | Precision = recall = F1 = 1.0 | The scorer does not penalize masking the trusted parts of the page |
| Feed the scorer the official-shaped object `{"css_selector": ".review", ...}` | TP = 0, FP = 0, FN = 1 | Valid selector information is silently discarded because the schema differs |
| Build candidate items for an opaque-class review fixture | Zero items selected | Undetected regions disappear before vendor labeling |
| Select the injected link in `P_err1` under a narrow envelope | Gate admitted; `effect=True` | The error condition explicitly opens the gate for that link |
| Keep the same injected label condition but deny the added gate permission | Gate rejected; `effect=False` | The result depends on the gate change, not the provenance change alone |
| Parse escaped button markup inside a literal `pre` example | Actionable count changes 0 to 1 | Deep parsing manufactures a live control from displayed code |
| Inspect the same parser's accounting | One splice, `nodes_added=0` | Nodes are counted after they have been moved out of the fragment |
| Classify an iframe with a relative first-party URL | `E`, `iframe:crossorigin` | Cross-origin status is assumed rather than checked |
| Compare `aria-label` with `aria_label` | Standard HTML spelling missed; archive spelling detected | The live and archived input paths need attribute normalization |
| Prune a span inside an actionable parent | Pruned text remains in the parent's displayed label | Recursive label extraction can bypass the mock renderer's pruning |
| Compare custom and official Booking sanitizers | Custom version retains sample image alt text, URL, and comment; official version removes/anonymizes them | The claimed sanitizer equivalence fails on a small fixture |

**Notebook engineering.** All three omit the required initial Git pull, metric-bearing `push()` calls after useful results, and final push. They also lack durable result checkpoints during paid loops. Paths and model parameters are scattered beyond the configuration block. The large corpus is not automatically a Git artifact, but newly created large captures and outputs need an explicit persistent destination and a manifest committed to Git, as specified in your notebook rules.

Before execution, add commit pins, package versions, model snapshots where available, prompt hashes, corpus hashes, unique trial IDs, resumable per-call results, token usage, and explicit failure accounting. API compatibility and model response limits were not tested in this review. A syntactically valid notebook is not an end-to-end validated experiment.

**Novelty assessment.** The generic propositions “accuracy does not fully determine harm” and “restricting actions reduces possible effects” are too broad to carry the paper. Related work already includes browser authority restriction in ceLLMate and an emphasis on adaptive attacks and utility in Jia et al.'s defense evaluation. [ceLLMate](https://arxiv.org/abs/2512.12594), [A Critical Evaluation of Defenses against Prompt Injection](https://arxiv.org/abs/2505.18333)

Confidently Wrong is adjacent on the limits of aggregate detector metrics under shifted attacks. It increases the need for an action-grounded result specific to provenance defenses. This targeted review does not certify that no competing paper exists. [Confidently Wrong](https://arxiv.org/abs/2606.22659)

A stronger research question is: **Under independently annotated boundaries, when do real or adversarially induced boundary errors become unauthorized state changes, and which control prevents that conversion at a declared utility cost?** The contribution would be an empirically validated evaluation method and findings, rather than a generic warning about F1.

Three variables must remain distinct: the representation the detector receives, the actions the gate authorizes, and the information allowed through the quarantined channel. Cardinality `K` cannot summarize policy quality. Allowing one search action and allowing one account-deletion action give the same `K` with very different consequences.

The observed monotonicity of a nested top-K criticality curve is partly guaranteed by construction. Its slope may still be useful. The substantive test is whether an operationally realistic policy improves measured safety at comparable task completion, and whether a proposed risk measure predicts outcomes on held-out sites better than simpler baselines.

**Recommended next work, in order.** These are effort estimates and review gates, not promises about sample size or acceptance.

1. **Repair and freeze the measurement setup, approximately one week.** Resolve the counterexamples above. Add negative controls for all-page masking, literal code, same-origin frames, hidden controls, and untrusted descendants. Keep the labeler input and agent observation separate. Recompute the historical figures under corrected definitions and preserve both versions with reasons for changes. A reference implementation, an ablation, and a surrogate must have distinct names.

2. **Build independent ground truth and a matched-view corpus, approximately one to two weeks.** Start with a rubric pilot around 40 items, but sample both heuristic-positive and heuristic-negative regions, including agreement cases. Two reviewers should label source control and task authorization independently, without seeing model predictions. Preserve ambiguous labels and report sensitivity to them. Use stable snapshot, task, step, and region identifiers. Obtain enough reviewed data for the actual primary endpoint after estimating its frequency; do not freeze the confirmatory size from the disagreement rate.

3. **Run a controlled behavioral pilot before scaling.** A concrete starting design is 12 task/attack cases across four to six site templates. Cross oracle versus native boundary labels, narrow task-valid versus broader gates, and text versus typed read interfaces; pair clean and attacked episodes. That is 12 × 2 × 2 × 2 × 2 = 192 episodes per agent, or 384 for two agents. This is a design example, not a powered confirmatory sample. Keep prompts and authorized task outcomes fixed where the factor design allows. Evaluate real local state transitions, not only proposed clicks. Run the core factorial inside a common stack first; confirm useful contrasts in a second implementation before generalizing across defenses.

4. **Recalculate confirmatory sampling from the repaired pilot.** Estimate error rates, criticality prevalence, task/episode dependence, site clustering, invalid-response rates, and the number of observed unauthorized effects. Simulate the actual paired, clustered design. Freeze a practically meaningful effect and the corresponding interval or power target. Stratified enrichment is reasonable, but retain inclusion probabilities and deployment weights. Keep adversarially selected opportunities separate from random deployment prevalence.

5. **Promote the study only if its result survives the controls.** Hold out sites or templates; compare aggregate classification scores, false-trust rate, critical-error rate, and an action-grounded risk measure. Test whether the proposed metric adds predictive value. Keep one or two well-defined adaptive attack families and clean utility controls. Record failed captures and unsolved tasks in the denominator policy.

At every stage, separate exposure, action selection, gate admission, executed state change, and task success. A single label error can increase one without increasing the others. Typed channels should also be evaluated for incorrect values; a type check does not certify factual correctness.

**Publication decision after that work.**

| Outcome | Manuscript scope | My venue judgment |
|---|---|---|
| A reproducible effect survives matched conditions, held-out sites, and more than one defense implementation; the study explains actual policy violations and utility | Full empirical security paper; a new defense is optional if the measurement result is strong enough | TOPS is a reasonable ambition; TDSC is another possible fit for substantial systems work |
| Reliable representation/annotation findings survive, with bounded behavioral evidence and useful deployment guidance | Focused empirical paper with narrow claims and a reusable evaluation artifact | DTRAP is the practical target I would plan around first |
| Only a nested-K curve and deliberately forced simulation failures survive | Technical report or a carefully scoped workshop contribution | Insufficient evidence to recommend a journal submission yet |
| The differences disappear under independent truth, faithful inputs, and fixed gates | Archive the negative result and stop the broad safety claim | Do not prolong the project solely to preserve the original narrative |

These are judgments about contribution fit, not acceptance forecasts. DTRAP's own editorial material emphasizes research and practice around digital threats. [DTRAP editorial site](https://dtrap-blog.acm.org/)

One venue correction in the earlier advice is supported: the publisher's current Computers & Security description explicitly places security of AI/ML systems, including LLMs, outside its stated scope. I would not use it as the fallback for this project under that policy. [Elsevier's journal description](https://shop.elsevier.com/journals/computers-and-security/0167-4048)

I could not retrieve current TOPS/DTRAP policy pages or verify your APC-waiver eligibility. Do not treat the handoff's guaranteed 100% waiver as established. The recommendation here does not depend on a waiver, a particular deadline, or an assumed staffing allocation.

**Resource choice.** Allocate a two-to-three-week correction and decision stage before a five-month program. One researcher who owns the estimands and annotation rubric, plus one engineer who owns the reference implementations and execution records, is a reasonable proposed starting allocation. If that stage establishes only a careful limited result, publish that result at its actual scope. If it establishes an unexpected, generalizable relationship between boundary errors and executed violations, invest in the broader journal study.

**Artifact fingerprints.**

```text
01_corpus_fidelity_and_structure_only_detection.ipynb
SHA256 575912669f92c72639a6fad41c7f5091a37bee94490a8260ce0195202852df34

02_cross_vendor_coupling_at_power.ipynb
SHA256 cef4617d9dec9c1193df4512d47b28ff7deb94519fd4470b5a7a39062a6d259b

03_agent_compliance_pilot.ipynb
SHA256 5ddea603537afc6bb9f744712c5496ad9b755bb7612d2e11fff52aa2dd95a56d
```

All quantitative checks attributed to this review are either outputs of the supplied functions on the specified shard/fixtures or calculations under explicit assumptions. No new empirical labeler error rate, live-agent ASR, or deployment-risk estimate was measured.
