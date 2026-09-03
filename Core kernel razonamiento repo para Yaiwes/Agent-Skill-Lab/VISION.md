# Vision

## Mission

Make AI agent skills easier to trust, test, and reuse across platforms.

## The problem

Agent skills are moving toward a shared folder-based format, but portability is not
binary. Platforms may interpret metadata differently, expose different tools, use
different install paths, or impose different execution boundaries.

At the same time, a structurally valid skill can still:

- request undeclared capabilities;
- depend on unavailable tools or environment variables;
- contain ambiguous or conflicting instructions;
- behave differently across agents and models;
- include unsafe scripts or supply-chain dependencies;
- fail silently while appearing compatible.

Security scanners address important malicious patterns, but authors and users also
need conformance, portability, permission transparency, and repeatable functional
testing.

## Product thesis

A vendor-neutral test lab can provide value by combining:

1. a standards-aware structural validator;
2. platform-specific compatibility profiles;
3. a normalized capability and permission manifest;
4. reproducible functional test scenarios;
5. optional integrations with established security scanners;
6. evidence-based reports with explicit uncertainty.

## Primary users

### Skill authors

They need to validate a skill before publishing it and understand which platforms it
supports.

### Maintainers and reviewers

They need stable reports in pull requests and a clear view of changes in capabilities
between versions.

### Agent users

They need a comprehensible explanation of what a skill may do before installing it.

### Runtime and registry maintainers

They need reusable fixtures and compatibility tests without adopting a competing
runtime.

## What success looks like

The project will be useful when:

- a new user can inspect a skill locally with one command;
- the same input produces deterministic baseline results;
- every finding contains evidence and remediation guidance;
- compatibility claims are tied to versioned profiles and fixtures;
- reports distinguish declared, inferred, observed, and unknown behavior;
- platform maintainers can correct profiles without rewriting the core;
- the project can integrate external scanners without hiding their provenance;
- tests include benign, malformed, ambiguous, and adversarial samples.

## Long-term direction

Agent Skill Lab may eventually become a shared conformance and test ecosystem, with:

- a CLI and local visual interface;
- a versioned compatibility database;
- CI integrations;
- sandboxed behavioral runners;
- signed, reproducible reports;
- community-maintained platform profiles;
- optional hosted collaboration for teams.

The open-source local workflow will remain the foundation.

## Boundaries

Agent Skill Lab will not:

- certify that a skill is absolutely safe;
- operate as a skill marketplace;
- silently execute untrusted content;
- require a specific model provider;
- optimize for one agent at the expense of the core format;
- treat a numerical risk score as a substitute for evidence.
