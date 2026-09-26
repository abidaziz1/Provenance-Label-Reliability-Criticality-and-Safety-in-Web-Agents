# Idea 3: corrected figures, with reasons

**Date:** 19 Sep 2026
**Purpose:** one table a future session can trust. Every published number that moved, what
moved it, and every published number that did not move and why.

Both versions were produced by the same harness (`fix/recompute_C_and_gate.py`,
`fix/reconcile.py`) with the fixes behind flags, so "v1" is not a memory of an old run —
it is the corrected code with the fixes switched off, and it reproduces the published
values exactly. That reproduction is the evidence that the diffs below are attributable.

## 1. Which fix moved which number

Five defects were fixed. Only one of them moves any figure on this corpus.

| Fix | Effect on the 57-site frame |
|---|---|
| **D4 same-origin iframe** — `<iframe src="/help/faq.html">` was labeled external without checking origin | **regions −13.7%, untrusted nodes −16.0%, claim-1 −2.97 points.** This is the whole of the v1→v2 change |
| D3 aria-label normalization | zero. The archive uses the underscore spelling throughout, so the hyphen fallback never fires. It matters only on live pages |
| D5 escaped markup spliced inside `<pre>`/`<code>` | **zero. `skipped_literal` = 0 over all 1,163 pages.** The defect is real (unit test proves it) and never occurs in this corpus |
| D5b `nodes_added` accounting | zero on counts; corrects the reported statistic only |
| D6 pruned text leaking through a parent's label | zero on corpus counts; changes the transmitted observation, which is the testbed, not the measurement |

**This partly rebuts the audit.** It called the `<pre>` splice "the one with the widest blast
radius" because it inflates actionable counts, which feed criticality, C and the gate curve.
Measured: actionable counts are identical between v1 and v2 (487,288 both), because the
defect never fires on Mind2Web. The audit was right that the defect is real and right that
it would matter on a corpus containing code samples. It does not matter here.

## 2. Every figure that moved

| Figure | Published (v1) | Corrected (v2) | Cause |
|---|---:|---:|---|
| untrusted regions, 57-site | 6,159 | 5,317 | D4 |
| untrusted nodes, 57-site | 198,767 | 166,948 | D4 |
| claim-1 region, 57-site | 74.65% | 71.68% | D4 |
| claim-1 region, 16-site | 77.83% | 76.44% | D4 |
| claim-1 node, 57-site | 40.30% | 36.98% | D4 |
| C per trajectory, 57-site mean | 31.7 | 26.3 | D4 |
| C per trajectory, 57-site median | 11.0 | 6.0 | D4 |
| C per trajectory, 16-site mean | 35.4 | 32.7 | D4 |
| gate curve, 16-site, K ≤ 5 | 0.67% | 0.71% | D4 |
| gate curve, 16-site, unbounded | 77.44% | 75.99% | D4 |
| trajectories with zero critical regions, 57-site | 22 | 36 | D4 |

One counter-intuitive movement worth recording: **C max per trajectory went up**, 313 to 355
on the 57-site frame. Removing the blanket `E` label from same-origin frames lets their
contents fall through to the identifier heuristics, so a UGC-classed node that used to sit
*inside* an external region now becomes a region root of its own. Net effect is −13.7%
regions, but individual pages can gain. That is correct behaviour, not a regression.

## 3. Every figure that did not move

| Figure | Value | Why it is unaffected |
|---|---:|---|
| actionable elements, 57-site | 487,288 | D5 never fires on this corpus |
| nodes parsed, 57-site | 2,460,488 | same |
| deep_parse splices / nodes added | 1,500 / 54,513 | same |
| exact reproducibility of the 37 checked values | matched | reproduction is repeatability, not validity; unchanged either way |
| Mind2Web strips `data-*` | 0.44 to 1.37 per 1k nodes | attribute audit, independent of all five fixes |
| zero-region two-cause split (obfuscation vs low UGC) | stands | region counts shift, the split does not |

## 4. A sixth defect, found while fixing the other five

`score_v2.py` compared `id()` values of lxml element proxies across two separately built
sets. lxml creates proxies on demand and frees them when the last reference drops, after
which CPython reuses the id. A negative control that should have scored zero recall scored
0.667. Fixed by pinning every element for the duration of the call. Any code in this project
that compares `id()` across element sets must hold a reference to all of them — the corpus
scripts do, by keeping `tree.xpath('//*')` alive, but that was luck rather than design.

## 5. The criticality definition, restated

Two choices in our own definition are worth more than all five code fixes combined.

| Choice | 57-site | 16-site |
|---|---:|---:|
| region critical if it contains an actionable **descendant** (Prismata's wording) | 49.93% | 41.58% |
| region critical if it contains one **or is itself actionable** (what we published) | 71.43% | 75.85% |

21.5 and 34.3 points. See `Idea3_Reconciliation_1.2pct.md`. Every criticality figure in the
paper must state which it uses.

## 6. The gate is oracle-informed, and the deployable one is wider

The published criticality ranks actionable elements by tree distance to the task's target
node. A defender labeling a page does not have the target. Measured on the 57-site frame at
K = 21 over 2,596 actionable-bearing regions on 410 pages:

| Gate | Target-free | Critical | Sites | Agrees with oracle |
|---|---|---:|---:|---:|
| document order | yes | 2.08% | 8 | 95.4% |
| lexical overlap with the task string | yes | **7.51%** | 23 | 92.7% |
| label-aware lexical | yes | 7.55% | 23 | 92.7% |
| tree distance to target | **no** | 4.08% | 26 | 100% |

The deployable gate admits roughly 1.8x more critical regions than the oracle gate. The
published figure was not conservative, and the two disagree on 7.3% of regions. Report both.
