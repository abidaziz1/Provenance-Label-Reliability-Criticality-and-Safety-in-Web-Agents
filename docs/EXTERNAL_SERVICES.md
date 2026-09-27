# External services and access

Use the narrowest credential that completes a task, set a provider-side spend cap before any paid run, and keep every secret outside Git, issues, pull requests, notebooks, and logs. Verify access with `scripts/preflight.py` before a new experiment.

## Required services

| Service | Use | Credential location | Notes |
| --- | --- | --- | --- |
| GitHub | Source, pull requests, and review | Git credential manager; Colab uses `GH_TOKEN_COLAB` | Scope a token to this repository and Contents read/write only. Never put it in a URL or notebook output. |
| Anthropic API | Approved model experiments | `RESEARCH_ANTHROPIC_API_KEY` | Use a workspace cap. Keep the research variable separate from the provider's default SDK variable. |
| OpenAI API | Approved comparison experiments | `OPENAI_API_KEY` | Use a project budget and record the exact model ID. |
| Hugging Face | Mind2Web download | Optional read-only `HF_TOKEN` | The dataset is public; a token only avoids rate limits. |

## Optional services

| Service | Use | Credential location | Notes |
| --- | --- | --- | --- |
| Google Gemini API | Optional comparison arm | `GEMINI_API_KEY` | Use a billing alert and record the model ID. |
| Docker Hub | Public image pulls if rate limited | `DOCKERHUB_USER`, `DOCKERHUB_TOKEN` | Read-only scope. |
| Slack | Optional maintainer notifications | `SLACK_WEBHOOK_URL` | Incoming webhook only; it is a secret. |

## Identity-bound actions

Email, OSF, Zenodo, arXiv, OpenReview, ScholarOne, repository settings, and releases are tied to the maintainer's identity. The maintainer reviews and submits them directly; credentials do not enter the repository.

Google Drive is not part of the project workflow. Code, results, and notes live in this repository. Large notebook outputs use the branch convention in [NOTEBOOK_GIT_CONVENTION.md](NOTEBOOK_GIT_CONVENTION.md).

## Rotation

Revoke credentials at the end of a phase or immediately after a suspected leak. Deleting a file does not remove a value from Git history. The repository scanner catches common provider formats, but it is a pattern check rather than a guarantee.
