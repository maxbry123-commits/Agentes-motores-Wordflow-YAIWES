---
type: refactoring_protocol
version: 1
status: active
updated: 2026-07-26
project: Agent_Handoff
---

# Refactoring Workflow

This file is a compact entry point for cleanup, decomposition, renaming, optimization, and internal restructuring.

Track concrete refactoring work in GitHub Issues.

Keep this file as protocol, not as a long backlog.

## Use for

- splitting large files;
- removing confirmed unused code;
- simplifying duplicated logic;
- optimizing existing functions;
- reducing module or layer coupling;
- clarifying ownership and source of truth;
- renaming confusing internal names;
- moving responsibilities to clearer modules.

## Issue fields

A refactoring Issue should include code area, current problem, target state, non-goals, invariants, compatibility boundaries, risk, required checks, and related files or PRs.

## Core rule

Refactoring is audit-first and layer-by-layer.

For every meaningful refactoring task, first define what should stay unchanged.

Keep external behavior unchanged unless the Issue explicitly allows behavior changes.

## Large refactoring

For large or multi-stage refactoring, create stages and follow `ai/TASK_REPORT_PROTOCOL.md`.

Each stage should materially advance the refactoring outcome, complete part of the stated acceptance proof, or document a verified out-of-envelope blocker. A stable supporting layer or repaired check is not a stage by itself. Record findings, make a small focused change, run targeted tests or explain why they were not run, and leave a stage result comment only at a legitimate outcome boundary.

## Baseline audit

For large refactoring, capture a baseline before changing runtime code.

Useful baseline items:

- size of the code area;
- largest files, functions, or classes;
- dependency count or heavy dependencies;
- current test count and runtime;
- migration or schema state when relevant;
- direct cross-layer call sites;
- compatibility layers;
- known risk zones;
- dead code candidates.

## Quality evidence

Use concrete evidence instead of one artificial score:

- size evidence;
- complexity evidence;
- architecture evidence;
- test evidence;
- performance evidence;
- data evidence;
- cleanup evidence;
- stage evidence.

When reporting refactoring results, compare before and after where practical.

Line count reduction is useful but not sufficient by itself.

Quality improves when boundaries are clearer, risks are lower, tests are stable, and future changes are easier.

## Finding classification

Classify findings before editing:

```text
delete now
refactor now
optimize now
keep as explicit compatibility boundary
move to separate issue
do not touch yet
```

If the work is larger than the current Issue scope, move it to a separate Issue.

## Safety rules

- Delete only confirmed dead code.
- Keep compatibility layers until call-site audit and tests are done.
- Use migrations and rollback notes for schema or storage changes.
- Keep unrelated refactoring types in separate stages.
- Preserve public APIs, routes, files, and data formats unless the Issue allows changes.

## Architecture boundaries

When refactoring boundaries, define the intended direction of dependencies.

Add or update lightweight architecture checks when practical.

## Function-level optimization

When optimizing existing functions, check for long functions, deep nesting, mixed responsibilities, repeated calls, calls inside loops, blocking work in async or UI paths, unclear error handling, and obsolete fallback branches.

For each optimization, document area, old problem, change, behavior impact, expected or measured benefit, and tests.

## Agent instruction

Perform the refactoring task described in the related GitHub Issue.

Before editing, read the required Agent Handoff files, related Issue or PR, current branch, recent commits, and active handoffs.

Before finishing, run checks, describe what changed and what was tested, list risks, and leave the required stage or final result comment.
