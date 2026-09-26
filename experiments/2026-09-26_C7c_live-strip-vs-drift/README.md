# C7c: archive stripping versus site drift, on live Booking pages

## Pre-registration (26 Sep 2026, saved to the claude.ai project before the first page load)

The repo could not be pushed from this session, so the timestamp for this pre-registration is the project doc `claude/Idea3_Prereg_C7c_26Sep.md`, written before `scripts/live_strip_test.py capture` ran.

- **Question.** On 131 archived Mind2Web Booking pages, 24 of UCM's 25 hand selectors and all 68 matching LLM selectors match nothing (K22). Two causes are confounded: the archive strips every site `data-*` attribute (K21), and Booking's class names changed between the 2023 archive and UCM's captures. This test holds the page fixed and varies only the stripping.
- **Claims tested.** NOVELTY_LEDGER C7 (archive fidelity) and C8 (selector decay); CLAIMS_LEDGER K22, K23; new row K25.
- **Design.** Capture UCM's three Booking pages (homepage; search for Paris; the Pullman Paris Tour Eiffel hotel page) once, live, with headless Chromium (Playwright, en-US, 1366x768). UCM's URLs carry a 1 Jul 2025 check-in, which is now past, so check-in and check-out move to 10 and 12 Nov 2026. Wait for network idle (45 s cap), then for UCM's own content selector (15 s cap), then 5 s. Serialize the DOM. Build a second copy of each page that keeps only the 21 attribute names the Mind2Web archive keeps, after renaming `-` to `_` as the archive does. Apply every UCM Booking selector (25 hand, 70 LLM, UCM commit acff2e4) to both copies with lxml's CSS engine, as written and in underscore form.
- **Primary outcome.** Among the selectors that match at least one node on the live DOM, the share that match nothing on the stripped copy of the same DOM, for hand selectors and pooled.
- **Secondary outcomes.** How many of the 25 hand selectors still match any live page today (all 25 matched on UCM's captures): a first decay measurement for C8. How many of the 23 hashed class tokens occur on today's pages.
- **Decision rule.**
  - At least 80% of live-matching selectors disabled by stripping: stripping alone suffices, so the archive result (K22) does not need drift to explain it. C7 keeps its Booking demonstration as an archive effect.
  - Under 50%: stripping does not suffice. The K22 result owes much to drift, and C7's Booking evidence moves to C8.
  - 50% to 80%: both causes act; report both shares.
  - Fewer than 5 hand selectors match live: the hand result is undetermined; use the pooled result if at least 10 selectors match live, else report only the decay counts.
  - Capture blocked (no page with UCM's content selector): no result. Record it and move the capture to Colab (task 2.7).
- **Construct check.** Same page, same moment, same CSS engine: only the attribute set differs, so drift is held fixed. This tests whether the published selectors survive archiving. It does not test UCM itself on archives: UCM generates selectors from the page it sees, so on an archived page its LLM would write different selectors. Whether those work is task 2.8.
- **Load and ethics.** Three page loads, no login, no clicks, no form input. Captured DOMs stay in `data/` (not committed); results record their size and SHA-256. Scripts print counts only.
- **Models and budget.** None; $0.

## Results

Run 26 Sep 2026, 12:47 to 12:48 UTC, UCM commit acff2e4. Output: `results/live_strip_test.json` (captured DOMs in `data/live/booking/`, not committed; sizes and SHA-256 in the result file). No selector failed to parse.

**Capture.** Two of the three pages loaded; the homepage did not.
- Homepage: HTTP 403, a 1 KB block page, no content.
- Search: the URL redirected to Booking's Paris city page (`/city/fr/paris.html`, HTTP 202, 1.0 MB, 340 elements with `data-testid`). UCM's content selector did not appear, and this is a different page type from UCM's search results.
- Hotel: the URL redirected to `/hotel/fr/tour-eiffel.html` (HTTP 200, 2.3 MB, 369 elements with `data-testid`), and UCM's content selector appeared.

**Primary outcome: stripping alone disables the selectors.**

| Selectors | Match the live DOM | Of those, match nothing after stripping | Share disabled |
| --- | ---: | ---: | ---: |
| Hand (25) | 13 | 11 | 84.6% |
| LLM (70, not also hand-written) | 44 | 42 | 95.5% |
| Pooled (95) | 57 | 53 | 93.0% |

Four selectors survive stripping. `div[aria-label='Certification name']` survives because the archive keeps `aria-label` as `aria_label`. The other three rest on classes the archive keeps: `h2.pp-header__title`, `h2.ddb12f4f86.pp-header__title`, and `section[id='questions-answers-desktop'] .aa225776f2.ca9d921c46.f6707cac49`. Of the 57 live-matching selectors, 52 use a `data-*` attribute.

**Decision rule outcome: stripping alone suffices** (hand 84.6%, at least 80% with 13 selectors matching live; pooled 93.0%). The K22 archive result does not need drift to explain it.

**Secondary outcomes.**
- Hashed class tokens: 16 of the 23 in UCM's Booking selectors occur on today's pages, against 0 of 23 in the 2023 archive. Booking's class names changed between the archive and UCM's capture, and most have lasted from UCM's capture to today.
- Decay (exploratory; the homepage and search captures failed, so only the hotel page compares like with like). Of the hand selectors that matched UCM's hotel capture, 13 of 16 match today's hotel page. For LLM selectors from UCM's hotel runs, it is 46 of 60, or 43 of 57 without the 3 that duplicate hand selectors. UCM does not record its capture date: its URLs carry a 1 Jul 2025 check-in, and its repo starts on 7 Jul 2026. So this is 19% to 25% breakage over an unknown interval, one page, one site.

**Reading.** On the same DOM at the same moment, the archive's attribute whitelist disables 53 of the 57 UCM Booking selectors that work live. Anyone who reuses published or live-generated selectors on Mind2Web-style archives masks almost nothing on Booking. This does not show that UCM fails on archives. UCM writes its selectors from the page it sees, so on an archived page it would have to build them from class names. On Booking those class names are hashed and changed between 2023 and UCM's capture. Whether selectors written that way work, and whether they transfer to live pages, is task 2.8.

## Deviations

- The pre-registration timestamp is a project doc, not a pushed commit (the repo was unreachable).
- The homepage capture was blocked (HTTP 403). The search URL redirected to a city landing page. Both were kept in the analysis as captured: the blocked page matches nothing, and the city page is still Booking's live DOM, so neither biases the same-DOM comparison. They do limit the decay count, which is why decay is reported for the hotel page only.
- The per-page decay comparison against UCM's result files was added after seeing the capture outcome; it is exploratory.
