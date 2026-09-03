---
type: work_claim_protocol
version: 1
status: active
updated: 2026-07-26
project: Agent_Handoff
---

# Work Claim Protocol

This file defines current work ownership in GitHub Issues and Pull Requests.

## Before starting work

1. Read the Issue.
2. Check linked Pull Requests.
3. Check active handoffs.
4. Choose `agent_name`, `agent_id`, and `run_id`.
5. Leave a work claim comment.
6. Record the primary outcome, smallest acceptance proof, and execution envelope.
7. Plan only legitimate stage or final result reports using `ai/TASK_REPORT_PROTOCOL.md`.
8. Create a branch and Draft PR early.

## Claim comment

```md
## Agent Handoff Work Claim

Agent: <agent_name>
Agent ID: <agent_id>
Run ID: <run_id>
Coordinator: <coordinator>
Supervision: autonomous | human-supervised | human-driven
Started: YYYY-MM-DD HH:MM UTC
Issue: #<issue-number>
Branch: <branch-name>
Draft PR: #<pr-number or TBD>
Scope: <short scope>
Primary outcome: <observable behavior, artifact, decision, or capability>
Smallest acceptance proof: <minimum demonstration, check, or evidence>
Execution envelope: <already-authorized scope, verification runs, resource limits, external effects, and separate approval boundaries>
Status: in-progress
Next update: <time or condition>
```

The execution envelope records existing authorization and MUST NOT be used by an agent to create or widen its own authority.

## Update comment

```md
## Agent Handoff Work Update

Agent ID: <agent_id>
Run ID: <run_id>
Status: in-progress | blocked | completed
Primary outcome:
Outcome progress: advanced | unchanged | completed | progress-stalled
Acceptance proof:
Supporting work:
Verified blocker:
Changed:
Tested:
Risk:
Next direct outcome step:
```

Use `progress-stalled` after two consecutive updates that report unchanged outcome progress and advance only supporting work. Then stop optional supporting work, restate the shortest path, move non-blocking work to follow-up or backlog, and continue within the execution envelope or request one decision only when an approval boundary has been crossed.

## Result comments

Every meaningful Issue must have result comments.

Large or multi-stage Issues use stage result comments after each legitimate outcome stage.

Small Issues use one final result comment before completion.

Use `ai/TASK_REPORT_PROTOCOL.md` for templates.

## Done

When work is finished, write what changed, what was tested, remaining risks, related PR or handoff, and the required result comment.

If an Issue or PR already has a recent work claim, coordinate before continuing.
