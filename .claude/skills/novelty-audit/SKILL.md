---
name: novelty-audit
description: Run the Phase 0 novelty audit on one candidate contribution or all of them. Use for tasks N0.1 to N0.5 and whenever a new claim appears.
argument-hint: "[candidate id from research/NOVELTY_LEDGER.md, or all]"
---
1. Read research/NOVELTY_LEDGER.md and the evidence files each candidate cites.
2. For each candidate in scope, delegate to the novelty-auditor subagent (fresh literature search, closest work quoted, verdict).
3. Then delegate the surviving version of each claim to the adversarial-reviewer subagent.
4. Update the ledger row: closest works with links, delta, verdict, what evidence would upgrade it, the experiment in ROADMAP.md that produces that evidence, and the reviewer's most damaging sentence.
5. When all candidates have verdicts, draft research/CONTRIBUTION_STATEMENT.md: 2 or 3 primary contributions, each one sentence, each tied to evidence and a falsification test. Open a needs-human issue asking Alam to approve it (Gate N).
