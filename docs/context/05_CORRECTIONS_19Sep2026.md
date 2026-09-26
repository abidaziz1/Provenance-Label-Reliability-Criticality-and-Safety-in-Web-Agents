# Idea 3: corrections after independent audit

**Date:** 19 Sep 2026
**Status of the audit: substantially correct. I verified its two load-bearing claims and all six
of its code counterexamples. Two published findings are retracted and one predeclared
decision flips.**

This document supersedes specific claims in `Idea3_Smoketest_EXECUTED_Results.md`,
`Idea3_Reproduction_And_Status.md`, `Idea3_Paper_Plan.md`, and the published report
artifact. Read it before acting on any of them.

---

## 1. RETRACTED: the deployment-distribution explanation

**What was claimed.** That Prismata's 1.2% critical-path figure fails to reproduce because
it was measured on a broad, low-interaction web crawl while we measured interaction-heavy
sites where agents are deployed. This was stated as the headline framing in the report, in
the paper plan, and in the status doc.

**What is true.** Prismata's corpus is majority Mind2Web, the same dataset we used. Verified
against the paper, Section 3:

> "From Common Crawl we take the Tranco top 10K domains ... giving 2,832 domains and
> 283,200 archived DOMs. For the labeled corpus we take one page per Common Crawl domain
> and an equal number of Mind2Web pages ... The result is a 5,664-DOM corpus, split evenly
> between the two sources."
>
> "This yields 90,408 untrusted path instances, 24,992 from Common Crawl and 65,416 from
> Mind2Web."

**65,416 of 90,408 instances, or 72.4%, come from Mind2Web.** The sampling-frame explanation
cannot account for the gap and is withdrawn.

**What this does not do.** It does not close the gap. Two analyses drawing mostly on the same
dataset report 1.2% and 74.65%, so at least one definition differs sharply. Candidates, in
order of likely size:

| Candidate | Ours | Theirs |
|---|---|---|
| Unit of measurement | maximal untrusted *region* | untrusted *path instance* |
| Page sampling inside Mind2Web | 1,163 observations, multiple steps per task, 57 sites | 2,832 DOMs, roughly one page per domain |
| Labeler | class-name and id heuristic | LLM trust derivation |
| "Critical path" definition | region contains an actionable descendant | path to an interactable element, gate unstated |

Reconciling these is now the highest-value single task in the project. It is cheap, it needs
no API budget, and until it is done the discrepancy is not attributable to anything.

## 2. RETRACTED: the labeler-cannot-see-the-cue framing (F2)

F2 reported that 79.5% of critical regions carry no cue "in the labeler's input", measured
over an accessibility-tree view with class names and ids removed.

Prismata's own Case 2 text names "developer-authored class names" alongside headings and
accessibility attributes as the structural cues its labeler uses. Its labeler sees class
names. Our restricted view was our construction, not theirs, so the measurement does not
describe their labeler's input.

The underlying measurement is still worth something, but only as stated: it describes how
much cue signal survives *a particular restricted representation*. Any claim about what
Prismata's labeler can or cannot see must be re-measured on the DOM view it actually gets.

## 3. RETRACTED: single label error defeats confinement (F8), and the kill rule flips

This is the most consequential item and the audit found it correctly.

The `P_err1` arm did two things at once: it relabeled the injected region as developer-authored,
**and** it added the attacker's injected link to the agent's allowed action set:

```python
envx = set(env) | ({id(holder)} if holder is not None else set())
```

I re-ran the full 984-trial testbed on the published 48-trajectory frame with a third arm,
`P_err1_fixedgate`, identical in every way except that the gate is held fixed:

| Envelope | Attack | Policy | n | L1 exposed | L2 selected | L3 gate | L4 effect |
|---|---|---|---:|---:|---:|---:|---:|
| narrow | containment | P_correct | 82 | 22.0% | 0.0% | 0.0% | **0.0%** |
| narrow | containment | P_err1 | 82 | 100% | 100% | 100% | **100%** |
| narrow | containment | **P_err1_fixedgate** | 82 | 100% | 0.0% | 0.0% | **0.0%** |
| page | containment | P_err1 | 82 | 100% | 100% | 100% | **100%** |
| page | containment | **P_err1_fixedgate** | 82 | 100% | 0.0% | 0.0% | **0.0%** |
| narrow | influence escape | P_err1 / fixedgate | 82 | 100% | 1.2% | 1.2% | **0.0% / 0.0%** |
| page | influence escape | P_err1 / fixedgate | 82 | 100% | 100% | 100% | **70.7% / 70.7%** |

**A label error alone produces exposure and nothing else. Zero selection, zero admission,
zero effect, in both envelopes.** The published 0% to 100% result is produced by the gate
grant, not by the label error.

Consequences:

- **F8 as written is withdrawn.** "A single critical false-trust error defeats confinement
  completely" is not supported by this testbed.
- **The predeclared kill rule was not refuted.** It read: "Kill if mechanical confinement
  prevents every critical error from reaching a protected effect." Under the corrected arm,
  confinement did prevent it. The proceed decision of 26 August rested partly on a
  confounded arm and has to be re-argued on the remaining evidence.
- **Proceed bar C is withdrawn.** It read "a critical-error count predicts end-to-end
  compromise, 0% to 100%, deterministic." That was the same arm.

**What replaces it, and it is a better claim.** The corrected result says a single failure is
insufficient and two simultaneous failures are required: the label must be wrong *and* the
gate must admit the mislabeled control. That is a sharper statement of the confinement-width
thesis than the one we published, and it points the same direction, but the headline inverts.
We were telling the story backwards.

**One open modelling question, and it is a real experiment rather than a patch.** For a
page-wide envelope defined as "every developer-authored actionable element", a label error
should propagate into gate admission by construction, because the mislabeled control now
looks developer-authored. The published code did not derive that, it granted it by fiat in
both envelopes. The correct third arm recomputes the envelope from the erroneous labels.
Expect page-wide to return to a high effect rate on that arm and narrow to stay at zero.
That arm is what the paper should report.

Artifacts: `audit/gate_ablation.py`, `audit/gate_ablation.json`, `audit/gate_ablation.log`.

## 4. CONFIRMED: all six code counterexamples reproduce

Executed against the shipped pipeline. Every one behaves as the audit describes.

| Check | Result |
|---|---|
| Score the selector `body` on a page with nav, a button and one review | P = R = F1 = 1.00. Masking the entire page scores perfectly; overmasking is never charged |
| Feed the scorer the official-shaped object `{"css_selector": ".review", ...}` | TP 0, FP 0, FN 1. Valid selector information is silently discarded |
| `visible_cue` on standard `aria-label` versus archive `aria_label` | Standard HTML spelling returns None; archive spelling matches. Live pages break the cue detector |
| `gt_provenance` on `<iframe src="/help/faq.html">` | Returns `('E', 'iframe:crossorigin')`. Same-origin frames are labeled external without checking origin |
| Literal escaped button markup inside a `<pre>` code sample | Actionable count 0 to 1, and `deep_parse` reports `spliced=1, nodes_added=0`. The parser manufactures a live control from displayed code, and miscounts it |
| Prune a child inside an actionable parent, then render | `[id=7] a: Buy SECRET REVIEW TEXT`. Pruned text leaks through the parent's label |

The code-example splice is the one with the widest blast radius: it inflates actionable counts,
which feed criticality, which feeds the gate-width curve and C.

## 5. Also confirmed by inspection

- **Notebook 01 reaches two Kohl's observations.** It loads only `train_10.json`, which holds
  kohls, sports.yahoo and travelzoo. Five of the six configured sites are absent.
- **Captured live pages never enter the detector loop.** Part 2 writes them, Part 3 iterates
  the archive.
- **The prompt guard does not exist.** I wrote, in the pre-work doc and in chat, that the
  notebook "stops if the clone fails". It does not. `(prompt_template or "")` accepts None and
  proceeds. Asserting a safety property the code lacks is the worst error in this set.
- **Notebook 02 does not implement differential coupling.** It computes a within-vendor
  P(error|critical)/P(error|not critical) and then applies the 2.67x cross-vendor decision rule
  to it. Those are different quantities. The audit's derivation is right.
- **The 29.4% baseline is disagreement, not error.** Our own completeness audit said so on
  28 August, and the power cell then used it as `BASE_RATE`. At a 5% true baseline the design
  has about 15% power, not 80%.
- **Observation truncated at 60,000 chars before the call but exposure scored on the full
  string** in notebook 03.

## 6. Where I would add to the audit rather than dispute it

- **The kill-rule flip is bigger than the audit states.** It treats F8 as "a possible
  conditional witness". The fixed-gate arm shows the predeclared kill condition was satisfied,
  not merely unproven. That is a decision reversal, not a caveat.
- **The Prismata corpus finding makes the gap more interesting, not less.** Two analyses over
  mostly the same data reporting 1.2% and 74.65% means a definitional difference of roughly
  sixty-fold is sitting there unexplained. That is a cheap, concrete, publishable question.
- **The nested top-K monotonicity point is correct but the curve retains one use.** The
  *shape* is guaranteed; the *location* of the knee is not. Where the curve turns is an
  empirical property of real DOMs. That is worth reporting, framed narrowly.
- **On the Git workflow requirement:** the audit says all three notebooks omit a required
  pull/checkpoint/push workflow. I cannot find that requirement in any project document I have
  access to. If it is a standing convention, point me at it and I will apply it. If it came
  from a different project, it does not apply here.

## 7. What survives

- The 57-site corpus expansion. It is recomputation of our own pipeline and is unaffected by
  items 1 to 3, though the code-example splice defect in item 4 means actionable counts, and
  therefore C, need recomputation after the parser fix.
- The zero-region two-cause split from the pre-work, which stands.
- The attribute-fidelity finding that Mind2Web strips `data-*`, which stands and still
  invalidates the naive head-to-head.
- The influence-escape results, which are untouched by the gate confound: 19.5% under a
  page-wide envelope with every label correct, 0% under a task-scoped one, identical across
  both error arms. **This is now the strongest surviving evidence for the confinement-width
  thesis**, and it does not depend on any planted label error.
- Exact numerical reproducibility, which the audit correctly describes as repeatability rather
  than validity.

## 8. Corrected next steps

The audit's ordering is better than the plan's. Adopt it, with one addition at the top.

0. **Reconcile the 1.2% against 74.65% at the definition level.** No budget, no keys. Match
   their unit, their page sample, and their critical-path definition on the Mind2Web half of
   their corpus. Until this is done, the project's most-quoted number is unexplained.
1. Repair and freeze the measurement setup. Fix the six counterexamples, add the negative
   controls the audit names, and recompute every historical figure that depends on actionable
   counts. Keep both versions with reasons.
2. Build independent ground truth, sampling heuristic-negative regions and agreement cases,
   not only disagreements.
3. Run the corrected gate ablation as a designed experiment, including the envelope-derived
   arm from item 3 above.
4. Only then size the confirmatory study, from measured rates rather than from the 29.4%
   disagreement figure.

**Venue implication.** The audit's DTRAP-first recommendation is better calibrated than my
TOPS-first one, given what just happened to three of the findings. I would also drop the
"100% ACM waiver" claim from the plan until someone verifies current policy directly.

## 9. Process note

Three of these errors were catchable here and were not caught. The gate confound sat in code
I read closely enough to transcribe into a notebook. The Prismata corpus composition is in
Section 3 of a paper I fetched twice. Both were missed because I was checking whether the
numbers reproduced rather than whether the experiment measured what it claimed. Reproduction
discipline does not substitute for construct validity, and the project now has good evidence
of the difference.
