# Operations

How this repo runs: where sessions run, what they can reach, where keys live, how work reaches main, and what to do when something goes wrong. Facts about Claude Code cloud sessions were checked against code.claude.com on 25 Sep 2026; `scripts/preflight.py` is the final word for any given environment.

## 1. Where Claude Code runs

**Cloud sessions (recommended).** Started from claude.ai/code, the Claude app's Code tab, the desktop app with Cloud selected, or `claude --cloud`. Each session runs in an Anthropic-managed VM (4 vCPU, 16 GB RAM, 30 GB disk, Ubuntu 24.04, Python 3, Docker, `gh`), clones this repo, and keeps running when Alam closes his laptop. Pushes go only to the session's own branch. Routines (scheduled cloud sessions) use the same environments.

**Local sessions.** `claude` in a clone on Alam's machine. Everything his machine can reach is reachable, including Docker if installed. Keys come from his shell environment.

Both read the same `CLAUDE.md`, `.claude/settings.json`, hooks, skills and subagents from the repo.

## 2. The cloud environment

Create one environment named `idea3` at claude.ai/code (environment selector, then **Add cloud environment**). Keep it personal: anyone who uses an environment can read its variables and setup script.

### 2.1 Network access: Custom

Choose **Custom**, tick **Also include default list of common package managers** (that list already covers PyPI, GitHub, Docker Hub, `api.anthropic.com` and `*.googleapis.com`, which includes the Gemini API), and add one domain per line:

```text
api.openai.com
huggingface.co
*.huggingface.co
hf.co
*.hf.co
arxiv.org
*.arxiv.org
api.semanticscholar.org
www.semanticscholar.org
openreview.net
*.openreview.net
dblp.org
aclanthology.org
proceedings.mlr.press
proceedings.neurips.cc
www.usenix.org
www.ndss-symposium.org
jmlr.org
dl.acm.org
ieeexplore.ieee.org
www.computer.org
link.springer.com
doi.org
api.crossref.org
api.openalex.org
papers.nips.cc
generativelanguage.googleapis.com
osf.io
cdn.playwright.dev
playwright.download.prss.microsoft.com
playwright.azureedge.net
```

Google Scholar blocks automated access, so the literature audit uses Semantic Scholar, OpenAlex, Crossref, DBLP and the publishers' pages instead. Add `hooks.slack.com` only if you set up the Slack webhook. Do not choose **Full**: this project reads untrusted web content all day, and an allowlist limits where an injected instruction could send anything. When a task needs a new domain, Claude opens a needs-human issue naming the domain and the reason; a blocked request returns `403` with `x-deny-reason: host_not_allowed`.

GitHub, MCP connectors and API-credential hosts bypass the allowlist by design. The GitHub proxy only lets a session reach the repositories attached to it.

### 2.2 Keys: environment variables and API credentials

Two mechanisms, and which one a key uses matters:

- **API credentials** (Pro and Max plans; not yet on Team or Enterprise). You add the key in the environment editor under **API credentials**, with the host it belongs to. The agent proxy attaches it to requests for that host after they leave the VM. Claude and its commands never see the value. They do not work for `api.anthropic.com`, PyPI, npm or GitHub. You can add them only when editing an environment that already exists.
- **Environment variables** (`.env` format in the environment dialog). Copied into every session at startup; any command Claude runs can read them. Changes apply to sessions started afterwards.

| Key | Mechanism | Setting |
| --- | --- | --- |
| Anthropic research key | environment variable (credentials never apply to `api.anthropic.com`) | `RESEARCH_ANTHROPIC_API_KEY=<key>` |
| OpenAI | API credential, host `api.openai.com`, header `Authorization`, prefix `Bearer` | plus the variable `OPENAI_API_KEY=proxy-injected` so the SDK starts |
| Gemini (optional) | API credential, host `generativelanguage.googleapis.com`, header `x-goog-api-key`, no prefix | plus `GEMINI_API_KEY=proxy-injected` |
| Hugging Face (optional) | API credential, host `huggingface.co`, header `Authorization`, prefix `Bearer` | none needed |
| Docker Hub (optional) | environment variables | `DOCKERHUB_USER=<name>`, `DOCKERHUB_TOKEN=<read-only token>` |
| Slack webhook (optional) | environment variable | `SLACK_WEBHOOK_URL=<url>` |

On a plan without API credentials, put the OpenAI and Gemini keys in environment variables instead. After any change, start a new session and run `python3 scripts/preflight.py`: 200 means the key works. If a proxy-attached key returns 401, the placeholder header is not being replaced; switch that key to an environment variable.

Never name the research key `ANTHROPIC_API_KEY`: Claude Code would use it for its own requests and bill them to the research budget.

### 2.3 Setup script

Paste this into the environment's **Setup script** field. It runs as root before Claude starts, on the first session and whenever the cache expires (about every 7 days) or the script or network list changes. It must finish in about 5 minutes and must exit 0, so the download is capped at 200 seconds. The Mind2Web frame is 1.27 GB and normally fits; if it does not, the session-start hook tells Claude the shards are missing and Claude runs `scripts/fetch_mind2web.py` in the session (that copy is not cached, so it repeats in each new session until the cache rebuilds).

```bash
#!/bin/bash
PKGS='lxml==6.1.0 cssselect==1.5.0 numpy==2.4.4 scipy==1.17.1 huggingface_hub==1.28.0 nbformat==5.11.1 tiktoken==0.14.0 pytest>=8 pyyaml==6.0.3 anthropic>=0.40 openai>=1.50'
python3 -m pip install -q --break-system-packages $PKGS || python3 -m pip install -q $PKGS || true
command -v gh >/dev/null || (apt-get update -qq && apt-get install -y -qq gh) || true
mkdir -p /opt/idea3-data/mind2web
timeout 200 python3 - <<'PY' || true
from huggingface_hub import hf_hub_download
for s in ("train_0.json", "train_1.json", "train_10.json"):
    hf_hub_download("osunlp/Mind2Web", f"data/train/{s}", repo_type="dataset",
                    revision="17ece8eb89862368edc0cc806acee6fca5163474",
                    local_dir="/opt/idea3-data/mind2web")
PY
exit 0
```

`scripts/session_start.sh` (a SessionStart hook in `.claude/settings.json`) then links `data/mind2web` to `/opt/idea3-data/mind2web`, sets `core.hooksPath` so the secret scan runs on every commit, and installs requirements if the cache missed them.

## 3. Local setup

macOS, Linux or WSL:

```bash
git clone https://github.com/<you>/<repo>.git idea3 && cd idea3
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
git config core.hooksPath .githooks
cp env.example .env              # fill in the values in an editor; .env is gitignored
python3 scripts/fetch_mind2web.py
set -a; source .env; set +a     # export the keys into this shell only
claude
```

Claude is denied read access to `.env` by `.claude/settings.json`, and the Bash hook blocks commands that print it. Keys reach scripts only through the environment of the shell that started `claude`.

## 4. How work reaches main

- **Cloud sessions** push only to their own `claude/...` branch, so one session is one branch and one PR. Claude commits each task separately (the message starts with the task ID) and gives each task its own "Check first" section in the PR body. Changes to guardrails, the pre-registration, a claim or a gate go in a session of their own, so that PR carries only that change and says so in its title (`[guardrail]`, `[prereg]`, `[claim]`, `[gate]`). **Local sessions** use one branch and one PR per task.
- Claude opens the PR as a draft when work starts, so a second session does not pick the same task, and marks it ready at the end.
- **Alam reviews and merges every PR into main, using "Create a merge commit".** Squash or rebase merges break the stacking below; turn them off in the repo settings (Settings, General, Pull Requests). Claude never merges into main and never pushes to it: the deny rules in `.claude/settings.json` and the Bash hook refuse `gh pr merge`, merge calls through `gh api`, and pushes to main.
- New cloud sessions and routine runs start from main. If work PRs are still open, Claude merges them into its branch, oldest first ("stacked on #N"), so work continues while PRs wait. Merging them in order clears the stack. If Alam closes a PR without merging it, Claude rebuilds the stack without it.
- CI (`.github/workflows/ci.yml`) runs the secret scan and the tests on every push and PR.
- Tags on main (`v2.0-baseline` at bootstrap, `results-frozen-<date>` after task 5.6) are Alam's: a cloud session cannot push tags.
- The repo is public since 27 Sep 2026, so branch protection is free: protect main (require a PR, block force pushes and deletion). Everything committed is public, drafts included; never commit captured pages, raw data or anything under embargo.

## 5. Human tasks

Claude opens a GitHub issue labeled `needs-human` for anything only Alam can do, then keeps working on something else. Issues carry numbered steps, paths, secret names to set, time, cost, a need-by date, and exactly what to send back. `research/HUMAN_TASKS.md` mirrors them.

Notifications: Claude's issues and PRs are created through Alam's own GitHub identity, and GitHub does not notify you about your own activity. So either set up the Slack webhook (Claude posts one line per new issue), or bookmark the repo's issue list filtered by `label:needs-human` and the PR list and check them daily. Task 0.1 includes a test issue so you can see which works.

## 6. Docker in cloud sessions

Docker is installed, but the daemon may need starting (`dockerd > /tmp/dockerd.log 2>&1 &`). Image pulls follow the network allowlist; Docker Hub is in the default list. Processes inside containers do not automatically go through the session's proxy or trust its CA certificate, so a `docker build` that downloads packages can fail. The usual fix: build and run with `--network host`, pass `HTTP_PROXY`/`HTTPS_PROXY` as build arguments, and copy the proxy CA bundle into the image and install it in an early layer. If the environment has a proxy README (for example `/root/.ccr/README.md`), follow its Docker section. Tasks 1.9, 2.5 and 3.3 depend on this; if a container cannot reach what it needs, Claude opens a needs-human issue rather than disabling any check.

## 7. Colab results flow

Colab runs push to `colab/<task-id>` branches; large files go to orphan `data/<task-id>` branches. Details in `docs/NOTEBOOK_GIT_CONVENTION.md`. Claude takes results in with the `colab-intake` skill.

## 8. Routines (optional, after the first week)

Routines are saved cloud sessions that run on a schedule (claude.ai/code/routines). They run without permission prompts and nobody reads their chat, so enable them only once a week of supervised sessions has gone well. Prompts are in `ONBOARDING_PROMPT.md` section 8:

- Weekly review and competitor watch (prompt 7, task 1.12): Mondays. It writes only `research/competitor_watch/`, `research/weekly/` and `research/HUMAN_TASKS.md`, so it never conflicts with a work session.
- Weekday work session (prompt 2 plus a time limit): at most one a day, never alongside an interactive work session.

Each run opens its own session and PR, and counts against the daily routine allowance and subscription usage.

## 9. Money

- Provider caps first: an Anthropic Console workspace for this project with a spend limit; an OpenAI project with its own key and budget; a Google Cloud budget alert for Gemini (Google's budget alerts notify, they do not stop spending).
- Then `src/llm.py`: opened with `LLM.from_experiment`, every paid call checks the experiment's `budget_usd` before it is made and logs cost to `cost.json`. Batch API support (50% cheaper) arrives with task 1.15; until then runs cost list price.
- Then the rules in CLAUDE.md: one run over $25, or a phase over its ROADMAP.md budget, needs Alam's yes.
- Claude Code's own usage is part of Alam's subscription and is not in these budgets.

## 10. If a secret leaks

1. Stop. Do not push.
2. If the commit is not pushed: remove the secret, amend or reset the commit, rerun `python3 scripts/scan_secrets.py`.
3. If it was pushed, or printed in a session: open a needs-human issue titled `rotate <KEY NAME>` without the value. Alam revokes the key at the provider and makes a new one. Revoking is the only real fix; rewriting history comes after and only with Alam (force-push is blocked for Claude).
4. Log the incident in RESEARCH_LOG.md: what leaked (name only), how, and the fix to the guardrail.

Alam rotates every key at the end of this phase of work anyway.

## 11. Guardrails in this repo

| Guardrail | File | Stops |
| --- | --- | --- |
| Read denials | `.claude/settings.json` | Claude's file tools reading `.env`, `.env.*`, `secrets/`, key and credential files, `/proc`, and the credential files of git, gh, Docker and Hugging Face |
| Bash deny rules | `.claude/settings.json` | printing the environment, `gh pr merge` and merge calls, pushes to main, force pushes, `--no-verify`, hook-path overrides, `git add -f`; enforced in every permission mode, including inside compound commands |
| Bash hook | `.claude/hooks/guard_secrets.py` | the same, plus echoing key variables, reading key files with shell tools, Python environment dumps, shell tracing, verbose curl |
| Pre-commit and commit-msg hooks | `.githooks/`, `scripts/scan_secrets.py` | committing staged content or a commit message that looks like a key |
| Session hook | `scripts/session_start.sh` | a session starting without the git hooks switched on |
| CI | `.github/workflows/ci.yml` | a leak or a failing test reaching a PR unnoticed |
| Budget | `src/llm.py` | a run spending past the cap in its `config.yaml` |
| `.gitignore` | `.gitignore` | `.env`, credentials, data and large files |

None of these is a sandbox: a script Claude writes can still read its own environment. They stop the common mistakes; CLAUDE.md's rules cover the rest.

Changes to any of these files go in a PR marked `[guardrail]`.
