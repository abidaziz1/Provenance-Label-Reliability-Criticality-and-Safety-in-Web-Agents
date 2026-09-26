# Decisions

One entry per decision: date, decision, who decided, why, evidence, what it changes. Newest at the bottom. Decisions before 25 Sep are reconstructed from `docs/context/` and cite it.

| Date | Decision | By | Why and evidence | Changes |
| --- | --- | --- | --- | --- |
| 2026-09-19 | Withdraw three findings: the sampling-frame explanation for the 1.2% gap; "the labeler cannot see the cue"; "0% to 100% on one label error". | Alam, after the independent audit | `docs/context/05_CORRECTIONS_19Sep2026.md`, `docs/history/Independent_Research_Audit_19Sep.md` | Paper framing; every figure recomputed |
| 2026-09-19 | Headline comparison becomes 49.93% vs 1.2% with the definitional account, replacing 74.65% vs 1.2%. | Alam | `docs/context/02_Reconciliation_1.2pct.md` | Contribution C1 |
| 2026-09-19 | Every criticality number states unit, whether the region root counts, and the gate. | Alam | The root rule alone moved results by 21.5 to 34.3 points | Reporting rule in CLAUDE.md |
| 2026-09-24 | Venue: TMLR primary, IEEE TDSC stretch, ACM DTRAP floor. | Alam | Venue audit in `docs/context/01_Submission_Roadmap.md` | ROADMAP.md targets |
| 2026-09-24 | The coupling study runs only on a go at Oct 30, with fixed thresholds. | Alam | Power table in ROADMAP.md | Task 3.1 |
| 2026-09-25 | Hand the project to Claude Code with a GitHub repo as the system of record. | Alam | Handoff request | This repo |
| 2026-09-25 | Phase 0 novelty audit comes first; Phase 3 spend waits for Gate N. | Alam | "The primary focus should be finding the true novelty and research contribution of this work." | ROADMAP.md Phase 0 |
| 2026-09-25 | Park the external review's ideas until N0.4, except the random-gate control, which goes into the pre-registration. | Claude, at handoff; Alam confirms at Gate N | `research/BACKLOG_IDEAS.md` | Tasks 1.6, 3.6 |
| 2026-09-25 | Research key is `RESEARCH_ANTHROPIC_API_KEY`, never `ANTHROPIC_API_KEY`, so Claude Code never bills its own requests to it. | Claude, at handoff | Claude Code reads `ANTHROPIC_API_KEY` for its own requests | `env.example`, `src/llm.py` |
| 2026-09-25 | No Google Drive. Large Colab outputs go to orphan `data/<task-id>` branches in this repo. | Claude, at handoff | Keeps one system of record and no extra credentials | `docs/NOTEBOOK_GIT_CONVENTION.md` |
