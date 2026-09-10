---
type: github_workflow
version: 1
status: active
updated: 2026-07-27
project: Agent_Handoff
---

# Coordinated GitHub Flow

Agent Handoff uses Coordinated GitHub Flow for medium repositories.

## Work unit

One work item should have one Issue, one scope, one primary outcome, one smallest acceptance proof, one execution envelope, one short-lived branch, one Pull Request, one visible owner, and required result reporting.

## Status labels

- `needs-triage`
- `ready`
- `in-progress`
- `blocked`
- `in-review`
- `changes-requested`
- `ready-to-merge`

Closed Issue or merged PR is the normal `done` state.

Finding-level states such as `open`, `addressed`, and `verified` are recorded in review threads or correction reports and are not additional status labels.

## Branch naming

Use meaningful branch names without `/`, Issue numbers, or random identifiers by default.

Issue linkage belongs in the Work Claim comment, PR description, GitHub links, and handoff metadata.

## Result reports

Every meaningful Issue must have a result comment.

Large or multi-stage Issues use stage result comments after legitimate outcome stages.

Small Issues use one final result comment.

Use `ai/TASK_REPORT_PROTOCOL.md`.

## Review correction loop

Use `ai/REVIEW_PROTOCOL.md` for Pull Request review and `changes-requested` work.

A blocking finding must carry a sufficient correction contract. The implementation agent maps each finding ID to the change and evidence in an Agent Handoff Review Correction Report.

The agent may report a finding as `addressed`, but only the reviewer or another authorized maintainer marks it `verified`.

The normal Pull Request transition is:

```text
in-review -> changes-requested -> in-review -> ready-to-merge
```

Return to `in-review` when the correction report and required checks are available. Use `ready-to-merge` only after all blocking findings are verified or otherwise validly dispositioned and required checks pass.

## Workflow

1. Create or select an Issue.
2. Mark it `ready` when scope is clear.
3. Choose agent identity when an agent is involved.
4. Claim work before editing.
5. Record the primary outcome, smallest acceptance proof, and execution envelope.
6. Create a short-lived branch.
7. Open a Draft PR early.
8. Link the PR to the Issue.
9. Keep discussion and result reports in Issue or PR.
10. Keep supporting work subordinate and handle localized fixes and bounded post-fix verification inside the current work item.
11. Run checks and smoke tests.
12. When review requests changes, address stable blocking finding IDs and write a correction report.
13. Return to review and keep agent-reported `addressed` separate from reviewer-confirmed `verified`.
14. Finish only after checks, review, verified or validly dispositioned blocking findings, and required result reporting.
15. Add a handoff only at a legitimate outcome boundary, blocker, interruption, or transfer.
