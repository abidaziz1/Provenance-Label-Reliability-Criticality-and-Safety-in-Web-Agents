# Idea 3: the 1.2% reconciled

**Date:** 19 Sep 2026
**Status:** resolved. The gap is definitional, it is located precisely, and locating it
produced a better paper claim than the one it replaces.
**Budget spent:** none. No API keys, no labeling, no human time beyond reading this.

Closes item 0 of `Idea3_CORRECTIONS_19Sep2026.md`: *"Reconcile the 1.2% against 74.65% at
the definition level. Until this is done, the project's most-quoted number is unexplained."*

---

## 1. What Prismata actually says

Three sentences matter. All three were pulled from `arxiv.org/html/2607.08147v1` on two
separate fetches with different prompts; both returned the same wording.

> **§2.1** "Prismata traces the critical path: the full HTML ancestor chain from the DOM
> root to that element."

> **§1.1** "In an empirical analysis of 1,500+ of the most visited sites (§3), of the over
> 90,000 instances of untrusted content sampled, only 1.2% lay on a critical path to an
> interactable element, which we address next."

> **§3** "Only 1,086 of the 90,408 untrusted paths (1.2%) contain an actionable descendant,
> an element the agent could click or fill (Fig. 5); the rest are leaves or text-only
> regions that cannot sit above a targetable element. We count a descendant as actionable
> if it is a non-hidden form control, a link, a label target, an element with an interactive
> ARIA role, an onclick handler, an editable region, or a tabindex."

The last two describe the same 1.2% but they are not the same measurement. §2.1 defines the
critical path as the chain to *that* element, singular, the one the agent is heading for.
§3 describes a property of the untrusted content on its own.

Corpus, from §3: 2,832 Common Crawl domains at one page each plus 2,832 Mind2Web pages,
5,664 DOMs; 90,408 untrusted path instances, 24,992 Common Crawl and 65,416 Mind2Web.
**The Mind2Web half is 23.10 untrusted instances per page.** That number does most of the
work below.

---

## 2. Three candidates, eliminated by measurement

All figures on our 57-site frame: 145 trajectories, 1,163 observations, 2,460,488 nodes,
same shards and revision as the published smoke test.

### 2.1 Not the actionability definition

| Criticality measured with | Regions critical |
|---|---:|
| our `is_actionable` | 71.68% |
| their seven clauses, verbatim | 71.43% |

0.25 points. Their definition is broader, so it should push the rate up. It does not,
because on Mind2Web archives only three of their seven clauses ever fire: link (298,756),
form control (80,531), interactive ARIA role (23,307). Label targets, `onclick`,
`contenteditable` and `tabindex` contribute **zero** — the archive strips them.

### 2.2 Not the page sampling

| Frame | Regions per page | Regions critical |
|---|---:|---:|
| every step (1,163 pages) | 4.57 | 71.43% |
| first step only (145 pages) | 3.20 | **80.82%** |

Thinning to one page per trajectory, which is closer to their sampling shape, moves
criticality **up**. Eliminated, and it moves the wrong way.

### 2.3 The unit explains part and cannot explain all

| Granularity | units | per page | critical (their actionable definition) |
|---|---:|---:|---:|
| maximal untrusted region | 5,317 | 4.57 | 71.43% |
| region plus untrusted item children | 11,436 | 9.83 | 63.37% |
| untrusted block-level nodes | 74,623 | 64.16 | 50.55% |
| untrusted leaf paths | 51,017 | 43.87 | 10.13% |
| every untrusted node | 166,948 | 143.55 | 35.38% |
| **Prismata, Mind2Web half** | **65,416** | **23.10** | **1.2%** |

Their density sits between our region-plus-items (9.83) and leaf-path (43.87) granularity.
Across that whole span criticality runs 63% down to 10%. It never approaches 1.2%. To get
there, 98.8% of units would have to be leaves or text-only; at our most leaf-heavy
granularity the figure is 89.9%. Refining the unit narrows the gap about six-fold and
leaves forty-fold unexplained.

---

## 3. Our own number was wrong too, by 21.5 points

Their sentence says "contain an actionable **descendant**". Our published claim-1 counted a
region as critical if it contained an actionable descendant **or was itself actionable** —
an untrusted `<a class="user-review-link">` counted. On a literal reading of their wording
it should not.

| Frame | descendants only | including the region root |
|---|---:|---:|
| 57-site | **49.93%** | 71.43% |
| 16-site published frame | **41.58%** | 75.85% |

Worth 21.5 points on the 57-site frame and 34.3 on the 16-site one. It also explains an
internal inconsistency nobody had chased: `critical_fraction.py` said 46.64% and the
pipeline said 77.83% on the same frame. The whole difference is this (46.45% descendants-only
over all observations; the target-resolvable subsetting accounts for 0.19 points, the region
root for 31.4).

**The like-for-like figure against Prismata's wording is 49.93%, not 74.65%.** The gap is
41.6x, not 62x. Still nowhere near closed.

---

## 4. What does close it

Measure the §1.1 and §2.1 reading: a unit is critical when it lies on the root-to-target
ancestor chain for the element the task actually needs. Over the 1,103 observations with a
resolvable Mind2Web target:

| Granularity | per page | on the root-to-target path |
|---|---:|---:|
| maximal untrusted region | 4.61 | **1.73%** |
| region plus untrusted item children | 9.86 | **1.13%** |
| untrusted block-level nodes | 54.39 | 0.58% |
| every untrusted node | 125.29 | 0.30% |
| **Prismata reports** | | **1.2%** |

**Their 1.2% is bracketed by our two coarsest granularities under the strict test, 1.13% to
1.73%, and is forty-fold from every granularity under the loose test.**

Not a one-frame coincidence: the published gate-width sweep independently found 0.67% at
K ≤ 5 on the 16-site frame using the same root-to-target construction, and this run
reproduces that to the digit.

---

## 5. The finding

**Prismata's headline residual-risk number is computed under one definition of "critical
path" and described under another, and the two differ by roughly forty-fold on the dataset
supplying 72% of their corpus.**

The number matches the §1.1/§2.1 reading. The §3 sentence reporting it says "contain an
actionable descendant", a property of the untrusted content alone; under that sentence's
plain meaning the rate on their own majority dataset is 10% to 63% depending on unit, and
about 50% at the unit closest to how a maximal untrusted region is normally drawn.

This matters beyond bookkeeping, because the two readings answer different safety questions.
"Is this untrusted block above something clickable?" is a property of the page, computable
at label time. "Is this untrusted block above the element the agent is about to act on?"
needs the target, which is what the agent is still looking for. A residual risk of 0.10%
resting on the second is a statement about a defender that already knows the answer. The
Case 1/2/3 decomposition inherits whichever reading you pick, and so does the 0.10% Case 3
figure.

**The honest caveat.** This is an inference from our corpus to theirs. Their labeler is an
LLM deriving trust; ours is a class-name and id heuristic. We cannot rule out that their
labeler produces spans shaped so differently that the loose test genuinely yields 1.2% on
their labeling. What we can say is how extreme that shape would have to be: at 23.10 units
per page, 98.8% would be leaves or text-only, against 10% to 63% criticality everywhere in
that density band on our labeling. Settling it needs their labeler's output on a shared page
set, which is one email or one repository away and should be the team's first ask.

---

## 6. What this changes in the paper

- The headline comparison becomes **49.93% against 1.2% with a definitional account**, not
  74.65% against 1.2% unexplained. A weaker number and a much stronger claim.
- The sampling-frame story stays retracted. Corpus composition was never the issue.
- The contribution is no longer "we failed to reproduce their number". It is "their number
  is reproducible under one of the two definitions their own paper gives for it, and the
  choice moves the residual-risk argument forty-fold". That is a measurement-methodology
  contribution, which is what DTRAP publishes.
- Every criticality figure in our own work must state whether the region root counts. Ours
  did not, and the omission was worth 21.5 to 34.3 points.

## 7. Artifacts

`fix/pipeline_v2.py`, `fix/score_v2.py`, `fix/reconcile.py` (with `FIX_OFF=` to isolate any
single fix), `fix/reconcile_{v1,v2,no_same_origin,no_attr_norm}.json`,
`fix/descendant_only.py`, `fix/recompute_C_and_gate.py`, `fix/gate_comparison.py`,
`fix/test_counterexamples.py` (33 assertions, all passing).
