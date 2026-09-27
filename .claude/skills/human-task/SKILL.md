---
name: human-task
description: Hand Alam a step only he can do (Colab run, key, account, domain, decision, annotation, outreach). Use instead of stopping to wait.
argument-hint: "<task-id> <what is needed>"
---
1. Write the request so it can be done without asking you anything: numbered steps, exact file or notebook paths, the Colab secret or environment variable names to set, how long it takes, what it costs, a date it is needed by, and exactly what to send back and where (a branch like `colab/<task-id>`, a file path, or a comment).
2. Never ask for a key's value in an issue, a file or chat. Ask Alam to set it in the cloud environment settings, in `.env` (local) or in Colab secrets, and give him the variable name.
3. Make sure the label exists (REST: `gh api repos/{owner}/{repo}/labels -f name=needs-human -f color=d93f0b`; an "already exists" error is fine).
4. Create the issue: `gh issue create --label needs-human --title "[needs-human] <task-id>: <short>" --body-file <tmp file>`. If the GitHub proxy rejects it, use REST: `gh api repos/{owner}/{repo}/issues -f title="[needs-human] <task-id>: <short>" -F body=@<tmp file> -f "labels[]=needs-human"`.
5. If both fail, write the full request into `research/HUMAN_TASKS.md`, put it at the top of STATUS.md and in the PR body, and post to Slack if `SLACK_WEBHOOK_URL` is set. A routine run has no one reading its chat.
6. Add or update the row in `research/HUMAN_TASKS.md` with the issue link, the need-by date and what it blocks.
7. If `SLACK_WEBHOOK_URL` is set, post one line with the issue link (no secrets, no results).
8. Continue with another unblocked task.
