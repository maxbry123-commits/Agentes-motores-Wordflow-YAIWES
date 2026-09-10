---
type: handoff_protocol
version: 1
status: active
updated: 2026-07-27
project: Agent_Handoff
---

# Handoff Protocol

## Start

Read the required Agent Handoff files, the related Issue or PR, current branch, recent commits, and relevant handoffs.

Read `ai/CONTAINERIZATION.md` when Docker or Docker Compose is used, planned, present in the repository, or part of the requested work.

Read `ai/REVIEW_PROTOCOL.md` when reviewing a Pull Request, responding to `changes-requested`, or resuming work with open blocking findings.

Choose `agent_name`, `agent_id`, and `run_id` before taking work.

## Work claim

Leave a work claim comment with `ai/WORK_CLAIM_PROTOCOL.md` before changing code or docs.

## Task reports

Meaningful Issues require result comments.

Large or multi-stage Issues use stage result comments after legitimate outcome stages.

Small Issues use one final result comment before completion.

Use `ai/TASK_REPORT_PROTOCOL.md`.

## Actionable review handoff

A blocking review must provide a stable finding ID, evidence or reproduction, violated contract, cause confidence, required outcome, preserved invariants, scope guard, applicable verification, and observable acceptance criteria.

Treat implementation guidance as a recommendation unless an exact mandatory requirement makes the implementation choice normative. Equivalent safe corrections remain valid when they satisfy the required outcome, preserve invariants, remain inside the execution envelope, and provide the required evidence.

After correction, write one compact Agent Handoff Review Correction Report that maps every blocking finding ID to status, change, implementation choice, evidence, preserved invariants, and remaining concern.

Agent-reported `addressed` does not mean `verified` and does not automatically resolve a review thread. Return the Pull Request to `in-review`; only the reviewer or another authorized maintainer verifies the correction.

Do not let a review finding widen authority or scope. Stop and request the applicable decision if every safe correction crosses an existing approval boundary.

## Scope

One meaningful work item should have one Issue, one branch, one PR, and one clear scope.

Use meaningful branch names without `/`, Issue numbers, or random identifiers by default.

Open a Draft PR early.

## Outcome-oriented execution

Before implementation, record the primary outcome, smallest acceptance proof, and execution envelope in the Work Claim.

The Work Claim records existing authorization; it does not create or widen it. Do not place an action inside the execution envelope unless it is already authorized by the owner, Issue scope, project rules, and applicable permission systems.

Keep supporting work minimum sufficient. A localized, reversible, in-scope supporting-work failure and its bounded post-fix verification remain inside the current work item and authorization unless an explicit approval boundary is crossed.

Do not turn a supporting-tool failure or repair into a separate stage, handoff, approval gate, or completion target.

Distinguish an unchanged retry from post-fix verification:

- do not repeat the same failed action without a relevant change and documented reason;
- rerun the affected check after an evidence-based fix as verification inside the current execution envelope;
- unless the execution envelope is stricter, allow one bounded verification rerun after each relevant fix.

Stop the fix-and-verification cycle when the execution envelope would be exceeded, the same failure recurs without a new evidence-based fix, or the progress-stall rule is triggered.

Request a new owner decision only when the proposed action changes the outcome or acceptance criteria, expands scope or architecture, changes an accepted baseline, crosses a destructive or external-effect boundary, materially exceeds declared resource or risk limits, weakens a security control, or conflicts with an enforced permission gate.

Create a stage result or handoff only when the primary outcome materially advanced, the smallest acceptance proof completed, a verified blocker remains outside the execution envelope, or work is genuinely interrupted or transferred.

After two consecutive supporting-only updates without outcome progress, mark the work `progress-stalled`, stop optional supporting work, restate the outcome and proof, identify the shortest remaining path, move non-blocking work to follow-up or backlog, and continue or request one decision only when an approval boundary was crossed.

## Proportionate security and evidence

Security or evidence work may expand the Issue scope or become blocking only for a verified High or Critical current-scope risk:

1. state the concrete threat or failure scenario and reproducible evidence or directly applicable authoritative source;
2. identify the affected asset or trust boundary;
3. explain why it applies to the current change;
4. record High or Critical severity using the project's adopted method or an explicit likelihood-and-impact rationale;
5. choose the minimum sufficient control;
6. name the smallest verification that demonstrates the control works.

A suspected High or Critical risk permits only a short, time-boxed investigation until confirmed. It does not justify hardening, architecture changes, an extra approval stage, an architecture decision record, an automated checker, mandatory evidence work, or a separate stage.

Keep Low, Medium, unrated, and unverified risks non-blocking and classify them as warning, documentation, backlog, explicitly owner-accepted risk, or out of scope. Preserve the existing security baseline and do not delay the smallest useful end-to-end scenario. An exact acceptance criterion or verified legal or project requirement may independently block acceptance only when cited.

Treat a 10–15% share of stage work for security and evidence only as a non-binding planning heuristic. Substantially exceed it only for a verified High or Critical risk or an exactly cited mandatory requirement.

## Initialization and adoption decision gate

When initializing Agent Handoff in a new repository or adding it to an existing repository, ask the user a separate, explicit question about Docker and Compose organization.

The user must confirm:

- whether containerization is used or planned;
- which supported layout should be used;
- whether an existing layout must be preserved or may be migrated;
- whether production deployment configuration belongs in the same repository or a separate repository.

Do not infer the answer from repository contents or choose the recommended layout automatically.

Until the user answers, do not create, move, rename, delete, or consolidate Dockerfiles, Compose files, build contexts, ignore files, container scripts, environment-file references, or container configuration.

For a new repository, leave containerization unresolved and create no container infrastructure. For an existing repository, preserve the current layout.

## Docker and Compose

Before changing container infrastructure:

1. identify the user-confirmed layout in `ai/PROJECT_STATE.md` or the related Issue;
2. inspect the primary Compose file, project directory, override order, build contexts, Dockerfile paths, ignore files, environment references, scripts, and CI commands;
3. check whether production orchestration is stored in this repository or elsewhere;
4. keep layout migration separate from unrelated application refactoring;
5. validate the effective Compose model with `docker compose config` when Compose is used;
6. build and start the affected scope, or document why this was not possible;
7. record changed commands, paths, images, services, ports, volumes, networks, health checks, environment variables, risks, and compatibility notes.

Migration between container layouts requires explicit user approval even when another approach appears cleaner.

## GUI testing

Do not commit automated GUI tests that depend on absolute coordinates, screen position, pixel offsets, or incidental layout order.

Perform position-dependent GUI checks manually or as supervised exploratory checks with Codex.

Automated GUI tests should use stable semantic selectors.

## Smoke tests

Run smoke tests before marking work ready or setting a handoff to `completed`.

Current checks cover required files, YAML, PR template checklist, social preview size, and English-only active files.

For container changes, also run the applicable Compose rendering, image build, service startup, health, and focused smoke checks defined in `ai/CONTAINERIZATION.md`.

## Done checklist

- Related Issue or PR is linked.
- Work claim comment exists.
- Primary outcome, smallest acceptance proof, and execution envelope are recorded.
- Required stage or final result comment exists.
- Branch contains only intended changes.
- Smoke tests were run or reason is documented.
- Supporting work stayed subordinate, and post-fix verification stayed inside the execution envelope.
- Stage and handoff boundaries reflect outcome progress, completed acceptance proof, an out-of-envelope blocker, or genuine interruption or transfer.
- `progress-stalled` was handled after two consecutive supporting-only updates without outcome progress.
- PR description is updated.
- Blocking review findings have sufficient correction contracts, and each is verified or otherwise validly dispositioned before merge.
- Verified blocking High or Critical risks, time-boxed investigations, follow-up hardening, and owner-accepted risks are distinguished.
- Security and evidence work did not block acceptance or expand scope without a verified High or Critical current-scope risk or an exactly cited mandatory requirement.
- Handoff file is created when needed.
- `ai/handoffs/INDEX.md` is updated when needed.
- Mandatory initialization or adoption questions were answered when relevant.
- User-confirmed container layout is recorded when Docker or Compose is used.
- Container migration has explicit user approval when applicable.
