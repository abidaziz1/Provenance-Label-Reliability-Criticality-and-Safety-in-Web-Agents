# Annotations

Human labels for task 1.7, the exposure audit that decides P3, and for 2.1 only if P3 needs more than the audit. Task 3.1 was dropped at Gate N. `ANNOTATOR_BRIEF.md` is the plain-language brief for the two annotators.

- `GUIDE.md`: the guide annotators read (version 0.1).
- `../scripts/build_annotation_page.py`: builds one self-contained HTML page from an items file. Page text is escaped and rendered as plain text; `tests/test_annotation_page.py` checks this.
- `demo_items.json` and `demo_page.html`: two invented items for trying the page. They are not study data.
- `raw/<annotator>_<date>.json`: one file per annotator per session, as saved by the page. Annotators email their file to Alam, who commits it. The repo is public, but annotators must not browse it while labeling: it holds the labeler's rules and what we expect to find, which would unblind them. Never edited after commit.
- Annotators are identified by a short code, not by name, in every committed file.
- Adjudicated labels and agreement statistics are produced by a script and written to the experiment folder of the task that uses them.

## First batch: the exposure audit (task 1.7, about 100 items)

The item sampler is the next piece to write. Its pre-registration goes in `experiments/<date>_1.7_exposure-audit/` before the batch is drawn, and it fixes the following.

- **Population.** Every exposed page in the 57-site frame under labeler V0: a page with a visible actionable element whose nearest untrusted strict ancestor is a seeded region. One item per exposed page: the seed responsible for the most exposed controls on it, with one exposed control drawn from that seed. `scripts/labeler_sensitivity.py` already attributes each exposed control to its seed.
- **Sample.** About 100 items, at most 3 per site, drawn site-stratified with seed 20261001, and shuffled so sites and seed rules interleave.
- **Blinding.** The page shows no rule name, no labeler variant and no count of exposed controls. Annotators see only the fields listed in `GUIDE.md`.
- **Analysis (H6 in `research/PREREGISTRATION.md`).**
  - The labeler's precision on exposure-driving seeds. A seed counts as correct when Q1 is neither "the site itself" nor "can't tell".
  - Per-page and per-task exposure recomputed with the audited seeds, with site-cluster 95% intervals.
  - The kill rule: keep P3 only if the lower bound of audited per-task exposure is above 25%.
  - Q3 gives the first per-page Case-3 estimate (backlog item O1).
- **Agreement.** Cohen's kappa between the two annotators, with a site-cluster interval. Alam adjudicates disagreements blind.
