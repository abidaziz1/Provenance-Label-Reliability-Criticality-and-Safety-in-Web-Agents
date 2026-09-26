# Idea 3: what to do before the team starts

**Date:** 19 Sep 2026, **corrected later the same day.**
**Purpose:** everything on the Idea 3 critical path that does not need two engineers, plus
the three Colab notebooks for work this environment cannot run.

> **CORRECTION HEADER.** An independent audit landed after the first version of this doc.
> Section 1's framing is withdrawn, section 4's description of notebook 01 asserted a safety
> property the code did not have, and all three notebooks have been rebuilt as v2. Corrected
> text is inline and marked. See `Idea3_CORRECTIONS_19Sep2026.md`,
> `Idea3_Reconciliation_1.2pct.md` and `Idea3_Corrected_Figures.md`.

Findings 2 and 3 below stand unchanged. Finding 1's *measurement* stands; its *conclusion*
was superseded within hours by a better one.

---

## 1. Finding: the sampling-frame objection does not survive contact

The plan's own kill test carried the row "16 of 57 Mind2Web sites, one corpus, the
sampling-frame criticism we aim at them lands on us." That row is answerable.

The three shards already downloaded contain **all 57 sites and 209 trajectories**, so no new
data was needed. Rebuilding at 3 trajectories per site across every site present gives 145
trajectories and 1,163 observations, against 48 and 341 in the published frame.

| Measurement | 16-site (published) | 57-site | Corrected (v2 pipeline) |
|---|---:|---:|---:|
| Trajectories / observations | 48 / 341 | 145 / 1,163 | unchanged |
| DOM nodes | 972,737 | 2,460,488 | unchanged |
| Untrusted regions | 2,183 | 6,159 | **5,317** |
| Claim 1, node granularity | 35.17% | 40.30% | **36.98%** |
| Claim 1, region granularity | 77.83% | 74.65% | **71.68%** |
| Claim 1, descendants only (their wording) | — | — | **49.93%** |
| Critical regions with no cue | 79.46% | 79.95% | **WITHDRAWN** |
| Same, U/H only | 95.27% | 84.12% | **WITHDRAWN** |
| C per trajectory, mean / median | 35.4 / 13.5 | 31.7 / 11.0 | **26.3 / 6.0** |
| C p90 / max | 114 / 227 | 85 / 313 | **72 / 355** |

Tripling the site count moves the headline by about 3 points, so **the gap is not a property
of which 16 sites were picked**. That part stands.

> **SUPERSEDED CONCLUSION.** The first version read this as evidence that Prismata's 1.2%
> reflects a different deployment distribution. It does not: their corpus is 72.4% Mind2Web,
> the same dataset. The gap is definitional, and it is now located precisely — their number
> matches the root-to-target reading of "critical path" (we measure 1.13% to 1.73%) and not
> the "contains an actionable descendant" reading their §3 sentence uses (we measure 49.93%
> like-for-like). Full working in `Idea3_Reconciliation_1.2pct.md`.

> **WITHDRAWN.** The no-cue rows were measured on a view with class names removed. Prismata's
> labeler reads class names. The measurement describes our restricted representation, not
> their labeler's input, and must be re-measured on the DOM view they actually get before it
> is quoted anywhere.

> **CORRECTED FIGURES.** The v2 column reflects one code fix: same-origin and relative iframe
> `src` values were being labeled external without an origin check, which inflated untrusted
> regions by 13.7% and untrusted nodes by 16.0%. Four other fixes change nothing on this
> corpus. Per-fix attribution in `Idea3_Corrected_Figures.md`.

Run cost: 140 seconds of CPU. Artifacts `scale/corpus57.json`, `scale/bysite57.json`, and
the corrected `fix/reconcile_v2.json`, `fix/C_gate_v2.json`.

## 2. Finding: the zero-region result is broader than Airbnb and has two causes (stands)

F3 says hashed CSS defeats structural provenance, evidenced by Airbnb returning zero
untrusted regions across 31 observations. At 57 sites, **five sites return zero**, 8.8%
rather than a single anecdote. But the explanation splits.

| Site | Observations | Semantic class ratio | Reading |
|---|---:|---:|---|
| seatgeek | 16 | **0.406** | structural obfuscation |
| airbnb | 31 | **0.570** | structural obfuscation |
| enterprise | 18 | 0.825 | low third-party content |
| mbta | 7 | 0.836 | low third-party content |
| us.megabus | 23 | 0.848 | low third-party content |

A transit authority and a bus operator having no user-generated content is a fact about
those businesses, not a labeler failure. Reporting all five as blind spots would overclaim.
The sharpest test cases are not Airbnb: **rentalcars sits at 0.126 and yields 5 regions in
total, seatgeek at 0.406 yields none.**

This is a correction to a published finding. Make it before a reviewer makes it for us.

## 3. Finding: Mind2Web strips the attributes UCM's detector is built on (stands, confirmed)

UCM's boundary detector never sees page text. Its sanitizer replaces every text node with
`[text:length:N]`, and its prompts lean on `data-testid` while discouraging bare class
selectors. It is a structure-only detector keyed on stable test hooks.

**Confirmed independently in the Colab run of notebook 01:**

| Site | Nodes | class attrs | `data-*` | `data-*` per 1k nodes |
|---|---:|---:|---:|---:|
| sports.yahoo | 25,214 | 15,533 | 11 | 0.44 |
| travelzoo | 8,038 | 4,182 | 11 | 1.37 |
| kohls | 2,204 | 1,077 | 3 | 1.36 |

One surviving `data-*` name in the whole shard: `data_pw_testid_buckeye`.

Consequences, in order:

1. **The WS1 step 2 experiment as written in the paper plan is not valid.** It has to become
   a live-DOM capture or an explicitly adapted detector with the missing-attribute rate
   reported as a limitation.
2. **Corpus strategy is a real decision.** A fair test of structure-only detection needs
   pages as served.
3. **Our own labeler is affected too**, since it reads class and id, which survive. Not
   equally, and the asymmetry must be stated rather than glossed.

## 4. The three notebooks — ALL REPLACED BY v2

> **The v1 notebooks are superseded. Delete them; do not run them.** Two defects fired in
> the user's DRY_RUN pass exactly as the audit predicted.

Filenames: `01_corpus_fidelity_and_structure_only_detection_v2.ipynb`,
`02_cross_vendor_coupling_at_power_v2.ipynb`, `03_agent_compliance_pilot_v2.ipynb`.

All three take credentials from the Colab secrets panel and default to `DRY_RUN = True`.
Every non-API path was executed against the real Mind2Web data before shipping.

### What the v1 DRY_RUN run actually showed

| Notebook | Observed | Diagnosis |
|---|---|---|
| 01 | detection loop reached **kohls only, 2 pages, 3 regions** | six sites configured, one shard loaded, five sites absent. v1 did not notice |
| 01 | UCM clone succeeded, 11,346-char prompt loaded, sanitizer clean (659,088 → 200,000 chars, no leaks) | this part worked |
| 02 | power cell fixed `N_ITEMS = 111`, builder found **40 critical against 37 needed** | a 1.08x margin is not a sample; and the base rate was a disagreement rate |
| 03 | all four conditions reached 40 trials | the builder works end to end |

### `01_..._v2.ipynb` — run first

- **Manifest resolves requested sites against what is loaded and raises if any are missing.**
  This is the fix for the kohls-only run.
- **The prompt guard now exists.** The v1 doc said "if the clone fails the notebook stops".
  It did not: `(prompt_template or "")` accepted `None` and proceeded. v2 raises, and a
  self-test proves the guard fires on `None`, empty, too-short, and missing-commit.
- The clone is pinned and the commit hash is stored with every result row.
- UCM's own sanitizer is imported if available; the run records which sanitizer ran.
- **Captured live pages now enter the detection loop.** v1 wrote them and iterated the
  archive.
- The scorer is node-level with an explicit overmask ratio, so `body` no longer scores F1
  1.00, and it parses the official object-shaped prediction instead of discarding it.
- Every result is described as **agreement between two heuristics**, not accuracy, and never
  as a bound on UCM's performance.

Site selection still runs from rentalcars at 0.126 up to kohls at 0.826, so F1 can be
plotted against semantic class ratio.

### `02_..._v2.ipynb` — the audit's named experiment

- **The base rate is an explicit, justified choice, and 0.294 is refused by assertion.**
  29.4% is inter-labeler disagreement. At a 5% false-trust rate the v1 design had about 15%
  power, not 80%.
- **Site clustering is priced in.** ICC uses the correct `n0`, the design effect inflates the
  required n, and inference is a site-level cluster bootstrap rather than a plain Fisher test.
- **Cross-vendor coupling is the primary statistic**, kappa = P(both wrong) / (P(A) x P(B)),
  which is the quantity the 2.67x rule was derived for. The within-vendor criticality ratio
  is kept, separately labeled, as a secondary question. v1 applied the coupling threshold to
  the criticality ratio.
- **The gate is target-free.** Measured on the 57-site frame at K=21: document order 2.08%
  critical, lexical overlap with the task 7.51%, label-aware 7.55%, oracle tree-distance
  4.08%. The deployable gate admits ~1.8x more critical regions and disagrees with the oracle
  on 7.3%. The published criticality was oracle-informed.
- **It stops before spending if the critical stratum is thin**, and the draw is stratified by
  site so one site cannot supply the whole stratum.

### `03_..._v2.ipynb` — removes the worst kill-test row

- **Four policy arms** separate the label error from the gate grant: `P_correct`,
  `P_err1_fixedgate` (label wrong, gate unchanged), `P_err1_derived` (envelope recomputed
  from the erroneous labels), `P_none`.
- **Paired injection-free controls** on the same page, so compliance is measured against the
  agent's own base rate.
- **One truncation point.** v1 truncated at 60,000 chars before the call and scored exposure
  on the full string, so a trial could be recorded as exposed when the agent never saw the
  injection. v2 records truncation and whether the injection survived it.
- Seeded random site order, realized distribution reported.
- The deterministic controller runs on identical trials at no cost, so the
  mechanism-to-behaviour gap is measured rather than quoted.

> **The baseline this notebook targets has changed.** It is no longer 0% / 100% / 19.5% /
> 70.7%. The 100% came from an arm that granted the attacker's element into the envelope.
> With the gate held fixed a label error yields 0% effect in both envelopes. The target is
> now the contrast between `P_err1_fixedgate` and `P_err1_derived`, and between narrow and
> page-wide envelopes on the derived arm.

## 5. Documents to settle before anyone is assigned

- **Pre-register the corpus and the criticality definition.** 3 trajectories per site across
  all 57 sites, and criticality at a stated gate width. **Added:** the pre-registration must
  say whether the region root counts as an actionable descendant (worth 21.5 to 34.3 points)
  and whether the gate is target-free or oracle-informed (worth 1.8x). Both were unstated.
- **Write the three disclosure emails.** Prismata's group for the Case 3 measurement, a code
  request, **and the question of which definition produced the 1.2%** — that last one is now
  the highest-value message in the project. UCM's group to say we are evaluating their public
  artifact on a different corpus.
- **Decide the venue framing.** Changed 19 Sep to DTRAP primary, TOPS secondary. See the
  paper plan §9.

## 6. Sequence

| When | Item | Needs | Blocking? |
|---|---|---|---|
| Today | Email Prismata about the 1.2% definition | nothing | highest value, unblocks the caveat |
| Today | Run notebook 01 v2 Part 1 with `SMALL_SHARD_ONLY = False` | nothing | gates the rest of 01 |
| Today | Send the other two disclosure emails | nothing | no, but 90 days out |
| Day 1-2 | Run notebook 02 v2 power cell, pick and justify the base rate | nothing | gates the labeling spend |
| Day 1-2 | Start the human ground-truth pilot | people | **now the top blocker** |
| Day 2-3 | Run notebook 02 v2 end to end | 2 API keys | settles the 28 Aug blocker |
| Day 3-5 | Run notebook 03 v2 | 1 API key | removes the worst kill-test row |
| Week 2 | Notebook 01 v2 Parts 2 and 3 | 1 API key, network | decides the corpus strategy |
| Week 2 | Pre-register corpus and criticality | nothing | gates all scaled runs |
| Week 2 | Restate F3 with the two-cause split | nothing | correctness |

Human ground truth has overtaken notebook 02 as the top blocker. Every labeling number in
the paper is currently inter-labeler agreement, and no amount of API spend changes that.

## 7. What is deliberately not started

- **The mechanism, WS4.** Its design depends on what notebook 01 finds about where
  structure-only detection fails.
- **The full live crawl.** Part 2 captures a handful of pages to settle the fidelity
  question.
- **Any prose update to the report artifact.** It still contains the three retracted claims
  and should not circulate without the corrections doc.
- **Scaling beyond 3 trajectories per site.** All 209 are available; the cap is deliberate,
  to keep the site-balanced frame defensible. Lift it only with a stated reason.
