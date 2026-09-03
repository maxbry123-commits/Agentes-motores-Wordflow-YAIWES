# Roadmap

This roadmap is outcome-based. Dates will be added only after the discovery phase
produces credible estimates.

## Phase 0 — Foundation

**Status:** completed with a narrowed product decision

- define the product thesis and non-goals;
- document the competitive landscape;
- establish the initial threat model;
- define the compatibility model;
- gather representative public skill fixtures;
- compare the compatibility findings with an established security scanner;
- define a narrow, evidence-backed v0.1 boundary.

Current research artifacts:

- [Research plan](research/README.md)
- [Methodology](research/methodology.md)
- [Candidate corpus](research/corpus.yml)
- [Result schema](research/result-schema.md)
- [Initial observations](research/findings-001.md)
- [SkillSpector comparison](research/skillspector-execution-001.md)
- [Version 0.1 scope](docs/v0.1-scope.md)

**Exit criteria**

- at least three repeatable compatibility or quality gaps are documented — met;
- an established scanner leaves equivalent deterministic gaps — met;
- Agent Skills, OpenClaw, and Hermes profiles use pinned primary sources — met;
- the v0.1 scope requires no execution of inspected content — met.

## Phase 1 — Deterministic inspector

**Status:** next decision gate; implementation has not started

- review the six rule families in the [v0.1 scope](docs/v0.1-scope.md);
- define deterministic fixtures and expected findings for every rule;
- discover and load one local skill directory;
- reject unsafe paths, links, oversized inputs, and directory escapes;
- parse `SKILL.md` metadata and local directory contents;
- emit evidence for metadata, symlink, prerequisite, permission, disclosure, and
  privileged-setup findings;
- export stable terminal and JSON reports;
- validate against three completed samples and up to three targeted additions;
- collect one independent usefulness signal before broadening the implementation.

**Exit criteria**

- no network or LLM is needed for baseline inspection;
- inspected files are never executed;
- report results are deterministic;
- each finding includes a source location and rule identifier;
- false positives and unsupported cases remain explicit;
- at least one independent author or maintainer confirms a finding changes a decision.

## Phase 2 — Compatibility profiles

**Status:** deferred until the v0.1 proof passes

- stabilize versioned profiles for Agent Skills, OpenClaw, and Hermes Agent;
- distinguish syntax support from runtime capability support;
- produce a compatibility matrix and remediation suggestions;
- add profile conformance fixtures supplied or reviewed by platform users;
- consider additional runtimes only after the initial profiles demonstrate user value.

## Phase 3 — Developer workflow

**Status:** deferred

- publish a standalone CLI package;
- add pre-commit and GitHub Actions integrations;
- compare reports between skill versions;
- support machine-readable policy thresholds;
- integrate established third-party security scanners as optional engines;
- preserve each engine's name, version, raw result, and limitations.

## Phase 4 — Behavioral lab

**Status:** deferred

- design isolated runners with no ambient credentials;
- use deny-by-default filesystem and network policies;
- define reproducible task scenarios and expected outcomes;
- record tool calls, file access, network attempts, and process execution;
- compare declared intent with observed behavior;
- add explicit approval gates before any untrusted execution.

Behavioral execution will not be released until the sandbox threat model has received
independent review.

## Phase 5 — Accessible interface

**Status:** deferred

- provide a local visual interface for non-specialists;
- explain findings without removing technical evidence;
- add guided remediation for authors;
- support signed and reproducible report bundles;
- evaluate an optional hosted collaboration service without weakening local-first use.

## Ideas deliberately deferred

- a public skill registry;
- universal safety certification;
- automated installation of untrusted skills;
- autonomous remediation without review;
- proprietary rules required for baseline operation.
