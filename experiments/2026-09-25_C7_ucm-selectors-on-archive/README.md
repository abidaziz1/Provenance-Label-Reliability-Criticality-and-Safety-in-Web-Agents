# C7: UCM's published selectors on archived Mind2Web Booking pages

## Status of this file

**Reconstructed on 26 Sep 2026.** The original README was lost with the workspace before any push. It carried the pre-registration (local commit 979f808) and the results (local commit a645e30). The design and decision rule below are restated from the surviving results write-up. Nobody outside the lost workspace can check the pre-registration, so treat this experiment as exploratory. The analysis was rerun on 26 Sep from public data (UCM at acff2e4, Mind2Web at the pinned revision), and every number below reproduced exactly.

## Design (restated)

- **Question.** Do UCM's published selectors match anything on archived Mind2Web Booking pages? Both the hand-written and the LLM-generated selectors count.
- **Data.**
  - Every step of the 7 Mind2Web Booking trajectories in train shards 0, 1 and 10: 131 pages.
  - UCM's `hand_labels.json` for Booking, Reddit and GitLab.
  - Every `llm_labels.json` under UCM's `results/`.
- **What each selector depends on.** Static analysis of the selector text: `data-*` attributes, hashed-looking class tokens (the `hashed()` heuristic in the script), ids and other attributes.
- **Matching.** lxml's CSS engine. Each selector is tried as written and with attribute names in underscore form, because the archive renames `aria-label` to `aria_label`.
- **Primary outcome.** Take the Booking selectors that match on UCM's own captures (counts from UCM's result files). How many of them match nothing on the archive?
- **Decision rule.** If more than half of those hand selectors match nothing on the archive, C7 gains a demonstration at the level of a defense.
- **Script.** `scripts/ucm_selectors_on_archive.py`. Output: `results/ucm_selectors_on_archive.json`.

## Results (25 Sep; rerun 26 Sep with identical output)

**What UCM's selectors depend on**

| Site, source | Selectors | Use a `data-*` attribute | Use a hashed-looking class | Either |
| --- | ---: | ---: | ---: | ---: |
| Booking, hand | 25 | 92.0% | 32.0% | 92.0% |
| Booking, LLM (3 runs x 3 pages, deduplicated) | 70 | 95.7% | 60.0% | 98.6% |
| Reddit, hand | 17 | 0.0% | 0.0% | 0.0% |
| Reddit, LLM | 70 | 15.7% | 0.0% | 15.7% |
| GitLab, hand | 73 | 13.7% | 2.7% | 16.4% |
| GitLab, LLM | 193 | 5.2% | 1.6% | 6.7% |

**Booking selectors on the archive**

- **Hand selectors.** All 25 match at least one node on UCM's own captured pages. 24 of 25 match nothing on any of the 131 archived pages. The one that matches, `h2.pp-header__title`, hits 6 nodes on 6 pages.
- **LLM selectors.** 68 of 70 match on UCM's captures, and all 68 match nothing on the archive (0 nodes).
- **Hashed class tokens.** None of the 23 that the Booking selectors use (for example `fff1944c52`, `f4008c3a61`) occurs anywhere in the 2023 archive.

**Decision rule outcome: C7 gains its demonstration at the level of a defense** (24 of 25, well over half).

**Reading (corrected 26 Sep).**
- **What the result shows.** Suppose an evaluation reuses UCM's published Booking selectors on Mind2Web. It would mask almost nothing.
- **Its limit.** The result is about reusing selectors across page representations. It does not show how UCM performs on archives. UCM writes its selectors from the page it sees; task 2.8 tests that case.
- **Two confounded causes.**
  - The archive strips every site `data-*` attribute (K21). That alone disables the 92% of hand selectors that use one.
  - Booking's hashed class names changed between the 2023 archive and UCM's capture.
- **How C7c separates them.** `experiments/2026-09-26_C7c_live-strip-vs-drift/` holds the page fixed. On the same live DOM, stripping alone disables 53 of the 57 selectors that work live.
- **How the sites differ.** Reddit's and GitLab's selectors rest mostly on semantic classes, and UCM reports its highest boundary F1 on Reddit (0.997). Booking has the most `data-*` and hashed-class dependence. There UCM reports F1 0.879 and gives the reason: "most of its class names are not semantically meaningful (e.g., ss133neaa)" (UCM §7.2, Table 2).

## Deviations

- Each selector was also tried with attribute names in Mind2Web's underscore form (`data_testid`). The counts above use that variant, which can only add matches.
- The 25 Sep reading said UCM's pages were from 2026. UCM does not record a capture date. Its URLs carry a 1 Jul 2025 check-in, and its repo starts on 7 Jul 2026 (`research/CORRECTIONS.md`, 26 Sep).
- The pre-registration commit was lost before any push (see above).
