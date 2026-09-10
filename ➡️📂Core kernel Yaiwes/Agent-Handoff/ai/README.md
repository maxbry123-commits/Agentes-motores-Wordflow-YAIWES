---
type: ai_readme
version: 1
status: active
updated: 2026-07-27
project: Agent_Handoff
---

# Agent Memory Map

This folder stores compact repository memory.

It does not replace GitHub Issues, Pull Requests, checks, or Git history.

## Reading order

1. `AGENTS.md`
2. `AGENT_HANDOFF_STANDARD.md`
3. `ai/GITHUB_WORKFLOW.md`
4. `ai/HANDOFF_PROTOCOL.md`
5. `ai/AGENT_IDENTITY.md`
6. `ai/WORK_CLAIM_PROTOCOL.md`
7. `ai/TASK_REPORT_PROTOCOL.md`
8. `ai/REVIEW_PROTOCOL.md` when reviewing, responding to `changes-requested`, or resuming a PR with open blocking findings
9. `ai/PROJECT_STATE.md`
10. `ai/DECISIONS.md`
11. `ai/CONTAINERIZATION.md` when Docker or Compose is used, planned, present, or being discussed
12. related Issue or PR
13. `ai/REFACTORING.md` when relevant
14. `ai/handoffs/INDEX.md`
15. relevant handoff files only

## Files

- `PROJECT_STATE.md` — project snapshot.
- `DECISIONS.md` — durable decisions.
- `GITHUB_WORKFLOW.md` — coordinated GitHub workflow.
- `HANDOFF_PROTOCOL.md` — workflow protocol.
- `AGENT_IDENTITY.md` — agent identity protocol.
- `WORK_CLAIM_PROTOCOL.md` — work claim protocol.
- `TASK_REPORT_PROTOCOL.md` — required result comments.
- `REVIEW_PROTOCOL.md` — blocking review correction contracts, agent correction reports, and reviewer verification.
- `REFACTORING.md` — refactoring workflow.
- `CONTAINERIZATION.md` — user-controlled Docker and Compose layout decisions, supported approaches, migration rules, and checks.
- `handoffs/INDEX.md` — handoff index.

## Rules

Keep files compact.

Do not choose or migrate a container layout without explicit user confirmation during new-repository initialization or existing-repository adoption.
