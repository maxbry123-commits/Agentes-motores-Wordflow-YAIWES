---
type: task_report_protocol
version: 1
status: active
updated: 2026-07-27
project: Agent_Handoff
---

# Task Report Protocol

This file defines required result comments for GitHub Issues and Pull Requests.

Task reports are written in the related Issue or PR so humans and agents can follow progress without reading chat history.

## Rule

Every meaningful Issue needs a result comment.

Large or multi-stage Issues need one result comment after each legitimate outcome stage.

Small Issues may have one final result comment.

Risk reporting must distinguish verified blocking High or Critical risk, time-boxed investigation of suspected High or Critical risk, follow-up hardening, and owner-accepted risk. Security or evidence work may block acceptance or expand scope only for a verified High or Critical current-scope risk supported by reproducible evidence or a directly applicable authoritative source, or for an exactly cited acceptance criterion or verified mandatory requirement.

Every result report must identify the primary outcome, outcome progress, acceptance proof, supporting work, verified blocker, and next direct outcome step.

When an agent addresses blocking review findings, it must also write one Agent Handoff Review Correction Report in the Pull Request.

## Stage work

A stage result is appropriate only when the primary outcome materially advanced, the smallest acceptance proof completed, a verified blocker remains outside the execution envelope, or work is genuinely interrupted or transferred.

A supporting-tool failure or localized repair is not a stage by itself. Summarize routine supporting fixes and bounded post-fix verification in the next legitimate stage or final report.

## Review correction report

A correction report maps every blocking finding ID to the implementation response and verification evidence. It does not replace the required stage or final result comment and does not create an additional outcome stage by itself.

```md
## Agent Handoff Review Correction Report

Agent ID: <agent_id>
Run ID: <run_id>
Reviewed head: <commit reviewed by the blocking review>
Correction head: <commit containing the responses>

### RH-01

Status: addressed | disputed | blocked | not-addressed
Change: <files, behavior, or no change>
Implementation choice: <recommended approach or explained equivalent alternative>
Evidence: <tests, commands, observations, and expected results>
Preserved invariants: <what remains true>
Remaining concern: <risk, disagreement, blocker, or none>
```

Repeat the finding section for every blocking finding.

`Addressed` means the agent believes the correction contract is satisfied. It is not reviewer verification and must not automatically resolve a review thread.

## Stage result comment

```md
## Agent Handoff Stage Result

Stage: <number or name>
Agent ID: <agent_id>
Run ID: <run_id>
Status: completed | blocked | partial
Primary outcome: <observable behavior, artifact, decision, or capability>
Outcome progress: advanced | unchanged | completed | progress-stalled
Acceptance proof: <completed proof, current proof state, or not completed>
Supporting work: <minimum supporting work performed, or none>
Verified blocker: <out-of-envelope blocker, or none>

Findings:
- <what was found>

Changed:
- <small focused change>

Not changed:
- <explicit non-changes or preserved behavior>

Tests:
- <targeted tests and result, or reason not run>

Docs:
- <docs updated or not needed>

Commit:
- <commit sha or not committed yet>

Risks:
- Blocking: <verified High or Critical risk, exactly cited mandatory requirement, or none>
- Investigation: <time-boxed suspected High or Critical risk, or none>
- Follow-up hardening: <Low, Medium, unrated, unverified, or optional improvement, or none>
- Accepted: <risk explicitly accepted by the owner, or none>

Next direct outcome step:
- <shortest next step toward the primary outcome, completion, or handoff target>
```

## Final result comment

```md
## Agent Handoff Final Result

Agent ID: <agent_id>
Run ID: <run_id>
Status: completed | blocked | partial
Primary outcome: <observable behavior, artifact, decision, or capability>
Outcome progress: advanced | unchanged | completed | progress-stalled
Acceptance proof: <completed proof, current proof state, or not completed>
Supporting work: <minimum supporting work performed, or none>
Verified blocker: <out-of-envelope blocker, or none>

Summary:
- <what was done>

Changed:
- <files, modules, docs, or behavior changed>

Not changed:
- <explicit non-changes or preserved behavior>

Tests:
- <checks and smoke tests, or reason not run>

Docs:
- <docs updated or not needed>

Commits:
- <commit shas>

Risks:
- Blocking: <verified High or Critical risk, exactly cited mandatory requirement, or none>
- Investigation: <time-boxed suspected High or Critical risk, or none>
- Follow-up hardening: <Low, Medium, unrated, unverified, or optional improvement, or none>
- Accepted: <risk explicitly accepted by the owner, or none>

Next direct outcome step:
- <next outcome work, follow-up, or none>
```

## Outcome gate

A multi-stage Issue moves to the next stage after the current legitimate outcome stage has a result comment and its acceptance proof is stable, or an out-of-envelope blocker is documented.

If two consecutive updates or proposed stages report unchanged outcome progress and only supporting work, mark the work `progress-stalled` and replan the shortest path before creating another stage.
