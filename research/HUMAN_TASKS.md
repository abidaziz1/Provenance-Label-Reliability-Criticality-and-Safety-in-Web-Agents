# Human tasks

Everything that waits on Alam. Each open row has a GitHub issue labeled `needs-human` (skill: human-task) once Claude asks. If issues cannot be created from the session, the row here is the request, and Claude also puts it at the top of STATUS.md and in the PR body.

IDs starting with H are standing human steps with no roadmap task of their own. Status values: `not asked` (Claude asks when the inputs are ready or the ask-by date nears), `asked`, `done`, `dropped`. `/status` flags any row whose need-by date is within 14 days.

| ID | What Alam does | Issue | Ask by | Need by | Blocks | Status |
| --- | --- | --- | --- | --- | --- | --- |
| H0 | Environment setup from HANDOFF_GUIDE.md: repo, GitHub App, cloud environment, network list, setup script | | 2026-09-25 | 2026-09-28 | everything | asked (handoff) |
| H1 | Check that a needs-human test issue reaches you (GitHub notification or Slack); pick your alert channel | | task 0.1 | 2026-10-02 | every later ask | not asked |
| 1.11 | Team, 2 annotators, spend caps, corresponding author and affiliation, venue intent | | 2026-09-29 | 2026-10-04 | 1.7, 2.1 | not asked |
| 1.14 | Colab secrets: `GH_TOKEN_COLAB` (fine-grained, this repo, Contents read and write, 90 days) and the model keys | | 2026-10-01 | 2026-10-11 | 2.7 and every Colab run | not asked |
| 1.1 | Send the Prismata email Claude drafted | | draft ready | 2026-10-06 | C1 confirmation | not asked |
| 1.2 | Send the UCM email Claude drafted | | draft ready | 2026-10-06 | Gate 1 | not asked |
| 1.6 | File the pre-registration on OSF | | draft ready | 2026-10-11 | Phase 2 data | not asked |
| N0.5 | Approve the contribution statement (Gate N) | | 2026-10-08 | 2026-10-11 | Phase 3 spend | not asked |
| H2 | Add `RESEARCH_ANTHROPIC_API_KEY` (workspace limit $100) and the OpenAI credential to the cloud environment | | when 2.2 is ready | 2026-10-12 | 2.2, 2.4, 2.5, 2.8 | not asked |
| 2.1 | Annotation pilot, 2 annotators, about 5 h each | | 2026-10-09 | 2026-10-25 | 2.2 scoring, coupling go/no-go | not asked |
| Gate | Coupling go/no-go decision | | 2026-10-28 | 2026-10-30 | 3.1 | not asked |
| 2.7 | Live capture in Colab | | 2026-10-12 | 2026-10-25 | 2.8, 3.5 | not asked |
| 2.3 | Gemini arm in Colab, only if preflight cannot reach Google's API | | when 2.2 is ready | 2026-11-01 | nothing critical | not asked |
| 2.6 | WASP on AWS, optional | | only if 2.5 fails | 2026-11-08 | Gate 1 fallback | not asked |
| Gate | Gate 1 decision (UCM reproduces) | | 2026-11-06 | 2026-11-08 | Phase 3 scope | not asked |
| H3 | Raise the Anthropic workspace limit to $300 a month | | 2026-11-01 | 2026-11-09 | Phase 3 runs | not asked |
| 3.1 | Coupling annotation, only on a go | | 2026-10-31 | 2026-11-30 | C6 | not asked |
| Gate | Gate 2 decision (real agents) | | 2026-12-04 | 2026-12-06 | the risk framing | not asked |
| Gate | Venue call: TMLR or TDSC | | 2026-12-11 | 2026-12-13 | Phase 4 | not asked |
| H4 | Renew `GH_TOKEN_COLAB` before its 90 days run out | | 10 days before expiry | before expiry | 5.6 Colab arms | not asked |
| Gate | Mechanism check (TDSC route only) | | 2027-01-08 | 2027-01-10 | venue | not asked |
| H5 | Ask for a cs.CR arXiv endorsement if this is your first cs.CR submission | | 2027-01-10 | 2027-02-01 | 6.2 | not asked |
| 5.3 | Team edits of the draft | | 2027-01-20 | 2027-02-05 | submission | not asked |
| 5.5 | One colleague reviews for about 4 h | | 2027-01-20 | 2027-02-01 | submission | not asked |
| H6 | Tag `results-frozen-<date>` on main after merging 5.6 | | after 5.6 | 2027-02-07 | 5.4, 6.1 | not asked |
| 5.4 | Publish the artifact: public release and Zenodo DOI | | 2027-02-01 | 2027-02-10 | submission | not asked |
| 6.2 | arXiv preprint | | 2027-02-05 | 2027-02-15 | Gate 3 protection | not asked |
| 6.3 | Submit on OpenReview (TMLR) or ScholarOne (TDSC) | | 2027-02-12 | 2027-02-19 | done | not asked |
| H7 | Rotate every key (checklist in docs/EXTERNAL_SERVICES.md) | | end of phase | end of phase | none | not asked |
