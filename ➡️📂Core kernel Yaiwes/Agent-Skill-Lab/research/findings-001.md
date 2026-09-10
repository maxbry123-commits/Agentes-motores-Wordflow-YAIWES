# Initial Observations Before Scanner Execution

**Date:** 2026-07-28  
**Evidence stage:** public documentation and repository metadata only

No scanner results are reported here. These observations shape the first comparison.

## O-001 — The shared format does not eliminate platform differences

The open Agent Skills format supports cross-product reuse, but platforms add discovery
paths, installation behavior, metadata, available tools, and execution boundaries.

Examples:

- ClawHub documents OpenClaw-specific runtime metadata for required environment
  variables and binaries.
- Hermes uses its own source-of-truth skill directory and supports external skill
  directories.
- NanoClaw uses skills for operational instructions and for platform customization or
  installation workflows.

**Implication:** a syntax-only validator cannot make a complete portability claim.

Sources:

- <https://agentskills.io/home>
- <https://github.com/openclaw/clawhub/blob/main/docs/skill-format.md>
- <https://hermes-agent.nousresearch.com/docs/user-guide/features/skills>
- <https://github.com/nanocoai/nanoclaw>

## O-002 — Package integrity is broader than `SKILL.md`

Skills can include scripts, references, assets, and other resources. A valid
`SKILL.md` does not prove that the installed package is complete.

A public Hermes issue reports that installation from a direct `SKILL.md` URL fetched
only that file and omitted the supporting directories of a Supabase skill.

**Implication:** installation portability should compare a complete source tree with
the installed tree, not only parse frontmatter.

Sources:

- <https://agentskills.io/home>
- <https://github.com/NousResearch/hermes-agent/issues/35125>
- <https://github.com/supabase/agent-skills/tree/main/skills/supabase-postgres-best-practices>

## O-003 — Security scanning is already a competitive category

NVIDIA SkillSpector, Cisco Skill Scanner, and Snyk Agent Scan already cover overlapping
security concerns using static rules, semantic analysis, dataflow, inventory, and CI
outputs.

**Implication:** the project should integrate or compare specialist scanners rather
than lead with a duplicate generic malware detector.

Sources:

- <https://github.com/NVIDIA/SkillSpector>
- <https://github.com/cisco-ai-defense/skill-scanner>
- <https://github.com/snyk/agent-scan>

## O-004 — Scanner behavior is part of the threat model

Snyk Agent Scan documents that inspecting MCP configurations can execute configured
commands and recommends sandboxing for untrusted configurations. Cisco describes its
skill scanner as best-effort rather than certification.

**Implication:** the comparison methodology must record whether the analysis tool
executes or uploads inspected content. A security tool cannot automatically be treated
as a passive parser.

Sources:

- <https://github.com/snyk/agent-scan>
- <https://github.com/cisco-ai-defense/skill-scanner>

## O-005 — Provenance and evaluation artifacts are emerging

NVIDIA's skills catalog documents signed skill directories, skill cards, evaluation
datasets, and benchmark reports in addition to `SKILL.md`.

**Implication:** the compatibility model should allow governance and evaluation
artifacts without making them mandatory for the open core format.

Source: <https://github.com/NVIDIA/skills>

## O-006 — Static quality and behavioral value are separate questions

Recent research has begun evaluating authoring smells and whether skills improve task
outcomes. This suggests that a structurally valid and non-malicious skill may still be
low quality, stale, or behaviorally ineffective.

**Implication:** later test contracts should measure claimed outcomes rather than
equating clean static results with usefulness.

Sources:

- <https://arxiv.org/abs/2607.01456>
- <https://arxiv.org/abs/2603.15401>

## First hypotheses to test

1. Complete-package integrity checks reveal portability failures that security scanners
   do not prioritize.
2. Platform profiles produce useful findings beyond open-format validation.
3. Capability manifests can explain runtime assumptions more clearly than a single
   risk score.
4. Existing scanner outputs disagree enough to justify a normalized evidence layer.
5. Deterministic quality checks can identify problems without an LLM or execution.

## What would disprove the product thesis?

- Existing tools already report the same compatibility and package-integrity evidence
  with stable local outputs.
- Platform differences cannot be normalized without misleading users.
- Authors do not consider the resulting findings useful enough for CI.
- The only meaningful remaining checks require unsafe or expensive execution.
