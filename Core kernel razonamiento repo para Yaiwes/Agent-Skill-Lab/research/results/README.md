# Manual Compatibility Results

This directory contains normalized, static manual baselines for the admitted corpus.

Each result:

- evaluates the portable Agent Skills core plus the OpenClaw and Hermes Agent profiles;
- uses only pinned source content and the recorded recursive inventory;
- records rule-level evidence, confidence, conditions, and explicit unknowns;
- leaves behavioral conformance `not_tested`;
- does not install or execute the inspected skill.

Results are research artifacts, not safety certifications or endorsements.

## Progress

| Sample | Name | Status |
|---|---|---|
| `ASL-C004` | `handoff` | [Pilot baseline complete](ASL-C004.yml) |
| `ASL-C005` | `autoreview` | [Baseline complete](ASL-C005.yml) |
| `ASL-C007` | `llm-wiki` | [Baseline complete](ASL-C007.yml) |

Nine admitted samples remain pending.
