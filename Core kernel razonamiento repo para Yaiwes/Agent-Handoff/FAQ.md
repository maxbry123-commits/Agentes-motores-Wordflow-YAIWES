# FAQ

## What is Agent Handoff?

Agent Handoff is a GitHub-native standard for passing project context between AI coding agents, human maintainers, and human-supervised agents.

## Why not just use chat memory?

Chat memory is usually tied to one tool, session, or provider. Agent Handoff stores compact durable context in the repository, next to Issues, Pull Requests, and code history.

## Is this a replacement for README?

No. README explains the project to people. Agent Handoff adds workflow, ownership, compact memory, and handoff rules for agents and maintainers.

## Is this a replacement for GitHub Issues?

No. GitHub Issues and Pull Requests remain the source of work truth. Agent Handoff uses them as the coordination layer.

## What is stored in `ai/`?

Compact durable project state, decisions, protocols, and handoff indexes.

## Which language should this repository use?

This repository is maintained in English.

## Do branch names include Issue numbers?

No by default. Use meaningful branch names and link Issues through Work Claim comments, PR descriptions, GitHub links, and handoff metadata.

## Why should supporting-tool failures stay inside the current work item?

Test harnesses, smoke wrappers, evidence collectors, CI scaffolding, and similar tools usually exist to enable or prove another outcome. Turning every localized failure into a separate stage, handoff, or approval cycle can advance the process without advancing that outcome.

Agent Handoff therefore keeps reversible in-scope repairs and bounded post-fix verification inside the original execution envelope. The envelope records existing authorization and cannot be used by an agent to grant itself broader authority. A new owner decision is still required when the outcome, scope, architecture, accepted baseline, external effects, resource or risk boundary, security baseline, or enforced permission gate changes.

## What makes a blocking review actionable for an agent?

A blocking review gives each finding a stable ID and enough evidence, contract, outcome, invariant, scope, verification, and acceptance information for another agent to correct it without private chat history.

The reviewer may recommend an implementation, but that recommendation is not a hidden acceptance criterion. An equivalent safe correction remains valid when it satisfies the required outcome, preserves invariants, stays inside the execution envelope, and provides the required evidence.

An agent can report a finding as `addressed`; the reviewer or another authorized maintainer still verifies it before merge.
