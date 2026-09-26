# C7b: Prismata-style criticality when a link needs an href

## Pre-registration (26 Sep 2026)

Saved to the claude.ai project (`claude/Idea3_Recovery_Bundle_26Sep.md`) before any run. The run waits for `src/pipeline_v2.py`, which is in the kit zip and was lost with the workspace.

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

(filled after the run)
