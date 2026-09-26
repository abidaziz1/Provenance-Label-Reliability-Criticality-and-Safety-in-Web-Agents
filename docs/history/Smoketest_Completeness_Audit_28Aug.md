# Idea 3: Smoke-Test Completeness Audit

**Date:** 28 Aug 2026
**Question asked:** is the smoke test complete enough to decide on deeper investment?
**Answer: NO — but it is now one experiment away, and that experiment is feasible.**

Inputs audited: my executed smoke test (48 trajectories), the Codex preregistered
mechanism test (10 trajectories), and my evaluation of it. This document reports
FIVE new analyses run in this session that neither prior test performed.

---

## The gap that both tests missed

Both tests planted errors deliberately. Codex placed 2 false-trust errors at chosen
positions; I planted exactly one under `P_err1`. **Neither measured what fraction of
positions are critical in nature, and neither measured whether real labeler errors
land there.** Every headline number in both reports depends on those two unmeasured
quantities.

---

## NEW A — the natural critical fraction (measured, real DOMs)

Using Codex's stricter criticality definition (region on the task target's critical
path) over 313 real observations with resolvable Mind2Web targets:

| Definition | Critical fraction |
|---|---:|
| Codex construction (assumed) | **40.0%** |
| Natural, strict (measured) | **0.67%** |
| Natural, my original C1 (measured) | **46.6%** |

Codex's construction over-represents criticality by ~60x. Only 4.5% of observations
and 22.9% of trajectories contain any strict-critical region at all.

## NEW B — criticality is a function of GATE WIDTH, not a constant

The two definitions are not rivals; they are two ends of one curve. Prismata composes
`effective_capability = min(action_gate, provenance)`, so a mislabel is critical only
if the gate ALSO admits the element it exposes. Measured sweep (K = actionable
elements the gate admits, ranked by tree distance to the task target):

| Gate width K | Critical fraction | Critical opportunities/trajectory |
|---:|---:|---:|
| 1–5 | 0.67% | 0.29 |
| 13 | 1.24% | 0.54 |
| 21 | 2.57% | 1.12 |
| 55 | 7.28% | 3.19 |
| 89 | 18.61% | 8.15 |
| 233 | **40.08%** ← Codex's implied gate | 17.54 |
| unbounded | **77.44%** ← my C1 regime | 33.90 |

**Neither test stated its gate assumption, and the gate moves the headline number by
115x.** This independently reproduces my F9 (envelope width dominates) inside Codex's
own stricter framework — two routes, same conclusion.

## NEW C — under random error placement, ranking inversions do not survive

Simulated 20,000 paired studies, labeler A genuinely better (1.31% vs 3.50%):

| N trajectories | Safety ranking reverses |
|---:|---:|
| 50 | 12.9% |
| 200 | 4.5% |
| 1000 | **0.0%** |

The inversion observed at small N is sampling noise. **The refined research direction
therefore requires that errors be COUPLED to criticality.** Without coupling there is
no paper.

## NEW D — the coupling requirement is specific and demanding

Inversion needs `eps_A * kappa_A > eps_B * kappa_B`, i.e. `kappa_A/kappa_B > eps_B/eps_A`:

| Labeler pair | Required differential coupling |
|---|---:|
| nano vs Gemini | **2.67x** |
| nano vs mini | 3.44x |
| Gemini vs mini | 1.29x |

It is not enough for errors to cluster. The *better* labeler must cluster onto critical
positions ~2.7x more than the worse one. At that ratio, inversions do persist at scale
(47.3% of studies at N=1000). At ratio 1.0 they vanish (0.0%).

## NEW E — coupling is UNMEASURED, and my data only half-constrains it

Tested three criticality proxies against my 131 natural Claude-vs-structural
disagreements:

| Proxy | Result |
|---|---|
| Region contains actionable elements | OR=1.14, p=1.00 |
| Interactive density (all errors) | p=0.169, direction *opposite* |
| Interactive density (false-trust only) | p=0.320, gap 0.0 |
| DOM depth | p=0.421 |

Power of that test: **98% to detect a 3x coupling, 43% at 2x, 14% at 1.5x.**
So it rules out a strong (>=3x) adverse coupling but says nothing below 2x — and 2.67x
is exactly the region that matters. The hinge assumption sits in my blind spot.

## NEW F — the proposed next-stage pilot is underpowered

Codex's mandatory gate 5 specifies "at least 50 trajectories across at least 10 sites".
Expected natural critical errors in such a pilot:

| Gate regime | Expected critical errors | P(observe ZERO) |
|---|---:|---:|
| very narrow | 0.19 | **82.6%** |
| task-scoped | 0.74 | **47.9%** |
| moderate | 2.09 | 12.4% |

A 50-trajectory pilot would likely observe zero or one natural critical error and could
not estimate coupling at all.

## The one experiment that would complete the smoke test

Measure the **differential criticality coupling** of two independently frozen labelers.
Required scale, derived not guessed:

| Gate regime | Trajectories per labeler |
|---|---:|
| task-scoped (K~21) | **~96** |
| moderate (K~55) | ~34 |

~96 trajectories per labeler is feasible — roughly 2x my existing corpus. This is a
concrete, bounded, affordable experiment, not a research programme.

## Revised decision

**Do not proceed to a full paper yet. Run the coupling experiment first.**

- If differential coupling >= ~2.7x: the refined direction is real and important.
  Proceed to full paper.
- If coupling ~1.0x: ranking inversions are sampling noise, the refined direction
  dies as framed, and the surviving contribution is the **gate-width finding**
  (NEW B) — that trajectory safety is not identified by the labeler at all without
  specifying the action gate. That is a smaller but genuine result.
- Either outcome is publishable-adjacent and cheap to obtain. That asymmetry is
  what makes this the right next step.

## Prior art recheck (28 Aug 2026)

No Prismata code release found. No competitor located for the matched-F1 critical-label
comparison. Novelty position unchanged from the 26 Aug audit: original claim not novel,
refined direction provisionally novel, medium confidence.

## Still unavailable to this session

1. Two frozen non-Anthropic labelers (needs the OpenAI key — still not supplied).
2. Independent human ground truth (40-item sheet still with the user).

Both remain necessary. Neither is optional for the coupling experiment, because the
whole question is about *natural* error placement from *real* labelers.
