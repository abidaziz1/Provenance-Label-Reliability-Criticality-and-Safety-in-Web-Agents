# C7b: Prismata-style criticality when a link needs an href

## Pre-registration (26 Sep 2026)

Saved to the dated project record (`Idea3_Recovery_Bundle_26Sep.md`) before any run. The run waits for `src/pipeline_v2.py`, which was restored before analysis began.

- **Question.** Prismata §3 counts a descendant as actionable if it is "a non-hidden form control, a link, a label target, an element with an interactive ARIA role, an onclick handler, an editable region, or a tabindex". It computes the 1.2% on archived pages, 65,416 of its 90,408 instances from Mind2Web. The Mind2Web archive removes `href`, `onclick`, `tabindex` and `contenteditable` on 57 of 57 sites (K21). Our rule counts every `<a>` as a link, and links are 74% of our clause hits (K12: 298,756 of 402,594). Suppose a count requires an `href` for a link, as a browser does for a hyperlink. On the archive, that count loses most of what makes an element actionable. How far does that move Prismata-style criticality on the same pages?
- **Claims tested.** NOVELTY_LEDGER C7 (the Prismata side) and the open question whether the 1.2% reproduces (C1'); new row K26.
- **Frame.** The 57-site frame of `scripts/c1_robustness.py`: 1,163 pages, 145 tasks.
- **Rules.**
  - R0, as published: every `<a>` is a link.
  - R1: an `<a>` is a link only with an `href`; every other clause is unchanged.
  - R2: R1, plus any element whose stored `is_clickable` flag is true.
- **Definitions.** Non-hidden as in `c1_robustness.visible`. Strict descendants only: the unit itself does not count. No gate. Units: G0 region, G3 every untrusted node, G4 leaf.
- **Outcomes.** For each rule:
  - criticality per visible unit;
  - per-page and per-task exposure;
  - site-cluster 95% intervals (B = 10,000, seed 20260925).
- **Reproduction check.**
  - R0 must reproduce K17 (G0 52.56%), K16 (G4 2.10%) and K19 (38.09% of pages, 59.31% of tasks).
  - R0 on G3 must equal the c1-robustness value, 19.57%.
  - If any of these fails, stop and find out why before reading R1.
- **Primary outcome.** The R1/R0 ratio of G3 criticality per visible unit.
- **Decision rule.**
  - R1/R0 at or below 0.5: the page representation moves Prismata-style criticality at least 2x. P1 gains its Prismata side, and email 1.1 asks which representation and which link rule Prismata used.
  - R1/R0 at or above 0.8: drop the Prismata side of P1.
  - Between: report it as a partial effect.
- **Construct check.** This tests sensitivity to a choice we do not know Prismata made. It cannot show what Prismata did. R2 stands in for a count that trusts the capture-time clickability flag in place of re-rendering the stored HTML.
- **Exploratory.** Whether R1 comes near 1.2% at any unit. No rule attached.
- **Script.** `scripts/actionability_on_archive.py` (written 25 Sep; unchanged since).
- **Budget.** $0.

## Results

Run 26 Sep 2026, after the pre-registration commit (8577256). Output: `results/actionability_on_archive.json`. Frame: 1,163 pages, 145 tasks, 57 sites.

**Reproduction check: passed.**
- R0 gives 52.56% for G0, 19.57% for G3 and 2.10% for G4.
- It gives 38.09% of pages and 59.31% of tasks exposed.
- These equal K17, the c1-robustness G3 value, K16 and K19.

**What the archive does to links.** Pages carry 256.9 `<a>` elements each, and not one of them has an `href`. Under R0, anchors are 69.1% of visible actionable elements.

| Rule | Visible actionable per page | G0 region | G3 node | G4 leaf | Pages exposed | Tasks exposed |
| --- | ---: | --- | --- | --- | --- | --- |
| R0, any `<a>` is a link (as published) | 179.4 | 52.56% [38.78, 67.45] | 19.57% [13.86, 27.90] | 2.10% [0.34, 6.08] | 38.09% [27.72, 49.05] | 59.31% [47.18, 70.95] |
| R1, a link needs an `href` | 68.6 | 23.94% [13.09, 40.23] | 9.40% [6.69, 13.50] | 1.29% [0.13, 4.48] | 25.28% [16.71, 35.21] | 50.34% [38.62, 62.14] |
| R2, R1 or the stored `is_clickable` flag | 188.7 | 50.82% [38.05, 64.72] | 20.57% [16.17, 27.63] | 1.94% [0.34, 5.64] | 38.09% [27.72, 49.05] | 59.31% [47.18, 70.95] |

Criticality is per visible unit, with site-cluster 95% intervals.

**Primary outcome.** The R1/R0 ratio of G3 criticality is **0.48**. Other units: G0 0.46, G4 0.61, page exposure 0.66.

**Decision rule outcome: at or below 0.5, so P1 gains its Prismata side**, and email 1.1 asks which representation and link rule Prismata used.
- **Exploratory interval.** It was added after the run. A site-cluster 95% interval for the ratio is [0.32, 0.64].
- **What it rules out.** The "drop" branch (at or above 0.8) is ruled out.
- **What it leaves open.** Whether the factor exceeds 2 is not settled: the interval spans 0.5. The fair summary is "about a factor of 2".

**Reading.**
- **Requiring an `href` roughly halves Prismata-style criticality** on archived pages. Whether a link needs an `href` is exactly what a browser's DevTools enumeration would decide on a re-rendered archive.
- **Trusting the capture-time `is_clickable` flag restores the tag-rule numbers (R2).** The archive's own flag stands in for what the page offered when it was live.
- **Neither rule brings per-node criticality near 1.2%.** R1 still gives 9.40% per visible untrusted node, about 8 times the published figure. The leaf-level R1 value, 1.29%, comes near it only through the labeler artifact documented in N0.3b.
- **So the representation is one of three unknowns, with the unit and the labeler.** It moves the number by about 2x, and it does not explain the 1.2% alone.

## Deviations

- **Wrong output folder.** The pre-registered script wrote to `experiments/2026-09-25_C7b_actionability-on-archive/`, a folder name left over from its first draft. The output was moved here and the path corrected. The computation did not change, and a rerun reproduced every pre-registered field exactly.
- **The exploratory interval** for the primary ratio was added to the script after the first run.
