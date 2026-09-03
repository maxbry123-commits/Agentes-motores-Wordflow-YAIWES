# Compatibility Model

## Goal

Describe compatibility as evidence across layers, not as a single yes/no label.

## Compatibility layers

### Layer 1 — Package structure

Can the skill be discovered and parsed as a folder-based Agent Skill?

Examples:

- required `SKILL.md`;
- valid frontmatter;
- valid name and description;
- resolvable bundled resources.

### Layer 2 — Platform packaging

Does the target platform recognize the skill's location, metadata, naming, and install
method?

Examples:

- OpenClaw-specific metadata;
- Hermes skill directories and discovery;
- NanoClaw build-time customization conventions;
- Codex or Claude Code skill discovery paths.

### Layer 3 — Capability availability

Does the target runtime provide the tools or environment that the skill assumes?

Examples:

- shell execution;
- browser control;
- MCP servers;
- required binaries;
- environment variables;
- filesystem mounts.

### Layer 4 — Behavioral conformance

Does the skill complete defined scenarios with expected outcomes on the target runtime?

This layer requires approved execution and is deferred beyond the static MVP.

### Layer 5 — Operational suitability

Is the skill appropriate under the user's policy, privacy, and deployment constraints?

This cannot be reduced to technical compatibility alone.

## Result vocabulary

- **Compatible:** all checks in the evaluated layers passed.
- **Compatible with conditions:** required configuration or capabilities are explicit.
- **Incompatible:** a known requirement cannot be satisfied.
- **Unknown:** the relevant layer was not tested or cannot be determined.
- **Not applicable:** the check does not apply to the target.

Every result must identify which layers were evaluated.

## Initial profiles

| Profile | Planned static scope | Primary references |
|---|---|---|
| Agent Skills | [Research profile 0.1](../research/profiles/agent-skills-research-0.1.md): core folder and metadata conformance | <https://agentskills.io/specification> |
| OpenClaw / ClawHub | [Research profile 0.1](../research/profiles/openclaw-research-0.1.md): runtime discovery, eligibility, and optional ClawHub publication surfaces | <https://github.com/openclaw/openclaw/blob/main/docs/tools/skills.md> and <https://github.com/openclaw/clawhub/blob/main/docs/skill-format.md> |
| Hermes Agent | [Research profile 0.1](../research/profiles/hermes-agent-research-0.1.md): runtime discovery, conditional activation, setup declarations, and optional distribution surfaces | <https://hermes-agent.nousresearch.com/docs/user-guide/features/skills> |
| NanoClaw | Deferred beyond the initial Phase 0 baseline | Primary sources to be pinned if the profile is resumed |
| Codex | Deferred beyond the initial Phase 0 baseline | Official Codex documentation to be pinned if the profile is resumed |
| Claude Code | Deferred beyond the initial Phase 0 baseline | Official Claude Agent Skills documentation to be pinned if the profile is resumed |

The Agent Skills, OpenClaw, and Hermes Agent research profiles are now defined. The
remaining platform profiles are explicitly deferred until this narrower baseline has
demonstrated value.

## Versioning

Profiles will be versioned independently from the CLI because platforms can change
without a core release.

A report should record:

- Agent Skill Lab version;
- report schema version;
- profile name and version;
- target platform version or range, when known;
- rule identifiers and versions;
- configuration and skipped checks.

## Portability principle

Platform-specific metadata is allowed, but the report should separate:

- portable core information;
- namespaced platform extensions;
- requirements that cannot be represented elsewhere;
- transformations that would lose behavior or meaning.

Automatic conversion must never silently discard unsupported information.
