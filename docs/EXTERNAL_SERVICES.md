# External services and access

What each outside service is for, what kind of access it needs, exactly what Alam creates, and where it goes. The rule behind every row: the narrowest credential that does the job, a spend cap set at the provider, never a value in the repo or in chat, rotated at the end of this phase.

"Cloud" means the Claude Code cloud environment settings (`docs/OPERATIONS.md` section 2). "Local" means `.env` on Alam's machine. "Colab" means the Colab secrets panel (key icon in the left sidebar), with notebook access switched on for this notebook only.

## Needed

| Service | Used for (tasks) | Access type | What you create | Scope and cap | Where it goes | Rotate |
| --- | --- | --- | --- | --- | --- | --- |
| GitHub, for Claude Code | everything | GitHub App, OAuth | Install the Claude GitHub App on this repository only (github.com/apps/claude, "Only select repositories") | This repo | Nothing to paste. The GitHub proxy keeps the credential outside the session VM | Uninstall or narrow the app when done |
| Anthropic API, research key | 2.2, 2.4, 2.5, 2.8, 3.2 to 3.5, 4.1, 4.2, 5.6 | API key | In the Claude Console, a new workspace `idea3-research` and a key in it | Workspace spend limit $100 for Phase 2; raise to $300 a month from Phase 3 | Cloud: environment variable `RESEARCH_ANTHROPIC_API_KEY`. Local: `.env`. Colab: secret `RESEARCH_ANTHROPIC_API_KEY` | End of phase, or at once after any leak |
| OpenAI API | 2.2, 3.1, 3.2, possibly 2.5 | API key | A new project `idea3` and a project key | Project budget $60 | Cloud: API credential for `api.openai.com` plus `OPENAI_API_KEY=proxy-injected` (or the key itself as a variable on plans without API credentials). Local: `.env`. Colab: secret `OPENAI_API_KEY` | same |
| GitHub, for Colab | 1.13, 2.7, every Colab arm | Fine-grained personal access token | github.com/settings/personal-access-tokens: this repository only; Contents read and write; Metadata read (added automatically); 90-day expiry | One repo; cannot touch other repos, issues or settings | Colab secret `GH_TOKEN_COLAB`. Never in the cloud environment | Renew before the 90 days run out (task 5.6 needs it in late January), and at end of phase |

## Optional

| Service | Used for | Access type | What you create | Scope and cap | Where it goes | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Google Gemini API | 2.3, Gemini arm of 3.2 | API key | Google AI Studio key on a project with billing | A Google Cloud budget alert of $15 (alerts notify, they do not stop spend) | Cloud: API credential for `generativelanguage.googleapis.com`, header `x-goog-api-key`, plus `GEMINI_API_KEY=proxy-injected`. Colab: secret `GEMINI_API_KEY` | If preflight shows 200, Claude runs the arm; otherwise it becomes a Colab task |
| Hugging Face | Mind2Web download | Read token | huggingface.co/settings/tokens, type Read | Read only | Cloud: API credential for `huggingface.co`, or variable `HF_TOKEN`. Local: `.env` | The dataset is public; a token only avoids rate limits |
| Docker Hub | 1.9, 2.5, 3.3 image pulls | Personal access token | hub.docker.com, Account settings, Personal access tokens, "Public Repo Read-only" | Read only | Cloud: `DOCKERHUB_USER` and `DOCKERHUB_TOKEN` variables; Claude logs in with `docker login -u "$DOCKERHUB_USER" --password-stdin <<< "$DOCKERHUB_TOKEN"` | Only if anonymous pulls hit the rate limit |
| Slack | Pings when a needs-human issue opens | Incoming webhook URL (it is a secret) | api.slack.com/apps: new app, Incoming Webhooks on, one channel | Posts to one channel, reads nothing | Cloud: variable `SLACK_WEBHOOK_URL` and `hooks.slack.com` in the allowlist | Recommended if you want pings: Claude's issues and PRs appear under your own GitHub account, and GitHub does not notify you about your own activity. Without Slack, check the needs-human issue list daily |

## Not needed, and why

| Service | Decision |
| --- | --- |
| Google Drive | Not used. Code, results and notes live in this repo; large Colab outputs go to orphan `data/<task-id>` branches (`docs/NOTEBOOK_GIT_CONVENTION.md`). Colab can still mount your Drive for its own scratch space under your login; Claude never needs it. If a later task truly needs Drive, the options are, in order: a claude.ai Google Drive connector with OAuth, enabled only for the session that needs it (broad: it reaches your whole Drive); or a Google Cloud service account shared on one folder, whose JSON key would have to sit in an environment variable where the session can read it. Decide then, not now. |
| AWS | Only for optional task 2.6, which you run yourself. Never give Claude AWS keys. If you run it: a separate IAM user or role with the least privilege the UCM README needs, and an AWS Budgets alarm. |
| OSF, Zenodo, arXiv, OpenReview or ScholarOne, email | Tied to your identity. Claude drafts; you submit (1.1, 1.2, 1.6, 5.4, 6.2, 6.3). No credentials leave your hands. |
| A GitHub token inside the cloud environment | Not needed: `gh` in cloud sessions works through the GitHub proxy with the placeholder `proxy-injected`. A token you set there would be readable by every session. |

## Where each secret must never be

In the repo (any file, any branch), in an issue or PR, in chat, in a notebook cell, in a commit message, in `research/` or `docs/`, in a log. `scripts/scan_secrets.py` blocks the common key formats at commit time, but it is a net, not a guarantee.

## Rotation checklist (end of phase)

1. Anthropic Console: delete the `idea3-research` key; make a new one only if work continues.
2. OpenAI: revoke the project key.
3. Google AI Studio: delete the Gemini key.
4. GitHub: delete `GH_TOKEN_COLAB`; narrow or uninstall the Claude GitHub App if the repo is done.
5. Hugging Face, Docker Hub, Slack webhook: revoke if created.
6. Cloud environment: delete the API credentials and clear the variables; archive the environment if unused.
7. Colab: delete the secrets from the notebook's secrets panel.
8. Ask Claude to note the rotation date in RESEARCH_LOG.md (names only).
