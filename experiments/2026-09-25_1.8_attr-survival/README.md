# 1.8: which attributes survive in the Mind2Web archive, per site

## Status of this file

**Reconstructed on 26 Sep 2026.** The original README and script (pre-registration in local commit a020f52, results in 7d44fd8) were lost with the workspace before any push. `scripts/attr_survival.py` was rewritten from the recorded output fields and rerun on 26 Sep. It reproduces every recorded number: 57 sites, 1,163 pages, 2,405,975 element nodes, 21 attribute names, one `data-*` name. The pre-registration cannot be checked by a third party, so treat the experiment as exploratory.

## Design

- **Frame.** The 57-site frame of `scripts/c1_robustness.py`: the first 3 trajectories per site by `annotation_id` in train shards 0, 1 and 10, taking every step's `raw_html` as stored. The count is 145 trajectories and 1,163 pages, parsed with lxml without `deep_parse`.
- **Counts.**
  - Every attribute name on every element node.
  - Per site, the rate per 1,000 nodes of each input a structural defense reads: `data-*`, `on*`, `tabindex`, `contenteditable`, `href`, `for`, `hidden`, `style`, `role`, `aria-*`, `id` and `class`.
- **Decision (ROADMAP 1.8).** If no site keeps its own `data-*`, the archive head-to-head with UCM is dead, and only live pages count.

## Results

- The archive keeps **21 attribute names**, listed here by count over 2,405,975 nodes:

  | Attribute | Count |
  | --- | ---: |
  | `backend_node_id` | 2,405,326 |
  | `bounding_box_rect` | 2,405,326 |
  | `class` | 1,421,009 |
  | `is_clickable` | 337,263 |
  | `role` | 153,928 |
  | `id` | 108,847 |
  | `value` | 91,709 |
  | `aria_label` | 78,228 |
  | `type` | 74,626 |
  | `title` | 59,750 |
  | `alt` | 43,019 |
  | `input_value` | 36,942 |
  | `name` | 35,643 |
  | `label` | 13,426 |
  | `placeholder` | 4,749 |
  | `data_pw_testid_buckeye` | 3,135 |
  | `option_selected` | 2,189 |
  | `input_checked` | 1,574 |
  | `aria_role` | 497 |
  | `aria_description` | 74 |
  | `text_value` | 15 |

- **No site-authored `data-*` survives.** The only `data-*` name is `data_pw_testid_buckeye`, apparently added by the capture tool ("pw" suggests Playwright). It appears on all 57 sites, at fewer than 1 per 1,000 nodes on 21 of them.
- **Seven defense inputs are absent on every site.** `on*`, `tabindex`, `contenteditable`, `href`, `for`, `hidden` and `style` occur on 0 of 57 sites.
- **What survives.** `role` survives on 56 sites and `aria-*` (renamed `aria_*`) on 55. `id` and `class` survive on all 57.
- **Decision.** The archive head-to-head with UCM's `data-*` selectors is dead. `experiments/2026-09-25_C7_ucm-selectors-on-archive/` and `experiments/2026-09-26_C7c_live-strip-vs-drift/` measure the consequence.

## Deviations

- The script was rewritten after the loss (see above). Output field names match the originals, and `tests/test_claims.py::test_K21` passes on the rerun.

## What this changes

- **C7.** The inputs that selector masking (`data-*`) and attribute-based actionability (`href`, `onclick`, `tabindex`, `contenteditable`) need are absent from the archive. Prismata's §3 count ran on pages like these. `experiments/2026-09-26_C7b_actionability-on-archive/` tests what that does to Prismata-style criticality.
