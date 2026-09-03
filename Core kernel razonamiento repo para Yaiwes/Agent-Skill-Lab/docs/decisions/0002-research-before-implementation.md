# Decision 0002: Require research evidence before implementation

- **Status:** accepted
- **Date:** 2026-07-28

## Context

The agent skill security ecosystem is developing quickly. Several established
organizations and open-source maintainers already provide scanners, inventory tools,
signatures, governance cards, and registry checks.

Starting implementation immediately would risk duplicating existing work or defining a
compatibility model that does not reflect real platform differences.

## Decision

The project will complete a bounded Phase 0 study before selecting an implementation
language or building the CLI.

The study uses:

- a diverse candidate corpus;
- immutable sample pinning before analysis;
- a non-executing manual baseline;
- versioned platform profiles;
- isolated comparison of existing tools;
- a normalized result schema;
- explicit criteria for continuing, changing direction, or stopping.

## Implementation gate

Implementation requires evidence of:

- at least three repeatable compatibility or quality problems;
- at least two meaningful tool disagreements or equivalent coverage gaps;
- at least one useful deterministic, local, non-executing check.

## Consequences

### Positive

- product decisions remain evidence-based;
- security constraints are designed before untrusted inputs are processed;
- competitors become potential integration engines rather than assumed duplicates;
- the first implementation can target verified user problems.

### Cost

- visible code arrives later;
- the initial repository is documentation-heavy;
- sample licensing and reproducibility work requires care.

This delay is intentional and should be revisited only with new evidence.
