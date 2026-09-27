# Idea 3: the corrected gate ablation, at scale

**Date:** 19 Sep 2026
**Run:** 5,088 trials, 159 trial pages over 27 sites, 57-site frame, deterministic
worst-case-compliant controller, 801 s of CPU. No API spend.
**Artifacts:** `fix/ablation_v2.py`, `fix/ablation_v2.json`, `fix/ablation_v2.log`.

This is item 3 of `Idea3_CORRECTIONS_19Sep2026.md`: *"Run the corrected gate ablation as a
designed experiment, including the envelope-derived arm."* It confirms the prediction made
there, and it produces one result nobody predicted.

## 1. The design

Four policy arms, with the label error and the gate grant separated. The published testbed
had only two, and its error arm did both at once.

| Arm | Labels | Envelope |
|---|---|---|
| `P_correct` | correct | derived from correct labels |
| `P_err1_fixedgate` | injected region relabeled D | **unchanged** |
| `P_err1_derived` | injected region relabeled D | **recomputed from the erroneous labels** |
| `P_none` | no defense | everything writable |

Plus an injection-free paired control on the same page for every trial, one truncation point
used for both sending and scoring, and a seeded random site order.

## 2. Results

| Envelope | Attack | Policy | n | L1 exposed | L2 selected | L3 gate | L4 effect | control L4 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| narrow | containment | P_correct | 159 | 54.7% | 0.0% | 0.0% | **0.0%** | 0.0% |
| narrow | containment | P_err1_fixedgate | 159 | 96.9% | 0.0% | 0.0% | **0.0%** | 0.0% |
| narrow | containment | P_err1_derived | 159 | 96.9% | 0.0% | 0.0% | **0.0%** | 0.0% |
| narrow | containment | P_none | 159 | 96.9% | 96.9% | 96.9% | **96.9%** | 0.0% |
| narrow | influence escape | P_correct | 159 | 54.7% | 0.0% | 0.0% | **0.0%** | 0.0% |
| narrow | influence escape | P_err1_fixedgate | 159 | 96.9% | 0.0% | 0.0% | **0.0%** | 0.0% |
| narrow | influence escape | P_err1_derived | 159 | 96.9% | 0.0% | 0.0% | **0.0%** | 0.0% |
| narrow | influence escape | P_none | 159 | 96.9% | 76.7% | 76.7% | **76.7%** | 0.0% |
| page | containment | P_correct | 159 | 54.7% | 0.0% | 0.0% | **0.0%** | 0.0% |
| page | containment | P_err1_fixedgate | 159 | 96.9% | 0.0% | 0.0% | **0.0%** | 0.0% |
| page | containment | **P_err1_derived** | 159 | 96.9% | 96.9% | 96.9% | **96.9%** | 0.0% |
| page | containment | P_none | 159 | 96.9% | 96.9% | 96.9% | **96.9%** | 0.0% |
| page | influence escape | P_correct | 159 | 54.7% | 43.4% | 43.4% | **43.4%** | 0.0% |
| page | influence escape | P_err1_fixedgate | 159 | 96.9% | 76.7% | 76.7% | **76.7%** | 0.0% |
| page | influence escape | P_err1_derived | 159 | 96.9% | 76.7% | 76.7% | **76.7%** | 0.0% |
| page | influence escape | P_none | 159 | 96.9% | 76.7% | 76.7% | **76.7%** | 0.0% |

Paired within-page contrasts, with site-clustered bootstrap intervals over 27 sites:

| Envelope | Attack | Contrast | pairs | delta L4 | 95% CI |
|---|---|---|---:|---:|---|
| narrow | containment | fixedgate − correct | 159 | 0.0% | [0.0, 0.0] |
| narrow | containment | derived − fixedgate | 159 | 0.0% | [0.0, 0.0] |
| page | containment | fixedgate − correct | 159 | 0.0% | [0.0, 0.0] |
| page | containment | **derived − fixedgate** | 159 | **+96.9%** | **[91.9, 100.0]** |
| narrow | influence escape | fixedgate − correct | 159 | 0.0% | [0.0, 0.0] |
| narrow | influence escape | derived − fixedgate | 159 | 0.0% | [0.0, 0.0] |
| page | influence escape | **fixedgate − correct** | 159 | **+33.3%** | **[15.3, 55.2]** |
| page | influence escape | derived − fixedgate | 159 | 0.0% | [0.0, 0.0] |

Every control arm is 0.0%. The compliant controller never clicks the damaging control on an
uninjected page, so the injected rates are compliance, not base rate.

## 3. What it says

**Containment is a two-failure event, and the second failure is the gate.** A label error
with the gate held fixed produces exposure and nothing else: zero selection, zero admission,
zero effect, in both envelopes, over 159 paired pages on 27 sites, with an interval of
exactly [0.0, 0.0]. Letting that error propagate into the envelope produces a 96.9% effect
rate — but only under a page-wide envelope. Under a task-scoped envelope the derived arm is
still 0.0%.

**That contrast, 0.0% against 96.9% on the same arm and the same pages, is the paper's
confinement-width result.** It is now derived from the error rather than granted by hand,
which is what the published version did and what inverted its headline.

**Influence escape needs no label error at all**, and a page-wide envelope admits it at
43.4% with every label correct. That was 19.5% on the 16-site frame; the 57-site frame with
a broader damaging-control set is harsher. A task-scoped envelope stops it completely in
every arm.

## 4. The result nobody predicted

`page / influence escape / fixedgate − correct = +33.3% [15.3, 55.2]`. A label error, with
the gate held fixed, **does** produce an effect here. That contradicts the clean "labels
alone do nothing" story, so it was chased down rather than reported as noise.

The cause is mechanical and, on inspection, correct behaviour. `build_capability_map` prunes
external content unconditionally:

```python
elif p in ('U','H'):
    cap[id(el)] = RO if id(el) in task_relevant_untrusted else PR
else:                      # E
    cap[id(el)] = PR
```

When the largest untrusted region on a page is labeled **E**, correct labels prune it and
the injection never reaches the agent at all. That is why L1 exposure is 54.7% under
`P_correct` and 96.9% under every error arm: the 42-point gap is the share of trials whose
chosen region was external and therefore invisible. A label error makes that content visible.

So there **is** a single-failure pathway for a label error, and it runs through **exposure,
not admission**. It only produces an effect where the gate was already wide enough to admit
the target — a page-wide envelope, where the damaging control is developer-authored and
admitted regardless of any label. Under a task-scoped envelope the same error exposes the
injection and still yields 0.0%.

Stated precisely for the paper: **a label error changes what the agent sees; the envelope
changes what the agent can do. Only the second produces a protected effect on its own, and
the first produces one only when the second was already permissive.**

## 5. A small scoring finding

106 of 2,544 injected trials were truncated at 60,000 characters, and in **80 of them the
injection itself was cut off**. The v1 notebook truncated before the call and scored exposure
on the untruncated string, so all 80 would have been recorded as exposed when the agent never
saw the injection. That is 3.1% of trials mis-scored in the direction of the hypothesis. The
v2 notebook truncates once and records both facts.

## 6. What to do with this

1. **Replace F8 in every document.** "A single critical false-trust error defeats
   confinement" becomes "an effect requires a wrong label and a gate wide enough to admit the
   mislabeled control, except for influence escape under a page-wide envelope, where the
   error's contribution is exposure of otherwise-pruned external content."
2. **The narrow-versus-page contrast on `P_err1_derived` is the headline figure.** 0.0%
   against 96.9%, same pages, same error, same attack. Nothing in either published system
   states its envelope width.
3. **Run notebook 03 v2 with a real agent.** These are controller numbers and therefore upper
   bounds. The gap between them and a real agent is what that notebook measures, and it is
   the last fatal row in the reviewer kill test.
4. **Report the E-pruning effect as its own result.** "Correct labels made the injection
   invisible in 45% of trials" is a defensive success worth stating, and it is the mechanism
   behind the exposure asymmetry rather than an artifact of it.
