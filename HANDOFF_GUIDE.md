# Handoff guide for Alam

How to put Idea 3 in Claude Code and keep it running. About 45 minutes the first time, most of it creating keys. You can start with no keys at all: Phase 0 and most of Phase 1 need none, and Claude asks through a GitHub issue when a key would unblock something.

## What is in the kit

| File | What it gives Claude Code |
| --- | --- |
| `CLAUDE.md` | The operating brief, loaded every session: mission, the autonomy contract, research integrity rules, untrusted-content rule, git and secrets rules, your writing style |
| `STATUS.md`, `ROADMAP.md`, `RESEARCH_LOG.md` | Where things stand, the 50 tasks with owners and gates, the history |
| `research/` | The novelty ledger (Phase 0 starts here), claims ledger, decisions, corrections, dated human tasks, pre-registration stub, the parked ideas from the external review |
| `docs/context/`, `docs/history/` | The 11 project documents, frozen, with a reading order in `docs/00_IMPORT_MANIFEST.md` |
| `docs/OPERATIONS.md`, `docs/EXTERNAL_SERVICES.md` | The environment, network, keys, money, Docker, the Colab results flow, the leak procedure |
| `.claude/` | 7 skills (status, next-task, new-experiment, human-task, colab-intake, novelty-audit, session-end), 3 subagents (novelty-auditor, adversarial-reviewer, numbers-verifier), deny rules and a hook that block secret leaks, merges and pushes to main |
| `src/`, `scripts/`, `tests/`, `results/`, `notebooks/` | The code, every result, 17 passing tests, the three v2 notebooks |

You do not paste documents into chat. Claude reads them from the repo. You paste one prompt (step 7).

## Step 1. Create the GitHub repo (2 minutes)

github.com/new: owner you, a name such as `idea3-confinement`, **Private**, no README, no license, no .gitignore. Then in the repo's Settings, General, Pull Requests: keep **Allow merge commits**, untick squash and rebase merging. Claude stacks its work on open PRs, and squash merges break that.

## Step 2. Push the kit (5 minutes)

You need git, Python 3 and a way to push to GitHub over HTTPS (sign in once with `gh auth login`, Git Credential Manager, or GitHub Desktop). On macOS, Linux or WSL:

```bash
unzip idea3-claude-code-kit.zip
cd idea3-repo
bash scripts/bootstrap_repo.sh https://github.com/<you>/idea3-confinement.git
```

The script scans for secrets, makes the first commit under your git identity, tags it `v2.0-baseline` and pushes both. By hand, it is: `git init`, `git checkout -b main`, `git add -A`, `git commit -m "v2.0 baseline"`, `git tag v2.0-baseline`, add the remote, push main and the tag.

Optional: paste the external review you received on 25 Sep under "Verbatim text" in `docs/reviews/2026-09-25_external_review.md` and commit it. Only a summary is there now.

## Step 3. Connect Claude Code to the repo (3 minutes)

At claude.ai/code, connect GitHub and install the Claude GitHub App with **Only select repositories** and this repo. That is the only GitHub access Claude Code needs; the credential stays outside the session.

## Step 4. Create the cloud environment (10 minutes)

At claude.ai/code, open the environment selector, **Add cloud environment**:

1. **Name:** `idea3`.
2. **Network access:** Custom. Tick "Also include default list of common package managers". Paste the domain list from `docs/OPERATIONS.md` section 2.1.
3. **Environment variables:** for now `OPENAI_API_KEY=proxy-injected` and `GEMINI_API_KEY=proxy-injected`. Add `RESEARCH_ANTHROPIC_API_KEY=<key>` when Claude asks for it (task H2), or now if you already made it.
4. **Setup script:** paste the script from `docs/OPERATIONS.md` section 2.3.
5. Save. Then open the environment again to add **API credentials** (they only appear when editing, on Pro and Max plans): OpenAI (host `api.openai.com`, header `Authorization`, prefix `Bearer`), and optionally Gemini (host `generativelanguage.googleapis.com`, header `x-goog-api-key`, no prefix) and Hugging Face (host `huggingface.co`, `Authorization`, `Bearer`).

If your plan has no API credentials section, put the OpenAI and Gemini keys in the environment variables instead.

## Step 5. Make the keys, with caps (15 minutes, can wait)

| Key | Where | Cap | Goes into |
| --- | --- | --- | --- |
| Anthropic research key | Claude Console: new workspace `idea3-research`, key inside it | spend limit $100 now; $300 a month from Phase 3 (task H3) | environment variable `RESEARCH_ANTHROPIC_API_KEY` (never `ANTHROPIC_API_KEY`); Colab secret of the same name |
| OpenAI | new project `idea3`, project key | budget $60 | API credential (step 4.5); Colab secret `OPENAI_API_KEY` |
| Gemini (optional) | Google AI Studio | budget alert $15 | API credential; Colab secret `GEMINI_API_KEY` |
| GitHub token for Colab | fine-grained token: this repo only, Contents read and write, 90 days | none needed | Colab secret `GH_TOKEN_COLAB` (task 1.14; renew before it expires, task H4) |

Details and the "not needed" list are in `docs/EXTERNAL_SERVICES.md`. The short version: no Google Drive (the repo and data branches replace it); no AWS unless you run the optional task 2.6 yourself; Slack only if you want pings (next step).

## Step 6. Decide how Claude reaches you (5 minutes)

Claude's issues and PRs are created under your own GitHub account, and GitHub does not notify you about your own activity. Pick one:

- **Slack:** create an incoming webhook for one channel, add `SLACK_WEBHOOK_URL=<url>` to the environment variables and `hooks.slack.com` to the network list. Claude posts one line per new needs-human issue.
- **Bookmarks:** your repo's issues filtered by `label:needs-human`, and its pull requests. Check both once a day.

The first session opens a test issue (H1) so you can confirm which works.

## Step 7. Start the first session (2 minutes)

At claude.ai/code: pick the repo and the `idea3` environment, set the permission mode to **Auto** (cloud sessions offer Accept edits, Plan and Auto; in Auto a safety classifier reviews each action instead of asking you, while the repo's deny rules and hook still apply; in Accept edits the session stops to ask before shell commands and stalls when you step away), paste prompt 1 from `ONBOARDING_PROMPT.md`, and send.

Expect from the first session: the preflight table, the baseline reproduction, the evidence inventory with tests, the first novelty audits, one PR, and a few needs-human issues (H1 alert check, 1.11 team decisions, 1.14 Colab secrets).

## Step 8. Your loop from here

| When | You do | Time |
| --- | --- | --- |
| A PR is ready | Review it: each task in it starts with "Check first". Merge with "Create a merge commit", oldest first | 5 to 15 min |
| A needs-human issue appears | Do the step, then paste prompt 5 into a session | varies |
| Starting any work session | Paste prompt 2 | 1 min |
| Mondays | Paste prompt 7 (weekly review and competitor watch) | 15 min |
| Gate dates: Oct 11 (Gate N), Oct 30 (coupling), Nov 8 (Gate 1), Dec 6 (Gate 2), Dec 13 (venue), Jan 10 (mechanism, TDSC route) | Decide; paste prompt 6 | 30 min |

After a good first week you can move prompts 7 and 2 into routines (`ONBOARDING_PROMPT.md` section 8) so sessions start on their own. Routines run without permission prompts, so turn them on only once you trust the loop, and never run a work routine and an interactive work session at the same time.

## What Claude does alone, and what comes to you

Of the 50 roadmap tasks, Claude runs 30 on its own (21 need nothing, 9 need a key you add to the environment), does most of 4 more (2.3, 3.2, 5.5, 5.6), and drafts 7 where you do the one step tied to your identity. 9 are yours alone, and one of those (the repo) is done at step 2. You keep: merges into main and tags, sending emails (1.1, 1.2), filing on OSF (1.6), team and budget decisions (1.11), annotation (2.1, 3.1), Colab runs (2.7, and Gemini arms if the cloud cannot reach Google), AWS (2.6, optional), gate calls, the draft's edits, and every public or account step (5.4, 6.2, 6.3). The dated list is `research/HUMAN_TASKS.md`.

## Alternative: run Claude Code on your own computer

See `docs/OPERATIONS.md` section 3. Same repo, same rules; keys come from a gitignored `.env` exported into your shell, and each task gets its own branch and PR.

## End of this phase

Rotate every key with the checklist at the end of `docs/EXTERNAL_SERVICES.md` (task H7).
