# Experiments

One folder per run that produces a number, created from `_template/` by the `new-experiment` skill. Rules: `docs/EXPERIMENT_PROTOCOL.md`.

Runs before 25 Sep 2026 predate this folder. Their scripts are in `scripts/` and their outputs in `results/`; `results/README.md` indexes them.

The 25 Sep pre-registration commits were lost before any push (see `research/CORRECTIONS.md`, 26 Sep), so those four experiments count as exploratory.

| Folder | Task | Claim IDs | Pre-registered (commit) | Status | Headline result | Spend |
| --- | --- | --- | --- | --- | --- | --- |
| `2026-09-25_N0.2_c1-robustness` | N0.2 | K16, K17 | 78e50c7 (lost) | done; rerun 26 Sep, identical | leaf 1.58% to 2.10% (labeler artifact); region 52.56% | $0 |
| `2026-09-25_N0.2_unit-ladder` | N0.2 | K18, K19, K20 | 30178d3 (lost) | done; rerun 26 Sep, identical | pages 38.09% [27.72, 49.05]; tasks 59.31% [47.18, 70.95] | $0 |
| `2026-09-25_N0.3b_labeler-sensitivity` | N0.3b | K24 | not pre-registered | done 26 Sep; reproduces the review's Table 1 | pages 24.33% to 38.09%, tasks 39.31% to 59.31% | $0 |
| `2026-09-25_1.8_attr-survival` | 1.8 | K21 | a020f52 (lost) | done; rerun 26 Sep, identical | 21 attribute names; no site `data-*`, `href`, `on*`, `tabindex`, `style`, `hidden` on 57 of 57 sites | $0 |
| `2026-09-25_C7_ucm-selectors-on-archive` | C7 | K22, K23 | 979f808 (lost) | done; rerun 26 Sep, identical | 24 of 25 hand and 68 of 68 LLM Booking selectors match nothing on the archive | $0 |
| `2026-09-26_C7b_actionability-on-archive` | 1.17 | K26 | 8577256 (and project doc, 26 Sep) | done 26 Sep | requiring an `href` halves Prismata-style criticality: G3 19.57% to 9.40%, ratio 0.48 [0.32, 0.64] | $0 |
| `2026-09-26_1.15_api-smoke-test` | 1.15 | none | 05f54c7 | done 26 Sep | both keys work; Anthropic batch submitted, collected and costed; Gemini batch refused on the free tier | $0.000272 logged |
| `2026-09-26_C7c_live-strip-vs-drift` | 1.18 | K25 | project doc `claude/Idea3_Prereg_C7c_26Sep.md`, 12:46 UTC | done 26 Sep | stripping alone disables 53 of 57 live-matching selectors (hand 11 of 13) | $0 |
