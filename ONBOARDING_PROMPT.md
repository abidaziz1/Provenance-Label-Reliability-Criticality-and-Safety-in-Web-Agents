# Prompts for Claude Code

Copy a prompt into a new session on this repository (claude.ai/code: pick the repo and the `idea3` environment, permission mode Auto). Everything Claude needs is in the repo; the prompts only point it at the right starting place. In a cloud session, one session produces one PR, so each prompt below is sized for one reviewable PR.

## 1. First session (kickoff)

```text
You are taking over the Idea 3 research project in this repository as my research assistant. I am Alam, the PI.

Read CLAUDE.md first. Then read docs/00_IMPORT_MANIFEST.md and the documents in docs/context/ in the order it gives, then ROADMAP.md, research/NOVELTY_LEDGER.md and research/BACKLOG_IDEAS.md.

Open a draft PR for this session's branch now, then do, in order, one commit or more per task:
1. Task 0.1: run python3 scripts/preflight.py and put the table in STATUS.md. Create the needs-human label and open one test issue titled "[needs-human] H1: alert check" asking me to confirm I was notified (this is row H1 in research/HUMAN_TASKS.md).
2. Task 0.2: fetch the data if it is missing, run the tests, rerun scripts/reconcile.py and scripts/descendant_only.py, and confirm git shows no change under results/. If anything changed, restore it with git checkout and report the difference. Confirm the v2.0-baseline tag exists.
3. Phase 0, the priority: N0.1 evidence inventory (add a test that recomputes each K1 to K12 value from its result file), then N0.2 with the novelty-auditor subagent for C1, C2 and C4. Search the literature fresh; never rely on the repo's own summaries of related work, and never invent a citation.
4. If time remains: drafts for tasks 1.1 and 1.2 in outreach/.

Work under the autonomy contract in CLAUDE.md. Open a needs-human issue for anything only I can do, then keep working. Never merge into main. End with /session-end and give me a five-line summary.
```

## 2. Resume (any later session)

```text
Continue the Idea 3 project. Run /status. Stack on my open work PRs as CLAUDE.md describes, open a draft PR for this session, then work through /next-task. Phase 0 and Gate N come before any Phase 3 spend. If the next task is a [guardrail], [prereg], [claim] or [gate] change, make it the only task in this session. Stop with /session-end before your context runs low.
```

## 3. Novelty focus (a session on the contribution only)

```text
This session is only about the contribution. Take the next unfinished rows in research/NOVELTY_LEDGER.md. Use the novelty-auditor subagent for a fresh search (classic security work counts: least privilege, the confinement problem, information flow, N-version programming), then the adversarial-reviewer subagent on the strongest surviving version. Judge each against the bar in the ledger: does the measurement predict or explain security outcomes beyond least-privilege reasoning? Update the rows and the verdict table. When every candidate has a verdict, draft research/CONTRIBUTION_STATEMENT.md in a session of its own and open the Gate N issue.
```

## 4. After you add keys

```text
I added these to the idea3 environment: <VARIABLE NAMES or API credential hosts, never values>. Run scripts/preflight.py, update STATUS.md, close the related needs-human issue, then start the tasks these unblock. Dry-run every paid experiment first and stay inside the budgets in ROADMAP.md.
```

## 5. After you finish a human task

```text
I finished needs-human #<number> (task <id>): <what I did, and where the result is: a colab/<id> branch, a file path, or an email reply pasted below>. Take it in (use colab-intake for a Colab run), update the ledgers and ROADMAP.md, close the issue, and continue.
```

## 6. A decision or a gate

```text
Decision on <gate or issue #>: <approve / approve with changes / reject>, because <reason>. Log it in research/DECISIONS.md, update ROADMAP.md and research/HUMAN_TASKS.md, and continue.
```

## 7. Weekly review (Mondays)

```text
Weekly review for the Idea 3 project in this repository. Read CLAUDE.md, STATUS.md, ROADMAP.md, research/HUMAN_TASKS.md and research/NOVELTY_LEDGER.md.
1) Competitor watch (task 1.12): search for a new version of arXiv:2607.08147 (Prismata) or its code, a new version of arXiv:2607.05277 (UCM), papers citing either, and new work on structural or DOM-based trust labeling, envelope or gate width, or information-flow defenses for web agents. Write research/competitor_watch/<today>.md with each hit, a link you opened, and which ledger candidate it touches. If anything overlaps a candidate's core claim, open an issue titled "[needs-human] 1.12: Gate 3 check".
2) Write research/weekly/<today>.md: open PRs and needs-human items I should clear, oldest first; human-task rows due in the next 14 days; spend against the budget; the plan for the week and whether the next gate is on track.
Change only research/competitor_watch/, research/weekly/ and research/HUMAN_TASKS.md, so this PR never conflicts with a work session. Open a PR titled "1.12: weekly review <date>", never merge it, and end with a ten-line summary.
```

## 8. Routines (optional, after a good first week)

Create at claude.ai/code/routines with this repo and the `idea3` environment; remove connectors the routine does not need. Routines run with no permission prompts and no one reading their chat, so the repo's deny rules, hook and CLAUDE.md are what keep them in bounds.

- **Weekly review**, weekly on Monday morning: prompt 7, verbatim.
- **Weekday work session**, weekdays, at most one a day: prompt 2 plus this line: "Finish one task or about two hours of work, whichever comes first. Nobody reads this session's chat: put anything for Alam in a needs-human issue, the PR body and STATUS.md."

Do not run a work routine while you have an interactive work session open on the same repo: two sessions would pick tasks in parallel.
