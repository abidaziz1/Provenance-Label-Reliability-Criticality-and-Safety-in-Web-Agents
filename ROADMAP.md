# Roadmap

The living task tracker. Update the Status column in the same commit as the work. The frozen source is `docs/context/01_Submission_Roadmap.md` (24 Sep 2026). Changes since that snapshot: Phase 0 (setup and the novelty audit) is new, task 1.5 was done at handoff, tasks 1.13 to 1.16 are new, and owners are remapped for Claude Code. Where the snapshot says "my sandbox", it means the Cowork sandbox of 24 Sep, not this environment; `scripts/preflight.py` says what this environment can reach.

**Targets.** TMLR by 19 Feb 2027 (primary). IEEE TDSC by 19 Mar 2027 only if Phase 4 works (stretch). ACM DTRAP (floor).

**Owner codes.** `C` Claude, nothing needed. `C+K` Claude, needs the named key in the environment. `A` Alam. `A+T` Alam and his team. `A/Colab` Alam runs a notebook in Colab. "C drafts, A sends" means Claude prepares everything and Alam does the one step tied to his identity.

**Status values.** `todo`, `doing`, `blocked (#issue)`, `done (commit)`, `dropped (reason)`.

## Phase 0: setup and the contribution (Sep 28 to Oct 11)

The novelty audit runs first because it decides what every later task is for. Phase 1 runs alongside it.

| ID | Task | Owner | Needs | Output, and what it decides | Budget | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 0.1 | Run `python3 scripts/preflight.py`; put the table in STATUS.md. Create the `needs-human` label. Confirm you can open an issue and a PR (gh, or the REST fallback in the skills). | C | nothing | What this environment can reach: each API, Docker, GitHub, disk. | $0 | doing: preflight ran 26 Sep (table in STATUS.md); issues and PRs cannot be opened from the Cowork session (GitHub API refused) |
| 0.2 | Baseline reproduction: fetch the 3 shards, run the tests, rerun `scripts/reconcile.py` and `scripts/descendant_only.py` (they rewrite their files in `results/`), then `git status`: no change means byte-identical. If anything changed, restore it with `git checkout -- results/`, record the difference in an experiment folder, and flag it. Confirm the `v2.0-baseline` tag exists. | C | nothing | The move into this repo broke nothing, and K1 to K5 re-derive from raw data. At handoff on 25 Sep `descendant_only.py` was byte-identical. | $0 | done 26 Sep: `reconcile.py` and `descendant_only.py` byte-identical at 9b8c760 (`v2.0-baseline`) |
| N0.1 | Evidence inventory for candidates C1 to C10 in `research/NOVELTY_LEDGER.md`: evidence file, script, test and construct check for each; mark it measured, pending or none. | C | nothing | A ledger in which every "measured" row reruns from a commit. | $0 | done (tests for K1 to K12 and K16 to K26 in `tests/test_claims.py`) |
| N0.2 | Prior-art audit of each candidate with the `novelty-auditor` subagent. Classic security work counts: least privilege, the confinement problem, information flow, N-version programming. So does 2024 to 2026 agent-defense work. | C | nothing | A verdict per candidate: NOVEL, NOVEL AS MEASUREMENT, INCREMENTAL or KNOWN. | $0 | done 25 Sep (`research/audit/`) |
| N0.3 | Adversarial review of each surviving claim with the `adversarial-reviewer` subagent. | C | nothing | The most damaging reviewer sentence per claim, and its fix. | $0 | done 25 Sep; labeler-sensitivity script committed as N0.3b, rerun pending |
| N0.4 | Triage the 25 Sep external review ideas in `research/BACKLOG_IDEAS.md` against N0.2 and N0.3: promote, merge into a candidate, or park, each with a reason. | C | nothing | No idea enters the plan without a verdict and an evidence path. | $0 | done 26 Sep (draft decisions in `research/BACKLOG_IDEAS.md`) |
| N0.5 | Draft `research/CONTRIBUTION_STATEMENT.md`: 2 or 3 primary contributions, one sentence each, each tied to evidence and a falsification test; 3 title options; each roadmap task mapped to the contribution it feeds, and tasks that feed none marked for dropping. Open the Gate N issue. | C drafts, A approves | your approval | Gate N. Phase 3 spend waits for it. | $0 | doing: draft ready 26 Sep; waits for your approval at Gate N |
| N0.6 | Re-audit after Gate 1 (Nov 8), after Gate 2 (Dec 6) and before task 5.3. Update the statement; log each change in `research/DECISIONS.md`. | C | nothing | The claims keep matching the evidence. | $0 | todo |

## Phase 1: lock down and de-risk (Sep 28 to Oct 11)

| ID | Task | Owner | Needs | Output, and what it decides | Budget | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 1.1 | Email Prismata's authors: which definition produced the 1.2%, and may we have their labeler output on a shared page set. Draft in `outreach/1.1_prismata.md`. | C drafts, A sends | your email account | Reply in 2 to 4 weeks. Task-target path: contribution C1 is clean. Any actionable descendant: 49.93% vs 1.2% is a real conflict their labels settle. | $0 | doing: draft ready 26 Sep (`outreach/1.1_prismata.md`); you send |
| 1.2 | Email UCM's authors: which model and commit reproduce their tables. Draft in `outreach/1.2_ucm.md`. | C drafts, A sends | your email account | Their model and commit for Gate 1, and the disclosure record reviewers ask for. | $0 | doing: draft ready 26 Sep (`outreach/1.2_ucm.md`); you send |
| 1.3 | Fix notebook 02 v2: its power cell sizes the secondary criticality ratio, not the coupling statistic. Add the coupling power table and a go/no-go cell. | C | nothing | The notebook stops before spending when the pilot error rate makes coupling unmeasurable. | $0 | done 26 Sep (recovery PR): coupling power cell and go/no-go |
| 1.4 | Model IDs in all three notebooks: Claude Sonnet 5 and GPT-5.6 Terra for our runs, UCM's own model for its reproduction. Log the model ID beside every result. Add missing prices to `src/llm.py` (a guarded file, so the PR waits for Alam). | C | nothing | Current models at lower cost; results anyone can rerun. | $0 | done 26 Sep: model IDs in the notebooks (recovery PR); prices verified (guardrail PR) |
| 1.5 | Private GitHub repo with pipeline v2, tests, notebooks, results and the corrections log. | A | done at handoff | Every number traces to a commit and a passing test (Gate 0). | $0 | done (handoff) |
| 1.6 | Pre-registration in `research/PREREGISTRATION.md`: frame, both criticality definitions, target-free and oracle gates, the random-gate control, primary outcomes, thresholds, stopping rules. | C drafts, A files on OSF | a free OSF account | A timestamped protocol that protects our sampling-frame argument from being turned on us. | $0 | doing: draft ready 26 Sep; you file it after Gate N |
| 1.7 | Annotation guide and a self-contained annotation page: one HTML file with the items embedded; each annotator saves a JSON file and emails it to Alam, who commits it to `annotations/raw/`. Annotators get no access to this repo. | C | names of 2 annotators | Ready by Oct 9. About 1 minute per item. | $0 | doing: guide and page done 26 Sep; the item sampler waits for the kit |
| 1.8 | Notebook 01 Part 1 on all 57 sites: how much `data-*` survives per site. | C | nothing | If no site keeps `data-*`, the archive head-to-head with UCM is dead and only live pages count. | $0 | done (K21; rerun 26 Sep) |
| 1.9 | Clone UCM, build its 10 self-hosted sites in Docker, dry-run its detector. | C | optional `DOCKERHUB_TOKEN` | Which UCM numbers reproduce here and which need an AWS GitLab server. | $0 | todo |
| 1.10 | Pull the other 8 Mind2Web train shards (about 5 GB): `python3 scripts/fetch_mind2web.py --all`. | C | disk space | More critical items (229 today). Needed only if coupling goes ahead. | $0 | todo |
| 1.11 | Decide the team, the 2 annotators, spend caps, corresponding author and affiliation, TMLR or TDSC intent. | A | 1 hour | Who owns each A row, the fee route, the key caps. | $0 | todo |
| 1.12 | Weekly competitor watch: Prismata v2 or code, UCM v2, anything citing either. Report in `research/competitor_watch/<date>.md`. | C | the weekly prompt | Early warning for Gate 3. | $0 | todo |
| 1.13 | Retrofit the three v2 notebook builders with `docs/NOTEBOOK_GIT_CONVENTION.md`: config cell, clone or pull, `push()` with metric-valued messages, periodic push for long cells, a `colab/<task-id>` branch, the token from Colab secrets. Rebuild the notebooks and add a test that they match their builders (builds are deterministic since 25 Sep). | C | nothing | Colab results arrive as commits, not as files you forward. | $0 | done 26 Sep (recovery PR); `tests/test_notebooks.py` |
| 1.14 | Create a fine-grained GitHub token for this repo only (Contents read and write, 90 days) and save it in Colab secrets as `GH_TOKEN_COLAB`, with the model keys as `RESEARCH_ANTHROPIC_API_KEY`, `OPENAI_API_KEY` and `GEMINI_API_KEY`. | A | 10 minutes | Unblocks every Colab push. Renew before it expires (see HUMAN_TASKS). | $0 | todo |
| 1.15 | Batch API support in `src/llm.py` (Anthropic Message Batches, OpenAI Batch): check the budget against the summed estimate before submitting, save the batch ID in the experiment folder so a later session can collect it, log cost from the results. A `[guardrail]` PR, in a session of its own. | C | nothing to build; a key to test | The 50% discount every Phase 2 and 3 budget assumes. Until it lands, runs cost about double. | under $1 | done 26 Sep (guardrail PR); live test in `experiments/2026-09-26_1.15_api-smoke-test/` |
| 1.16 | Notebook plumbing for the runs Claude does (1.8, 2.2, 2.4, 2.8): move their work cells into scripts under `experiments/` or run them headless, route every model call through `src/llm.py`, read `RESEARCH_ANTHROPIC_API_KEY` (map the Colab secret of the same name), and fix the GPT-5 call parameters in notebook 02 (`max_completion_tokens`, enough room for reasoning tokens). | C | nothing | Paid notebook work runs under the budget cap and cost log. | $0 | done 26 Sep (recovery PR); notebook 03 uses the Batch API |
| 1.17 | C7b: Prismata-style criticality when a link needs an `href`, on the 57-site frame (pre-registered 26 Sep). | C | the kit (`src/pipeline_v2.py`) | Whether the page representation moves Prismata-style numbers; decides the Prismata side of P1. | $0 | done 26 Sep (K26: ratio 0.48) |
| 1.18 | C7c: UCM's Booking selectors on live pages and on the same pages stripped to the archive's attributes (pre-registered 26 Sep). | C | nothing | Separates archive stripping from drift. | $0 | done 26 Sep (K25: 53 of 57 disabled) |

## Phase 2: ground truth, pilots, reproduction (Oct 12 to Nov 8)

| ID | Task | Owner | Needs | Output, and what it decides | Budget | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 2.1 | Human annotation pilot: 2 annotators label the same 300 regions, stratified by site and by heuristic outcome. | A+T | about 5 h per annotator | Kappa of 0.70 or better, and the heuristic's precision and recall against people. | $0 | todo |
| 2.2 | Vendor labeling pilot on the same 300: Claude Sonnet 5, GPT-5.4-mini, GPT-5.4-nano. | C+K | `RESEARCH_ANTHROPIC_API_KEY`, `OPENAI_API_KEY` | Each model's false-trust rate against people and a first coupling estimate. Drives the Oct 30 go/no-go. | about $1 | todo |
| 2.3 | Gemini 3 Flash arm of 2.2. Optional. | C+K if preflight reaches Google's API, else A/Colab | `GEMINI_API_KEY` | The third model in Prismata's panel. | under $1 | todo |
| 2.4 | Notebook 03 v2 real-agent pilot: 16 conditions, 40 trials each, plus the paired no-injection control, 1,280 calls through the Batch API. | C+K | `RESEARCH_ANTHROPIC_API_KEY` | Whether the 0.0% narrow vs 96.9% page-wide contrast survives a real agent. First read on Gate 2. | $11 to $22 | todo |
| 2.5 | UCM reproduction for Gate 1: boundary F1 on Booking, Reddit and GitLab pages, plus 60 agent episodes on 3 self-hosted sites. | C+K | `RESEARCH_ANTHROPIC_API_KEY`, `OPENAI_API_KEY` if their judge needs it | F1 inside their intervals (Reddit 0.997, Booking 0.879, GitLab 0.840; UCM Table 2); attack success inside theirs. Decides Gate 1. | $15 to $40 | todo |
| 2.6 | UCM's WASP numbers on WebArena GitLab. Optional: only if 2.5 fails or a reviewer insists. | A | AWS account and a Docker machine | The GitLab half of their paper reproduced. | $45 to $120 | todo |
| 2.7 | Notebook 01 Part 2 live capture: the 7 study sites plus up to 10 more. Colab pushes the capture to an orphan data branch (`docs/NOTEBOOK_GIT_CONVENTION.md`). | A/Colab | Colab, `GH_TOKEN_COLAB` | A live corpus with `data-*` density per site, and a refusal list. | $0 | todo |
| 2.8 | Notebook 01 Part 3: UCM's detector with its pinned prompt on archive and live pages, scored against the 2.1 human labels where they overlap. | C+K | `RESEARCH_ANTHROPIC_API_KEY`, the capture from 2.7 | Detector F1 against semantic class ratio, archive vs live. | $3 to $13 | todo |

## Phase 3: experiments at scale (Nov 9 to Dec 13). Waits for Gate N.

| ID | Task | Owner | Needs | Output, and what it decides | Budget | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 3.1 | Confirmatory coupling study, only on a go at Oct 30. People label every item; the vendors label the same items. | A+T, then C+K | 9 to 44 annotation hours | Coupling with a site-bootstrap interval; the criticality ratio as a secondary result. | $2 to $7 | todo |
| 3.2 | Real agents from 3 families on the 8 headline conditions, 100 trials each plus paired controls: Claude Sonnet 5, GPT-5.6 Terra, Gemini 3 Flash. | C+K; Gemini arm as in 2.3 | all three keys | Compliance per family with intervals. Decides Gate 2 on Dec 6. | about $27, plus $5 to $10 for Gemini | todo |
| 3.3 | Mislabel by criticality on UCM's self-hosted sites: one wrong label at a critical vs a non-critical position, typed output channel vs free text. | C+K | `RESEARCH_ANTHROPIC_API_KEY` | The two-system contrast. Prediction: the typed channel degrades gracefully and the text channel does not. | $60 to $150 | todo |
| 3.4 | Measure the envelope an LLM picks when it scopes a task the Prismata way, on the 1,163 pages; place it on the gate-width curve; rerun influence escape at that width. | C+K | `RESEARCH_ANTHROPIC_API_KEY` | One measured operating point in place of today's bracket (0.0% task-scoped, 43.4% page-wide). | $24 to $35 | todo |
| 3.5 | UCM deployment cost: CSS selectors needed per site across 57 sites, and how many break between the 2023 archive and 2026 live pages. | C+K | `RESEARCH_ANTHROPIC_API_KEY`, the capture from 2.7 | A selectors-per-site distribution and a breakage rate. | about $11 | todo |
| 3.6 | Sensitivity analyses: region root counted or not, unit granularity, target-free vs oracle gate, 3 vs all trajectories, leave one site out, seeds. Add a random gate of matched width and a token-cost axis per gate width. | C | nothing | Every headline number with its range under each definition; width separated from which elements are admitted. | $0 | todo |

## Phase 4: the mechanism, TDSC route only (Dec 14 to Jan 10)

| ID | Task | Owner | Needs | Output, and what it decides | Budget | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 4.1 | Criticality-conditioned verification: a second labeling call only on untrusted regions inside the gate-admitted set (about 1.2 regions per trajectory at K = 21, against 25 with no gate). | C+K | `RESEARCH_ANTHROPIC_API_KEY` | A prototype with a bounded extra cost per page. | $15 to $40 | todo |
| 4.2 | Evaluate it: coverage, added latency, false blocks, residual effect against both defenses, including an attacker who knows the verifier exists. | C+K | `RESEARCH_ANTHROPIC_API_KEY` | TDSC if residual effect falls at bounded cost; otherwise TMLR and no time lost. | $25 to $60 | todo |

## Phase 5: writing, figures, artifact, review (Dec 14 to Feb 7)

| ID | Task | Owner | Needs | Output, and what it decides | Budget | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 5.1 | Claims ledger complete: every paper claim mapped to evidence file, commit and test. | C | nothing | Catches the 19 Sep class of error before a reviewer does. | $0 | todo |
| 5.2 | Figures: reconciliation ladder, gate-width curve (oracle and deployable), confinement contrast, four-layer bars, per-site heatmap. One script per figure. | C | nothing | Five figures from frozen results. | $0 | todo |
| 5.3 | Full draft: introduction, threat model, method, results, related work, limitations, ethics and disclosure. | C drafts, A+T edit | 20 to 30 editing hours | A complete draft by Jan 24. | $0 | todo |
| 5.4 | Artifact: clean repo, one-command reproduction, README, frozen data. | C prepares, A publishes | public GitHub release, Zenodo account | A citable artifact with a DOI. | $0 | todo |
| 5.5 | Internal adversarial review: `adversarial-reviewer` on every claim, plus one colleague. | C, plus one colleague | about 4 h of a colleague | A fix list. A construct-validity failure triggers stop condition 4. | $0 | todo |
| 5.6 | Dated re-run of every number from the tagged commit, then freeze. Tag `results-frozen-<date>`. | C+K; Colab arms A/Colab | all keys again | Every number produced on one date from one commit. | $20 to $40 | todo |

## Phase 6: submission (Feb 8 to Feb 19)

| ID | Task | Owner | Needs | Output, and what it decides | Budget | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 6.1 | Format and anonymize: TMLR template (double-blind) or IEEE template for TDSC. | C | nothing | Submission PDF with the artifact link anonymized. | $0 | todo |
| 6.2 | arXiv preprint. A first cs.CR submission may need an endorsement, so ask early. | A | arXiv account | A public, dated claim to the result. | $0 | todo |
| 6.3 | Submit on OpenReview (TMLR) or ScholarOne (TDSC). | A | the venue account | Submitted by 19 Feb 2027 or 19 Mar 2027. | $0 | todo |
| 6.4 | Reviews: point-by-point responses and any extra runs. | C drafts, A posts | posting | A revision inside the discussion window. | $0 to $30 | todo |

## Gates

Pass conditions are fixed now, before the data exists. Changing one needs Alam's approval and an entry in `research/DECISIONS.md`.

| Gate | Date | Passes when | If it passes | If it fails |
| --- | --- | --- | --- | --- |
| Gate 0: measurement discipline | standing | A number has a commit, a passing test and a named construct check | It can enter the paper | It stays out |
| Gate N: contribution | Oct 11 | Alam approves `research/CONTRIBUTION_STATEMENT.md`: 2 or 3 contributions, each rated NOVEL or NOVEL AS MEASUREMENT by the audit, each with evidence or a funded task that produces it | Phase 3 spend can start | Rework the statement. If nothing rates NOVEL AS MEASUREMENT or better, stop and decide with Alam (the fallback is a reproducibility note) |
| Coupling go/no-go | Oct 30 | Pilot false-trust rate against people is 20% or more per vendor, or 10% with 2 annotators free for about 44 hours | Run 3.1 | Report the pilot kappa with its interval and drop 3.1 |
| Gate 1: UCM reproduces | Nov 8 | Boundary F1 inside their intervals on at least 2 of 3 sites, and attack success inside theirs on the self-hosted sites | Two-system comparative paper | Ask the authors; if unresolved, a one-system paper (still viable at TMLR) |
| Gate 2: real agents | Dec 6 | Compliance measured for 3 model families with intervals; the narrow vs page-wide contrast holds or its absence is explained | The risk framing stays | Effect rates become mechanism upper bounds; the definitional and confinement results stand |
| Venue call | Dec 13 | Alam wants TDSC and two people are free for Phase 4 | Phase 4 | TMLR route, submit Feb 19 |
| Mechanism check | Jan 10 | 4.1 cuts residual effect at a bounded cost per page | TDSC, submit Mar 19 | TMLR; the slip is about a week |
| Gate 3: scooped | weekly | Nobody publishes the definitional audit or the deployment measurement first | Carry on | Repackage around what is still unique |

**Coupling go/no-go in numbers** (80% power for coupling of 2x, site clustering priced in with design effect 2.68; source `results/roadmap/tokens_and_coupling.json`):

| Per-vendor false-trust rate | Items needed | Annotation hours | Call |
| --- | --- | --- | --- |
| 20% | 469 | about 9 | Go |
| 10% | 2,192 | about 44 | Go only with 2 annotators and the shards from 1.10 |
| 5% | 9,084 | about 180 | No-go |

Today's shards supply at most 1,660 eligible items (229 critical), so the 10% row needs 1.10 first.

The design effect comes from an intraclass correlation of 0.24 measured in the 26 Aug smoke test as heuristic-versus-LLM label disagreement across sites (bootstrap 95% interval 0.065 to 0.409), not from human-labeled errors. At the interval's upper end (design effect 3.86) every row needs about 44% more items: 676, 3,157 and 13,084. Re-estimate it from the 2.1 human labels before the Oct 30 call.

**Stop conditions.** Any one of these means do not submit to a good journal: (1) UCM does not reproduce from its own code and its authors do not answer; (2) real agents almost never follow a visible injection, so every effect rate collapses; (3) someone publishes the definitional audit first; (4) another construct-validity failure of the 19 Sep kind. None is true on 25 Sep.

## Budget (API spend only; Claude Code's own usage is separate)

| Phase | Claude's runs | Alam's runs | Human hours | Main driver |
| --- | --- | --- | --- | --- |
| 0 and 1 | $0 | $0 | about 3 | emails, decisions, OSF, Colab token |
| 2 | $30 to $76 | under $1, plus $45 to $120 if 2.6 runs | about 12 | annotation pilot, 10 h |
| 3 | $124 to $230 | $5 to $10 | 1 to 46 | coupling annotation, only on a go |
| 4 (TDSC only) | $40 to $100 | $0 | 0 | mechanism runs |
| 5 | $20 to $40 | $1 to $2 | 26 to 36 | editing and review |
| 6 | $0 to $30 | $0 | about 4 | accounts, submission, responses |
| Total | $175 to $380 (TMLR), $215 to $480 (TDSC) | $6 to $13, plus optional $45 to $120 | 45 to 100 | |

The API figures assume the Batch API's 50% discount wherever calls are independent (task 1.15). Approval rules: any single run over $25, or a phase going over its upper bound, needs a needs-human issue and Alam's yes. Every paid call goes through `src/llm.py`, opened with `LLM.from_experiment`, which enforces the cap in the experiment's `config.yaml`.

