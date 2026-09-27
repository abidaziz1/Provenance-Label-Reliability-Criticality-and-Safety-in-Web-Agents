# What structural prompt-injection defenses read

A measurement study of how the page a web agent's defense sees changes what that defense can do. It covers two published structural defenses against indirect prompt injection in web agents: Prismata (arXiv:2607.08147) and Untrusted Content Masking (UCM, arXiv:2607.05277). This is work in progress, targeting TMLR in February 2027.

**Every number here is provisional.** A number is final only when `research/CLAIMS_LEDGER.md` marks it `supported`. Nothing in this repo claims that either paper's published results are wrong. Where our measurements differ from a published number, we say which of our choices could explain the difference and which details only the authors can confirm.

## Main result so far (P1 in `research/CONTRIBUTION_STATEMENT.md`)

The archive behind Mind2Web, a widely used web-agent dataset, removes the page attributes structural defenses read. So does time.

| Finding | Value | Evidence |
| --- | --- | --- |
| Attribute names the Mind2Web archive keeps (57 sites, 1,163 pages) | 21. No site-authored `data-*`, `href`, `on*`, `tabindex`, `style` or `hidden` on any site | K21, `experiments/2026-09-25_1.8_attr-survival/` |
| UCM's published Booking selectors that match UCM's captures but nothing on 131 archived Booking pages | 24 of 25 hand-written; 68 of 68 LLM-written | K22, `experiments/2026-09-25_C7_ucm-selectors-on-archive/` |
| Same live Booking pages, attributes reduced to the archive's 21 names: working selectors disabled | 53 of 57 (drift held fixed) | K25, `experiments/2026-09-26_C7c_live-strip-vs-drift/` |
| Prismata-style criticality per visible untrusted node, links counted with vs without an `href` | 9.40% vs 19.57% (ratio 0.48, interval 0.32 to 0.64) | K26, `experiments/2026-09-26_C7b_actionability-on-archive/` |
| UCM Booking selectors that matched UCM's capture and no longer match today (one page) | 19% to 25% | `experiments/2026-09-26_C7c_live-strip-vs-drift/` |

**What these results do not show.**
- They do not show that UCM fails on archived pages. UCM writes its selectors from the page it sees; that test is planned.
- They do not show what Prismata's own count used. The paper does not state its page representation or link rule.

## Claims we withdrew

Older documents in `docs/context/`, `docs/history/` and the git history contain claims we later found wrong. The novelty audit of 25 Sep withdrew them (`research/NOVELTY_LEDGER.md`, `research/CORRECTIONS.md`):

- **"Prismata's 1.2% comes from a second, narrower definition."** Wrong: Prismata states one definition, three times.
- **"Prismata's gate is an oracle."** Wrong: the oracle was in our own reconstruction.
- **"A task-scoped envelope gives 0% effect."** Withdrawn as stated: our task-scoped envelope was the annotated target, so 0% held by construction.

## Reproduce

```bash
pip install -r requirements.txt
python3 -m pytest -q tests              # each claim's test recomputes it from the committed result file
python3 scripts/fetch_mind2web.py       # 1.27 GB, pinned revision
python3 scripts/attr_survival.py        # K21, a few minutes
python3 scripts/actionability_on_archive.py   # K26, about 3 minutes
```

The UCM selector scripts need a clone of `github.com/ethz-spylab/untrusted-content-masking` at commit `acff2e4` (set `UCM_DIR`). `scripts/live_strip_test.py capture` loads three Booking pages; the captured pages are not in this repo.

## Layout

| Path | What |
| --- | --- |
| `research/` | Contribution statement, novelty and claims ledgers, decisions, corrections, pre-registration draft, backlog |
| `experiments/` | One folder per run from 25 Sep on, each with its pre-registration, results and deviations |
| `scripts/`, `src/` | Analyses, the labeling pipeline, the budgeted LLM client (`src/llm.py`) |
| `tests/` | Per-claim tests, pipeline regressions, budget and secret guards, notebook checks |
| `results/` | Outputs up to 25 Sep, frozen |
| `notebooks/` | Colab notebooks and the builders that generate them |
| `annotations/` | Annotation guide and page (task 1.7) |
| `docs/` | Operations; imported project documents (`docs/context/`, `docs/history/`, frozen, some superseded) |
| `CLAUDE.md`, `ROADMAP.md`, `STATUS.md` | How the AI research assistant works in this repo, the plan, the current state |

## Third-party data and code

- **Mind2Web** (osunlp/Mind2Web, revision `17ece8eb`), CC BY 4.0. The data is not redistributed here, except small derived excerpts in `results/legacy/`.
- **UCM** (ethz-spylab/untrusted-content-masking, commit `acff2e4`), MIT License, copyright 2026 Nikolić, Zverev, Rando, Jagielski, Debenedetti and Tramèr. Its selectors are quoted in our result files.
- **Prismata.** Only its paper is used; no code has been released.

The full attribution and license notices are in `THIRD_PARTY_NOTICES.md`.

## License

Not chosen yet, so all rights are reserved for now. Open an issue if you want to reuse something.
