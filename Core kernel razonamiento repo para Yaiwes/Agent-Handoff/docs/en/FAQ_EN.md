# FAQ

Agent Handoff FAQ.

## Why should supporting-tool failures stay inside the current work item?

Test harnesses, smoke wrappers, evidence collectors, CI scaffolding, and similar tools usually exist to enable or prove another outcome. Turning every localized failure into a separate stage, handoff, or approval cycle can advance the process without advancing that outcome.

Agent Handoff therefore keeps reversible in-scope repairs and bounded post-fix verification inside the original execution envelope. The envelope records existing authorization and cannot be used by an agent to grant itself broader authority. A new owner decision is still required when the outcome, scope, architecture, accepted baseline, external effects, resource or risk boundary, security baseline, or enforced permission gate changes.

## What makes a blocking review actionable for an agent?

A blocking review gives each finding a stable ID and enough evidence, contract, outcome, invariant, scope, verification, and acceptance information for another agent to correct it without private chat history.

Implementation guidance remains non-binding when an equivalent safe correction satisfies the required outcome, preserves invariants, stays inside the execution envelope, and provides the required evidence.

Agent-reported `addressed` status still requires verification by the reviewer or another authorized maintainer.
