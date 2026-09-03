# Decision 0001: Build a test lab, not another generic scanner

- **Status:** accepted
- **Date:** 2026-07-28

## Context

The project began with the idea of helping users detect malicious agent skills across
platforms such as OpenClaw, Hermes Agent, NanoClaw, Codex, and others.

Initial research found a rapidly growing set of specialist security products,
including NVIDIA SkillSpector, Cisco Skill Scanner, Snyk Agent Scan, and several
projects already using the name "SkillScan." These tools cover static rules, semantic
analysis, dataflow, dependency checks, inventory, CI output, and some behavioral
analysis.

Building another broad scanner would create substantial duplication and weak
differentiation.

## Decision

Agent Skill Lab will focus on a vendor-neutral combination of:

- structural conformance;
- cross-platform compatibility profiles;
- normalized capability and permission manifests;
- reproducible functional test contracts;
- explicit evidence and uncertainty;
- optional composition of established security scanners.

Security remains a required dimension, but is not the sole product identity.

The working project name is **Agent Skill Lab**. "SkillScan" will not be used as the
project name because it is already used by multiple security tools and describes a
narrower product.

## Consequences

### Positive

- clearer differentiation;
- reduced duplication of mature security engines;
- broader value for authors, reviewers, users, and platform maintainers;
- less dependence on any one agent ecosystem;
- a path from static validation to reproducible behavioral testing.

### Costs

- compatibility profiles require continuous maintenance;
- behavioral claims need representative runtime fixtures;
- normalized permissions can oversimplify platform differences;
- the product may initially appeal to a narrower technical audience.

## Guardrails

- Do not claim universal safety certification.
- Do not execute untrusted content in the MVP.
- Do not hide the provenance of external scanner findings.
- Do not claim platform compatibility without versioned evidence.
- Revisit this decision if user research shows no meaningful compatibility or testing
  gap.
