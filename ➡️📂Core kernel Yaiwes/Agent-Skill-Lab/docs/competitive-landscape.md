# Competitive Landscape

**Research snapshot:** 2026-07-28

This document records why Agent Skill Lab should not be built as another generic
security scanner. It is an initial landscape, not a complete market analysis.

## Adjacent standards and platforms

### Agent Skills

The open Agent Skills format defines a folder containing `SKILL.md` and optional
scripts, references, and assets. It is designed for cross-product reuse.

Source: <https://agentskills.io/home>

### OpenClaw and ClawHub

ClawHub publishes text-based skills and defines OpenClaw-specific runtime metadata,
including required environment variables and binaries.

Sources:

- <https://github.com/openclaw/clawhub>
- <https://github.com/openclaw/clawhub/blob/main/docs/skill-format.md>

### Hermes Agent

Hermes documents compatibility with the open Agent Skills standard and supports
external skill directories and agent-managed skills.

Source:
<https://hermes-agent.nousresearch.com/docs/user-guide/features/skills>

### NanoClaw

NanoClaw uses skills as an installation and customization mechanism, including for
channels and alternative agent providers. Its runtime and packaging assumptions are
not identical to a passive `SKILL.md` knowledge package.

Sources:

- <https://github.com/nanocoai/nanoclaw>
- <https://nanoclaw.dev/skills/>

## Existing security tools

| Project | Primary focus | Notable capabilities | Implication for this project |
|---|---|---|---|
| NVIDIA SkillSpector | Skill security scanning | Static rules, optional semantic analysis, CVE lookup, risk reports, several input formats | Do not duplicate a broad pattern scanner |
| Cisco Skill Scanner | Best-effort threat detection | Static patterns, YARA, dataflow, semantic analysis, SARIF and CI | Reuse or integrate where appropriate |
| Snyk Agent Scan | Agent component inventory and security | Discovers skills and MCP servers, security analysis, enterprise monitoring | Inventory alone is not a sufficient differentiator |
| ClawHub scanning and metadata | Registry trust and platform metadata | Publishing rules, runtime requirements, registry-level analysis | Remain registry-independent |

Primary sources:

- <https://github.com/NVIDIA/SkillSpector>
- <https://github.com/cisco-ai-defense/skill-scanner>
- <https://github.com/snyk/agent-scan>
- <https://github.com/openclaw/clawhub>

## Observed gap to validate

The initial hypothesis is that existing tools emphasize threat detection, inventory,
or one platform's publication rules. Agent Skill Lab would instead combine:

- standards conformance;
- versioned cross-platform compatibility profiles;
- normalized capability declarations;
- deterministic functional test contracts;
- behavioral comparison across approved runtimes;
- security-engine composition with preserved provenance.

This is a hypothesis, not a proven market gap. It must be tested against real users and
fixtures before implementation expands.

## Differentiation rules

The project should stop or change direction if it cannot demonstrate at least one of:

- compatibility findings that established scanners do not report;
- useful normalized manifests across multiple platforms;
- reproducible tests that detect functional regressions;
- clearer evidence and remediation than platform-specific validators;
- a workflow that skill authors adopt in CI.

## Build-versus-integrate decisions

| Capability | Initial decision |
|---|---|
| Core format validation | Build |
| Platform compatibility profiles | Build |
| Capability manifest | Build conservatively |
| Generic malware pattern database | Integrate, do not lead |
| Dependency vulnerability scanning | Integrate established tools |
| LLM semantic judgment | Optional and deferred |
| Dynamic sandbox | Design first; build only after review |
| Public skill registry | Do not build |

## Research backlog

- Run representative skills through at least three existing scanners.
- Catalogue disagreements and false positives without assuming our interpretation is
  correct.
- Gather compatibility issues from public platform repositories.
- Interview maintainers about which failures block publication or installation.
- Compare report schemas and CI stability.
- Investigate licenses and APIs before integrating external engines.
