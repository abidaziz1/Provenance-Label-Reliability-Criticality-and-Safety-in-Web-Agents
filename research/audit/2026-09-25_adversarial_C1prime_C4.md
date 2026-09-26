# Adversarial review: C1' and C4 (Prismata / UCM measurement study)

Date: 2026-09-25. Role: a hostile but fair program-committee reviewer, held to the IEEE S&P / USENIX Security standard. I was not involved in this work. Nothing under `/home/claude/work/repo` was modified. Tool budget: 15 calls.

**What I read.**
- `research/NOVELTY_LEDGER.md`
- `experiments/2026-09-25_N0.2_c1-robustness/`: README and config
- `experiments/2026-09-25_N0.2_unit-ladder/`: README, config and `results/unit_ladder.json`
- `scripts/c1_robustness.py` and `scripts/unit_ladder.py`
- `scripts/ablation_v2.py`: `build` and `score`
- `src/pipeline_v2.py`: `deep_parse`, `gt_provenance`, `build_capability_map`, `render_observation`, `controller` and `capability_gate`
- `research/audit/2026-09-25_C1_C2_C10.md`, and the C4 section of `research/audit/2026-09-25_C3_C4_C5.md`
- `results/ablation_v2.log:35` and `research/CORRECTIONS.md:13`
- The Prismata HTML (arXiv:2607.08147), fetched with WebFetch. Its quotes come from an extraction model and must be checked against the PDF.

## Verdict in brief

**C1' does not survive as written.** Its three load-bearing numbers each fail a different check.

- The "reproduction" of 1.2% (1.58% to 2.10%) is an artifact of our labeler. All 808 of 808 "critical leaves" exist only because `gt_provenance` relabels a nested menu, footer, header or nav as trusted. A leaf has no descendants of its own.
- The "18 to 28 times" ratio changes the criterion and the unit at the same time. With the criterion held fixed, going from unit to page multiplies the rate by only 1.9 to 4.0.
- The per-element figure (9.19%) and the per-target figure (7.71%) are mostly labeler false positives:
  - Expedia's first-party page wrapper (`Storefront-Homepage`) counts as hosted content.
  - eBay's results layout (`s-answer-region`) counts as user content.
  - UUID-like attribute values count as "ad".

  With stricter labels the two figures fall to 1.2% to 2.5% and 0.5% to 2.7%.

What survives is descriptive. Under stricter heuristic labels, 24% to 31% of pages and 39% to 48% of tasks have a visible control inside ad, user or hosted content. Excluding five sites whose "ads" are first-party promotions brings the page figure to about 17%. Prismata reports no per-page or per-task rate, so this gap is real. It is not yet a statement about Prismata's residual risk.

**C4 does not survive as measured.**

- The 0.0% is guaranteed by the harness. The "task-scoped" envelope is exactly the annotated target, and the attacker's control is always a different element.
- The capability gate never decides anything in any arm. Only admitted elements are rendered addressable, so L3 ≡ L2.
- "More than label accuracy" is not supported. The label-error effect, +33.3 [15.0, 55.7], contains 43.4.
- The principle is least privilege, which is KNOWN, and Prismata's own gate is built on it.

## New evidence produced for this review (free, CPU only)

**How it was produced.** The script `c1p_attr.py` is in the appendix. It re-implements `gt_provenance` so that every rule that fires on a node is kept, in priority order. It then does three things:

- reproduces the unit-ladder numbers;
- attributes each exposed control to the seed rule responsible for it;
- recomputes the rates with families of rules removed.

It ran in 108 s after the JSON load, on the same frame: 1,163 pages, 145 tasks, 57 sites. It passed two checks:

- It gives the same label as `P.gt_provenance` on every 25th node, with 0 mismatches.
- V0 reproduces 9.19%, 38.09% [27.72, 49.05], 59.31% [47.18, 70.95], 7.71% and 40 sites exactly.

Its outputs went to the session scratchpad, not the repo.

**Table 1. Labeler sensitivity.** Site bootstrap, B = 10,000, seed 20260925.

| Labeler variant | Controls inside untrusted content | Pages exposed [95% CI] | Tasks exposed [95% CI] | Target untrusted or inside | Sites with any |
|---|---:|---|---|---:|---:|
| V0, as published | 9.19% | 38.09% [27.72, 49.05] | 59.31% [47.18, 70.95] | 7.71% | 40 |
| V1, no tokens from `data-*` values | 9.19% | 38.09% [27.72, 49.05] | 59.31% [47.18, 70.95] | 6.62% | 40 |
| V2, no Hosted (H) rule | 2.45% | 30.70% [20.61, 42.33] | 47.59% [35.14, 60.31] | 2.72% | 32 |
| V3, no generic UGC tokens (question, answer, qa, feedback) | 8.82% | 36.20% [26.03, 46.93] | 58.62% [46.48, 70.47] | 7.07% | 39 |
| V4, strict (V1 + V2 + V3) | 2.02% | 27.77% [18.00, 39.17] | 45.52% [33.09, 58.11] | 1.00% | 30 |
| V5, ads and cross-origin iframes only (class, id, src) | 1.22% | 24.33% [14.88, 35.55] | 39.31% [27.08, 52.32] | 0.54% | 25 |

**F1. The per-leaf rate is a labeler artifact.**
- There are 38,477 visible untrusted leaves, and 808 of them are critical (2.10%, as in the README).
- Every one of the 808 has only children that the labeler seeded as developer content (D).
- The children's rules, sampled up to five per page, are: `menu` 159, `footer` 52, `header` 21, `<nav>` 14, `role=search` 5, `<main>` 5 and `logo` 4.
- A leaf is an untrusted node with no untrusted element child. It can have an actionable descendant only through this override (`c1_robustness.py:144`, `:106-112`; `pipeline_v2.py:209-212`).

**F2. Aggregation with the criterion held fixed.**
- Pages with at least one critical leaf: 8.43%, 4.0x the per-leaf rate of 2.10%. Independent leaves would predict 16.37%, so critical instances cluster on the same pages.
- Per-page exposure (38.09%) is, by definition, the share of pages with at least one critical untrusted node, meaning a node with a non-hidden actionable strict descendant. The per-node rate is 15.83% over all units and 19.57% over visible units (c1 README:27). The page rate is therefore 1.9x to 2.4x the node rate.
- Against the per-region rate (G0: 38.50% to 52.56%), the page rate is 0.72x to 0.99x.

**F3. What drives exposure.** There are 443 exposed pages and about 19,170 exposed controls.
- **By control:**
  - Hosted: `storefront` 7,564 (39%), `listing` 4,681 (24%), `listings` 581, `sellers`/`seller` 643, `third-party` 284.
  - UGC: `answer` 701, `reviews` 592, `forum` 355.
  - Ad: `ad` 661, `adslot` 490, `sponsored` 479.
- **By page** (a page can count under several rules):
  - Ad: `ad` in a class 120, `ad` in an id 91, `ads` 45, `adslot` 39, `native-ad` 34.
  - Hosted: `listing` 56, `partner` 40, `storefront` 34.
  - UGC: `reviews` 46, `answer` 27.
- 86 of the 443 pages are exposed only through Hosted seeds.
- 67 of the 443 pages have a responsible seed that covers more than half of all DOM nodes; 88 have one covering more than 20%.

**F4. What the 7.71% target figure is made of.** It covers 85 of 1,103 steps, grouped here by the seed responsible.

| Seed (count) | Sites and targets | Judgement |
|---|---|---|
| Hosted `storefront` (34) | All Expedia: `div.Storefront-Homepage`, about 90% of the DOM. The targets are the whole first-party search form: "Flights", "One-way", "Leaving from", "Going to", "Search". | first-party |
| `ad` from a `data-*` value (12) | The target labels itself "external ad": the CVS "Shop" menu button, a Delta combobox input, the eBay search textbox, an AMC nav link, a CarGurus label. | first-party |
| Ad `adslot` (5) | An Expedia layout row covering about 57% of the DOM. The target is the sort `<select>`. | first-party |
| UGC `answer` (4) | eBay `s-answer-region`. The targets are "Best Match" and "Price + Shipping: lowest first". | first-party |
| Hosted `listing`/`listings` (20) | Booking "Choose your room" in hotel cards; eBay "All Filters" inside a `b-listing` section covering 70% of the DOM; Eventbrite organizer "Contact" and "Follow". | mixed |
| `forum` 2, `reviews` 2, `marketplace` 1, `sponsor` 1, `feedback` 3 | | plausible, unchecked |

At least 55 of the 85 (65%) are first-party controls in first-party containers. The `data-*` hits look like random collisions of the delimited token `ad` with UUID-like values. Two things point that way:
- 12 of 1,103 targets is about 1%, close to what UUIDs predict.
- Newegg's Osano dialog id, `64b5edb2-814d-4094-ad04-…`, matched the same way.

**F5. E-only exposure.** V5 flags 283 pages.
- Most of it is genuine advertising:
  - GPT slots with "Shop now" buttons on CVS
  - a Taboola feed on FoxSports
  - `adsbygoogle` on NYC
  - Amazon ad-topper cards
  - an eBay leaderboard
  - an ESPN ad slot
  - a KBB `google_ads_iframe`
  - Newegg sponsored brands
- Five sites supply 90 of the 283 pages through first-party seeds:
  - Expedia `uitk-view-row-theme-brand_promo` rows: 39 pages
  - AA `aa-hp-ad-hero`, the homepage hero: 21
  - United `homeTop__ad`, "Advertisement by United": 16
  - BoardGameGeek `game-description-with-ad`: 12, with 71 controls including "Edit"
  - Delta `adv-search`, which means advanced search: 2

Without those five sites the rate is 16.6%, so the E-only per-page rate lies between about 17% and 24%. These samples came from a second snippet that reuses the appendix functions with the V5 filter and prints up to two seeds per site.

**F6. Concentration.**
- Ten sites supply 219 of the 443 exposed pages (49%): expedia 39, booking 32, amazon 24, aa 21, ebay 21, ryanair 19, target 17, united 16, nyc 15, ticketcenter 15.
- The pooled rate is a ratio of sums, so sites with long trajectories count for more.

**Answers to the checks the task asked for.**
- **What does `gt_provenance` mark as untrusted?**
  - Ads are E. That covers class, id or `data-*` tokens such as `ad`, `ads`, `adv`, `gpt`, `dfp` and `sponsor(ed)`; ad-network hosts in any attribute; and cross-origin iframes.
  - Reviews and comments are U, and so are the generic tokens `question`, `answer`, `qa` and `feedback`.
  - Seller, merchant, vendor, marketplace, `storefront`, `listing(s)`, `partner` and `affiliate` are H.
  - Navigation is *trusted*. Nav, header, footer, main, menu, logo and `role=search` are seeded D, and they override an untrusted ancestor (`pipeline_v2.py:132-147`, `:187-213`).
  - Matching looks for delimiters inside tokens (`:124`), so `adv-search`, `aa-hp-ad-hero` and UUID segments like `-ad04-` all hit.
- **Would over-labeling inflate the per-page rate?** Yes, and not symmetrically.
  - The per-page statistic is an OR over every seed on the page, so a single false page-wrapper seed flips the whole page.
  - The per-leaf statistic is near zero by construction, whatever the labeler does.
  - So the "reproduction" cannot see labeler error, while the per-page headline absorbs all of it.

## C1': attack table

| # | Attack | Type | Evidence checked (file:line) | Verdict | Minimal fix |
|---|---|---|---|---|---|
| 1 | "Reproduces under its stated definition" rests on an artifact. All 808 critical leaves are critical only because the labeler relabels a nested menu, footer, header or nav as trusted. | Reproduction taken as validity | `scripts/c1_robustness.py:144` (G4 = untrusted node with no untrusted element child); `:135` and `:81-88` (strict descendants only); `:106-112` (seeds override inheritance); `src/pipeline_v2.py:209-212`; F1 (808/808) | **fatal** (for the reproduction sub-claim) | Delete "reproduces". Say that the per-leaf rate is zero by construction and that its non-zero part measures a labeler override. |
| 2 | "Prismata's 1.2% is a per-leaf rate" is not what Prismata says. Its instance is an untrusted node flagged by an LLM provenance model: 23.10 per Mind2Web page, against our 143.55 untrusted nodes per page. At every-node granularity our rate is 15.83% to 19.57%, which is 13 to 16 times the published figure. G4 was chosen as the "most conservative" cell, which means the unit that makes the rate smallest. | Construct; our view reported as theirs | Prismata §3 (WebFetch): "For every untrusted node, a second model reads the path from the root…" and "This yields 90,408 untrusted path instances"; the provenance model "flags each DOM node". c1 README:12, :26-27. Audit C1_C2_C10.md:80 ("does not define the granularity") | **fatal** (as a claim about Prismata) | Attribute the point to Prismata's own sentence: the non-critical instances "are leaves or text-only regions that cannot sit above a targetable element". Report the G4-to-G3 band (1.6% to 19.6%) and name the density of flagged nodes as the unknown. Ask the authors for their unit (task 1.1). |
| 3 | "18 to 28 times larger" changes two variables at once: the criterion and the unit of aggregation. | One arm, two variables | `scripts/unit_ladder.py:53-66` and `:115-117` (numerator: a page with a visible control that has an untrusted strict ancestor), against c1 README:26 (denominator: an untrusted leaf with a visible actionable descendant). F2, with the criterion fixed: 4.0x from leaf to page, 1.9x to 2.4x from node to page, 0.72x to 0.99x from region to page | **fatal** (for the headline ratio) | Drop the multiples. Report absolute levels per unit at one fixed criterion; give any ratio a CI and name its criterion. |
| 4 | Aggregation raises the rate trivially: P(at least one of n) ≥ p, and a task is an OR over about 8 pages. It bears on Prismata's argument only through per-page or per-task Case 3, which is not measured. | Construct; significance | Prismata (WebFetch) gives no per-page, per-task or per-action rate ("NOT FOUND"). Its residual is per path: 94 Case-3 paths, "0.10% of the full corpus" (§3). Frame: 1,163 pages over 145 tasks | **needs fix** | Estimate per-page and per-task Case-3 presence, either by rebuilding the cue annotator or by hand-coding cues on the exposed pages. Prismata's own counts cap per-page Case 3 at 94/2,832 = 3.32% of its Mind2Web DOMs. The per-task figure is the one that matters. |
| 5 | Exposure is sold as risk. Case 2 (on the path, with cues) is handled by Prismata's cue parsing; only Case 3 is residual. | Construct | `research/NOVELTY_LEDGER.md:33` (per-page rates set against the "about 0.10%" residual); unit-ladder README:15; Prismata Table 1 (Cases 1 to 3) | **needs fix** | Call it "gate decisions with untrusted content on the path", i.e. the Case 2 + 3 load. Remove the comparison with 0.10% until a Case-3 estimate exists. |
| 6 | The labeler over-labels. The 9.19% control figure and the 7.71% target figure are mostly false positives. | Labeler validity; our view reported as theirs | `src/pipeline_v2.py:132-135` (UGC: question, answer, qa, feedback); `:136-138` (Hosted: storefront, listing(s), partner, vendor); `:139-142` (ad, adv, gpt, dfp); `:119-121` (tokens from `data-*` values); `:124` (delimited substring match). `scripts/unit_ladder.py:72`: the target counts if it is itself untrusted or inside, while the controls count only when strictly inside. Table 1; F3; F4 | **fatal** (for 9.19% and 7.71% as stated) | Fix the rules: drop `storefront`, `answer` and `adv`; allow no substring hits in ids or `data-*` values; allow no seed that wraps more than 20% of the DOM. Report a labeler-sensitivity band and human-measured precision (task 2.1). |
| 7 | Per-page and per-task exposure hold up, at lower levels, under stricter labelers. | Labeler validity | Table 1, V2 to V5; F5 (90 of the 283 E-only pages come from first-party promotions) | **survives, reduced**: about 17% to 31% of pages and 39% to 48% of tasks, on heuristic labels | Quote the band, not 38% and 59%. Call the labels heuristic and add audited precision. |
| 8 | The comparison with Prismata's per-page cap uses a pooled denominator. Our 38.09% sits at Prismata's absolute ceiling for Mind2Web, which suggests our labeler flags far more than theirs does. | Arithmetic; construct | `scripts/unit_ladder.py:137-141`; unit-ladder README:30 (1,086/5,664 = 19.17%); ledger:33; Prismata §3 (5,664 DOMs "split evenly", so 2,832 from Mind2Web) | **needs fix** | For Mind2Web, use caps of 38.35% (1,086/2,832) for any critical path and 3.32% (94/2,832) for Case 3, and say what it means that we reach the first. |
| 9 | The ledger says "1.58% to 2.10%, below the 1.66% ceiling", but 2.10% is above the ceiling. | Accuracy | `research/NOVELTY_LEDGER.md:20`; c1 README:26 | **needs fix** | Correct the sentence. It becomes moot once row 1 is applied. |
| 10 | Statistics: intervals and weighting | Statistics | `scripts/unit_ladder.py:80-87`: only the page and task rates get a site bootstrap. The control, target and per-leaf rates and the multiples have no CI. The pooled estimate is a ratio of sums, and ten sites give 49% of exposed pages (F6). `PER_SITE = 3` (`c1_robustness.py:24`) gives 2.5 tasks per site. The frame is a convenience sample: the first three trajectories per site in train shards 0, 1 and 10 (`c1_robustness.py:23`, `:167`). | **needs fix** | Give site-cluster CIs for every rate and ratio. Report site-macro averages next to the pooled ones, add a leave-one-site-out check, and name the frame. |
| 11 | The pre-registration cannot be checked, and its rule could not fail. | Process | Both `config.yaml` files have `prereg_commit: ""`, and the working tree has no git history. The 10x rule (unit-ladder README:14) was written after region rates of 33% to 53% were already known (c1 README:34). | **needs fix** | Commit before running. Call C1' exploratory, and say that the threshold was set after the region rates were seen. |
| 12 | Prior art and novelty: Prismata already explains why its number is small, and C1' has had no novelty audit of its own. | Prior art | c1 README:34 quotes Prismata's sentence about leaves. Ledger:36-37 lists only Prismata, Carlini et al. and Pith. The audits cover C1, C2, C10 and C3 to C5, not C1'. Web-measurement work on how often third-party or ad content appears per page was not searched. | **needs fix** | Run a novelty audit of C1' that includes web-measurement prevalence studies. Claim only the per-page, per-task and per-step measurement for DOM gates. |

## C4: attack table

| # | Attack | Type | Evidence checked (file:line) | Verdict | Minimal fix |
|---|---|---|---|---|---|
| 1 | The task-scoped 0.0% holds by construction. The envelope is exactly the target, and the attacker's control is drawn from non-target elements. | Tautology | `scripts/ablation_v2.py:79` (`narrow` returns `{id(tgt)}`); `:61-62` (attacker candidates exclude the target id); `:65` (`a2 = dmg[0]`) | **fatal** | Report the narrow cell as a sanity check only. Use an envelope whose width is not defined by the answer. |
| 2 | "Task-scoped" is an oracle, the annotated Mind2Web target, not Prismata's LLM gate. It is the same oracle the ledger withdrew for C2. | Our view reported as theirs; oracle | `scripts/ablation_v2.py:79`; ledger:21 and :45; Prismata §2.2 (an LLM judges each critical path) and §5.3 ("every evaluated model exceeds 93% precision and 87% F1"; recall as low as 82.69%) | **fatal** (for any statement about task-scoped defenses) | Use the LLM-chosen envelope (ROADMAP 3.4) and a target-free width sweep, and report the width actually realized. |
| 3 | The gate never decides. Only admitted (RW) controls are rendered addressable, and the controller picks only addressable lines, so L3 ≡ L2 in every arm. The width arm changes rendering and gating together, and all of its effect happens at rendering. | One arm, two variables | `src/pipeline_v2.py:275-276` (`[id=…]` only when RW), `:304`, `:313-316`, `:319-324`; `scripts/ablation_v2.py:101-106`; `results/ablation_v2.log:35` (L2 = L3 = L4 = 43.4%) | **fatal** (for "width governs" read as a property of the gate) | Decouple the two: render every control addressable and vary only the gate, or the reverse. Report L2 and L3 separately so that the gate can bind. |
| 4 | The harness sets exposure. P_correct declares the injected region task-relevant, so a U or H region is shown and an E region is pruned. The page-wide arm is therefore "no action gate, injected region shown", which is neither Prismata (it has a gate) nor UCM (it masks untrusted content). | Construct; our view reported as theirs | `scripts/ablation_v2.py:85-86` (`inj_ids` passed as `task_relevant_untrusted`); `:54-58` (the largest untrusted region is the one injected); `src/pipeline_v2.py:240-242` | **needs fix** | Say this, and vary the task-relevance assumption. |
| 5 | The worst-case controller makes "influence" equal to "admitted and visible". | Tautology | `src/pipeline_v2.py:306-317`; ledger:58; audit C3_C4_C5.md:116 | **needs fix** | Call 43.4% "the pages where the named damaging control is visible and admitted", an upper bound. Add real agents with an adaptive attacker (ledger:59). |
| 6 | "More than label accuracy" is not supported. +33.3 [15.0, 55.7] contains 43.4, and the two doses cannot be compared: one control against every developer control, versus one flipped region. | Statistics; design | ledger:57; audit C3_C4_C5.md:112 | **fatal** (for the comparative wording) | Run a formal interaction contrast on a common scale, for example per admitted element, with site-cluster CIs. Otherwise say "both matter". |
| 7 | It is not a dose-response. There are two envelope values, and the K sweep measures criticality, is ranked by an oracle, and rises with K by construction. | Design | `scripts/ablation_v2.py:129` (`narrow`, `page`); ledger:57 | **needs fix** | Sweep width with a deployable gate and measure influence at each width (ROADMAP 3.4). |
| 8 | "Correct labels" means our heuristic, with the false positives shown above. Those false positives also decide where the injection goes. | Labeler validity | `scripts/ablation_v2.py:44-53`, `:58`; F3 and F4 above | **needs fix** | Rerun with the strict labeler or on human-validated regions, and rename `gt_provenance`. |
| 9 | Clustering and sensitivity | Statistics | n = 159 pages (log:35). Up to 6 steps per trajectory (`ablation_v2.py:123`), with the same `dmg[0]` control each time. No site-cluster CI. The figure went from 19.5% to 43.4% with a "broader damaging-control set" (`research/CORRECTIONS.md:13`), which depends on `DAMAGING_RX` (`ablation_v2.py:28-30`). | **needs fix** | Give site-cluster CIs, test sensitivity to `DAMAGING_RX`, and use one page per trajectory as a robustness check. |
| 10 | Prior art | Prior art | Audit C3_C4_C5.md:75-95: Saltzer and Schroeder 1975; Progent's "too broad … too narrow"; the AgentDojo tool filter. Prismata's own rationale: "confines the attacker's goal by gating the agent's allowed actions to the task scope" and "Low precision indicates over-permissiveness". | **needs fix** (downgrade) | Treat C4 as INCREMENTAL until rows 1 to 3 are fixed. It becomes NOVEL AS MEASUREMENT only with a real width dose-response under a deployable gate and real agents. |

**This project's three recurring failure patterns, as they appear here.**
- One arm changing two variables: C1' row 3 and C4 row 3.
- Our own view reported as the other system's input: C1' rows 2 and 6, and C4 rows 2 and 4.
- Reproduction taken as validity: C1' row 1. The exact V0 reproduction in this review validates the code, not the construct.

## (1) The most damaging sentence a reviewer could write

- **C1':** "The '18 to 28 times larger' exposure divides a per-page count by a per-leaf rate that exists only because the authors' own class-name heuristic relabels nested menus and footers as trusted (808 of 808 'critical leaves'), and the per-target figure is mostly Expedia's own homepage wrapper classed as third-party 'storefront' content; the headline compares two artifacts of their labeler, not Prismata's statistic."
- **C4:** "The 'task-scoped' envelope is the single annotated target, the attacker is always given a different element, and the gate never decides anything because only admitted controls are rendered, so '43.4% vs 0.0%' measures how often a 'Sign out' link is visible to a controller that obeys every injection, a property of the harness and not of envelope width, and it is statistically indistinguishable from the label-error effect it claims to dominate (+33.3 [15.0, 55.7])."

## (2) Can C1' be a primary contribution of a TMLR paper?

Not as it stands. TMLR judges whether claims are correct and well supported and whether some readers care about them; it does not judge novelty. A *corrected* C1' could therefore anchor a short measurement paper, but four things must come first.

1. **Delete the ratio and the reproduction.** Report the rate per node, control, page, task and step at one fixed criterion. Give site-cluster CIs, site-macro averages and a leave-one-site-out check.
2. **Validate the labels.**
   - Get human labels on a site-stratified sample (task 2.1).
   - Fix the known false positives: storefront, answer, adv, UUID and wrapper seeds.
   - Publish a labeler-sensitivity band covering the strict heuristic, E-only, a Prismata-style LLM labeler, and human labels.
3. **Tie it to Prismata's argument.** Estimate per-page and per-task *Case-3* presence, either by rebuilding the cue annotator or by hand-coding cues on the exposed sample. That is the per-page quantity the residual-risk argument depends on, and Prismata does not report it.
4. **Match the unit.** Obtain or emulate the density of Prismata's flagged nodes (task 1.1), and commit the pre-registration before running.

Even with all four, C1' reads better as the measurement section of a paper whose headline is residual risk with real agents.

## (3) The one cheapest analysis (no API spend) that would most strengthen or kill C1'

The rule-level labeler ablation above cost 2 minutes of CPU. It already kills the ratio, the reproduction and the target figure. What remains open is whether the per-page and per-task levels are real.

The decisive next step is a **blinded, site-stratified hand audit of the seeds responsible for exposure**:
- Scope: about 100 exposed pages, one seed each, at most 3 per site, taken from the F3/F4 attribution.
- Cost: about 3 hours, and nothing in API spend.
- For each seed, record whether it is third-party, user or hosted content, and whether the exposed control is first-party UI.
- It gives the labeler's precision on exposure-driving seeds, and corrected per-page and per-task rates with site CIs.
- Pre-register the kill rule before looking. For example: keep C1' only if the lower bound of the audited per-task rate stays above 25%.

A zero-compute step to take first: restate the result at a fixed criterion, per node 15.83% against per page 38.09%, a factor of about 2.4.

## Caveats

- Prismata quotes come through WebFetch's extraction model and must be checked in the PDF. This matters most for "For every untrusted node…", Table 1 (the Cases) and §5.3.
- My false-positive judgements rest on class and id strings and on control text, not on rendered pages. A human should confirm each one.
- The "L3 ≡ L2" point is derived from the code. I did not rerun `ablation_v2.py`.
- The analysis outputs are in the session scratchpad and will not persist. The script is reproduced below. It imports the repo's `pipeline_v2` and `c1_robustness` modules unchanged. Run it with the output path as its only argument.

## Appendix: `c1p_attr.py`

```python
import sys, json, collections, gc, time, re
from pathlib import Path
import numpy as np
ROOT = Path('/home/claude/work/repo')
sys.path.insert(0, str(ROOT/'src')); sys.path.insert(0, str(ROOT/'scripts'))
import pipeline_v2 as P
import c1_robustness as C
from lxml import html as LH
OUT = Path(sys.argv[1])
def comb(p):
    p = sorted(p, key=len, reverse=True)
    return re.compile(r'(?:^|[-.])(' + '|'.join(re.escape(x) for x in p) + r')(?:$|[-.0-9])')
GEN = {'question','answer','qa','feedback'}
EXT = comb([p for p,_ in P.EXTERNAL]); UCORE = comb([p for p,_ in P.UGC if p not in GEN]); UGEN = comb(sorted(GEN))
HOST = comb([p for p,_ in P.HOSTED]); DEV = comb([p for p,_ in P.DEV])
def candidates(el, host):
    tag = el.tag.lower() if isinstance(el.tag, str) else ''
    c = []
    if tag in ('iframe','embed','object'):
        src = P.gattr(el,'src') or P.gattr(el,'data_src') or el.get('data') or ''
        if P.AD_HOST.search(src): c.append(('E','iframe:adnetwork','src'))
        elif P._frame_origin(src, host) == 'cross': c.append(('E','iframe:crossorigin','src'))
    toks = [(t,'class') for t in P.class_tokens(el)]
    i = (el.get('id') or '').lower()
    if i: toks.append((i,'id'))
    for k,v in el.attrib.items():
        if (k.startswith('data_') or k.startswith('data-')) and isinstance(v,str) and len(v) < 60:
            toks.append((v.lower(),'data:'+k))
    for t,s in toks:
        m = EXT.search(t)
        if m: c.append(('E','ad:'+m.group(1),s))
    for k,v in el.attrib.items():
        if isinstance(v,str) and P.AD_HOST.search(v): c.append(('E','attr:adnetwork','attr:'+k)); break
    for t,s in toks:
        m = UCORE.search(t)
        if m: c.append(('U','ugc:'+m.group(1),s))
        m = UGEN.search(t)
        if m: c.append(('U','ugcgen:'+m.group(1),s))
    for t,s in toks:
        m = HOST.search(t)
        if m: c.append(('H','hosted:'+m.group(1),s))
    if tag in P.DEV_TAGS: c.append(('D','tag:'+tag,'tag'))
    role = (P.gattr(el,'role') or '').lower()
    if role in P.DEV_ROLES: c.append(('D','role:'+role,'role'))
    for t,s in toks:
        m = DEV.search(t)
        if m: c.append(('D','dev:'+m.group(1),s)); break
    return c
VARS = {
 'V0_base': lambda c: True,
 'V1_no_data_attr_tokens': lambda c: not c[2].startswith('data:'),
 'V2_no_hosted_H': lambda c: c[0] != 'H',
 'V3_no_generic_ugc(question/answer/qa/feedback)': lambda c: not c[1].startswith('ugcgen:'),
 'V4_strict(V1+V2+V3)': lambda c: (not c[2].startswith('data:')) and c[0] != 'H' and not c[1].startswith('ugcgen:'),
 'V5_E_only(ads+crossorigin iframes, class/id/src)': lambda c: c[0] in ('E','D') and not c[2].startswith('data:'),
}
def key(c): return f"{c[0]}|{c[1]}|{c[2].split(':')[0]}"
def analyse(raw, site, tid):
    try: tree = LH.fromstring(raw)
    except Exception: return None
    P.deep_parse(tree)
    nodes = tree.xpath('//*')
    if not nodes: return None
    host = P.host_for(site); n = len(nodes)
    cand = [candidates(el, host) for el in nodes]
    mism = 0
    for k in range(0, n, 25):
        lab,_ = P.gt_provenance(nodes[k], host)
        if lab != (cand[k][0][0] if cand[k] else None): mism += 1
    idx = {id(el): k for k, el in enumerate(nodes)}
    par = []
    for el in nodes:
        p = el.getparent(); par.append(idx.get(id(p), -1) if p is not None else -1)
    byid, lt = {}, set()
    for el in nodes:
        v = el.get('id')
        if v: byid.setdefault(v, el)
    for el in nodes:
        if C.tag(el) == 'label':
            f = P.gattr(el, 'for')
            if f and f in byid: lt.add(id(byid[f]))
    vis = [C.visible(el) for el in nodes]
    act = [vis[k] and bool(C.clause_attr(nodes[k], lt)) for k in range(n)]
    tk = -1
    if tid:
        for k, el in enumerate(nodes):
            if el.get('backend_node_id') == tid: tk = k; break
    kids = [[] for _ in range(n)]; size = [1]*n; had = [False]*n
    for k in range(n):
        if par[k] >= 0: kids[par[k]].append(k)
    for k in range(n-1, -1, -1):
        p = par[k]
        if p >= 0:
            size[p] += size[k]
            if act[k] or had[k]: had[p] = True
    out = {'mism': mism, 'n': n, 'v': {}}
    for vn, keep in VARS.items():
        sr = [None]*n
        for k in range(n):
            for cc in cand[k]:
                if keep(cc): sr[k] = cc; break
        src = [-1]*n; prov = ['D']*n
        for k in range(n):
            if sr[k] is not None: src[k] = k; prov[k] = sr[k][0]
            elif par[k] >= 0: src[k] = src[par[k]]; prov[k] = prov[par[k]]
        nu = [-1]*n
        for k in range(n):
            p = par[k]
            if p >= 0: nu[k] = src[p] if prov[p] != 'D' else nu[p]
        inside = [k for k in range(n) if act[k] and nu[k] >= 0]
        tf = None
        if tk >= 0: tf = prov[tk] != 'D' or nu[tk] >= 0
        rec = {'n_act': sum(act), 'inside': len(inside), 'target': tf}
        if vn == 'V0_base':
            rs = set(nu[k] for k in inside)
            rec['page_keys'] = sorted(set(key(sr[s]) for s in rs))
            rec['elem_keys'] = dict(collections.Counter(key(sr[nu[k]]) for k in inside))
            rec['data_attrs'] = sorted(set(sr[s][2] for s in rs if sr[s][2].startswith('data:')))
            rec['maxcov'] = max([size[s]/n for s in rs], default=0.0)
            rec['maxcov_tag'] = C.tag(nodes[max(rs, key=lambda s: size[s])]) if rs else None
            unt = [prov[k] != 'D' for k in range(n)]
            leaf = [unt[k] and not any(unt[c] for c in kids[k]) for k in range(n)]
            vl = [k for k in range(n) if leaf[k] and vis[k]]
            crit = [k for k in vl if had[k]]
            rec['g4'] = dict(vis_leaves=len(vl), crit=len(crit), crit_allkids_D=sum(1 for k in crit if kids[k] and all(sr[c] is not None and sr[c][0]=='D' for c in kids[k])),
                             crit_tags=[C.tag(nodes[k]) for k in crit][:5], crit_child_rules=[sr[kids[k][0]][1] for k in crit if kids[k] and sr[kids[k][0]] is not None][:5])
            if tf:
                s = src[tk] if prov[tk] != 'D' else nu[tk]; se = nodes[s]
                rec['tinfo'] = dict(key=key(sr[s]), seed_tag=C.tag(se), seed_ci=((se.get('class') or '')[:40] + '#' + (se.get('id') or '')[:20]),
                                    cov=round(size[s]/n, 3), t_tag=C.tag(nodes[tk]), t_text=' '.join(' '.join(nodes[tk].itertext()).split())[:50])
        out['v'][vn] = rec
    return out
def site_ci(d, seed=20260925, b=10000):
    s = sorted(d); sums = np.array([sum(d[x]) for x in s], float); cn = np.array([len(d[x]) for x in s], float)
    ix = np.random.default_rng(seed).integers(0, len(s), size=(b, len(s))); m = sums[ix].sum(1)/cn[ix].sum(1)
    return [round(100*float(np.percentile(m, 2.5)), 2), round(100*float(np.percentile(m, 97.5)), 2)]
bys = collections.defaultdict(list)
for f in C.FILES:
    for t in json.load(open(f)): bys[t['website']].append(t)
    gc.collect()
sel = [x for s in sorted(bys) for x in sorted(bys[s], key=lambda t: t['annotation_id'])[:C.PER_SITE]]
del bys; gc.collect()
rows, t0 = [], time.time()
for i, t in enumerate(sel):
    for st, a in enumerate(t['actions']):
        r = analyse(a['raw_html'], t['website'], P.target_id(a))
        if r: r.update(site=t['website'], task=t['annotation_id'], step=st); rows.append(r)
    if (i+1) % 25 == 0: print(f'[{i+1}/{len(sel)}] {len(rows)} {time.time()-t0:.0f}s', flush=True)
res = {'pages': len(rows), 'mismatch_vs_gt_provenance_sampled': sum(r['mism'] for r in rows), 'variants': {}}
for vn in VARS:
    pbs, tf = collections.defaultdict(list), {}
    for r in rows:
        e = r['v'][vn]['inside'] > 0; pbs[r['site']].append(e); tf[(r['site'], r['task'])] = tf.get((r['site'], r['task']), False) or e
    tbs = collections.defaultdict(list)
    for (s,_), f in tf.items(): tbs[s].append(f)
    tg = [r['v'][vn]['target'] for r in rows if r['v'][vn]['target'] is not None]
    na = sum(r['v'][vn]['n_act'] for r in rows); ins = sum(r['v'][vn]['inside'] for r in rows)
    res['variants'][vn] = dict(elem_pct=round(100*ins/na, 2), page_pct=round(100*sum(sum(v) for v in pbs.values())/len(rows), 2), page_ci=site_ci(pbs),
        task_pct=round(100*sum(tf.values())/len(tf), 2), task_ci=site_ci(tbs), target_pct=round(100*sum(tg)/len(tg), 2), target_n=len(tg), sites_any=sum(1 for v in pbs.values() if any(v)))
V0 = [r['v']['V0_base'] for r in rows]; ex = [(r, v) for r, v in zip(rows, V0) if v['inside'] > 0]
pk = collections.Counter(k for _, v in ex for k in v['page_keys'])
ek = collections.Counter()
for _, v in ex: ek.update(v['elem_keys'])
g4v = sum(v['g4']['vis_leaves'] for v in V0); g4c = sum(v['g4']['crit'] for v in V0); g4d = sum(v['g4']['crit_allkids_D'] for v in V0)
p = g4c/g4v
res['V0_detail'] = dict(exposed_pages=len(ex), page_keys_top=pk.most_common(20), elem_keys_top=ek.most_common(15),
    data_attr_names=collections.Counter(a for _, v in ex for a in v['data_attrs']).most_common(8),
    pages_only_H=sum(1 for _, v in ex if all(k.startswith('H|') for k in v['page_keys'])),
    pages_only_data_tokens=sum(1 for _, v in ex if all(k.endswith('|data') for k in v['page_keys'])),
    exposed_pages_maxcov_gt50=sum(1 for _, v in ex if v['maxcov'] > 0.5), exposed_pages_maxcov_gt20=sum(1 for _, v in ex if v['maxcov'] > 0.2),
    maxcov_tags=collections.Counter(v['maxcov_tag'] for _, v in ex).most_common(8),
    g4_vis_leaves=g4v, g4_crit=g4c, g4_crit_pct=round(100*p, 2), g4_crit_with_all_children_seeded_D=g4d,
    g4_crit_child_rules=collections.Counter(x for v in V0 for x in v['g4']['crit_child_rules']).most_common(8),
    g4_crit_tags=collections.Counter(x for v in V0 for x in v['g4']['crit_tags']).most_common(8),
    page_with_crit_leaf_pct=round(100*sum(1 for v in V0 if v['g4']['crit'] > 0)/len(V0), 2),
    indep_pred_page_pct=round(100*float(np.mean([1-(1-p)**v['g4']['vis_leaves'] for v in V0])), 2),
    site_exposed_pages=sorted(collections.Counter(r['site'] for r, _ in ex).items(), key=lambda x: -x[1])[:10],
    target_examples=[dict(site=r['site'], step=r['step'], **v['tinfo']) for r, v in zip(rows, V0) if v.get('tinfo')][:40],
    target_keys=collections.Counter(v['tinfo']['key'] for v in V0 if v.get('tinfo')).most_common(12))
json.dump(res, open(OUT, 'w'), indent=1, default=str)
print('DONE', time.time()-t0)
```

