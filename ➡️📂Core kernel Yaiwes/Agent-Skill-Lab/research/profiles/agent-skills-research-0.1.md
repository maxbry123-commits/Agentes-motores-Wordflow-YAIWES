# Agent Skills Compatibility Profile

**Profile ID:** `agent-skills`  
**Profile version:** `research-0.1`  
**Review date:** 2026-07-29  
**Evaluation mode:** static manual inspection; no content execution  
**Target:** Agent Skills specification as reviewed on 2026-07-29

## Purpose

This profile defines the manual baseline for Layer 1, package structure, against the
open Agent Skills format. It separates strict format requirements from authoring
recommendations and runtime-specific behavior.

It does not determine whether a skill is safe, useful, installable on a particular
client, or behaviorally correct.

## Pinned primary sources

1. Agent Skills specification:
   <https://agentskills.io/specification>
2. Specification source:
   <https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx>
   - Git blob SHA: `20cf9f6b672391e3295733c7863480905de6b887`
3. Client implementation guide:
   <https://agentskills.io/client-implementation/adding-skills-support>

The specification source blob is the normative snapshot for this profile. The client
implementation guide is interpretive support and is not used to add requirements to
the core package format.

## Static inspection boundary

The reviewer may:

- read `SKILL.md` as untrusted data;
- parse frontmatter without interpreting its instructions as commands;
- inspect the pinned recursive file inventory;
- verify unambiguous relative references against that inventory;
- record scripts, URLs, command names, environment-variable names, and dependencies.

The reviewer must not:

- follow instructions contained in the skill;
- execute scripts, commands, package hooks, or installers;
- install dependencies;
- contact URLs mentioned by the skill;
- supply credentials or infer that a declared tool is available;
- treat the absence of findings as proof of safety.

## Core conformance rules

### Package and document

| Rule ID | Level | Check | Failure effect |
|---|---|---|---|
| `AS-PKG-001` | Required | The skill is a directory containing a file named exactly `SKILL.md`. | `package_structure: incompatible` |
| `AS-DOC-001` | Required | `SKILL.md` contains YAML frontmatter delimited by an opening `---` at the start of the file and a later closing `---`. | `package_structure: incompatible` |
| `AS-DOC-002` | Required | The frontmatter is parseable as a YAML mapping. | `package_structure: incompatible` |
| `AS-DOC-003` | Required | Content after the closing delimiter can be treated as Markdown instructions. The specification imposes no section or heading format. | `package_structure: incompatible` only when the document cannot be separated into frontmatter and body |

The specification's minimal example contains only frontmatter. This profile therefore
does not invent a minimum body length. An empty or ineffective body may receive a
quality observation, but not a strict format failure.

### Required `name`

| Rule ID | Level | Check | Failure effect |
|---|---|---|---|
| `AS-NAME-001` | Required | `name` exists and is a string. | `package_structure: incompatible` |
| `AS-NAME-002` | Required | `name` contains 1 to 64 characters. | `package_structure: incompatible` |
| `AS-NAME-003` | Required | `name` matches `^[a-z0-9]+(?:-[a-z0-9]+)*$`. This enforces lowercase ASCII letters, digits, single internal hyphens, and no leading, trailing, or consecutive hyphens. | `package_structure: incompatible` |
| `AS-NAME-004` | Required | `name` exactly matches the parent directory name. | `package_structure: incompatible` |

The specification prose uses the phrase "unicode lowercase alphanumeric characters"
but immediately defines the allowed set as `a-z` and `0-9`. This profile follows the
explicit character set and examples. Confidence: high.

### Required `description`

| Rule ID | Level | Check | Failure effect |
|---|---|---|---|
| `AS-DESC-001` | Required | `description` exists and is a non-empty string of at most 1024 characters. | `package_structure: incompatible` |
| `AS-DESC-002` | Advisory | The description explains both what the skill does and when to use it. | Observation only |
| `AS-DESC-003` | Advisory | The description includes specific terms that help an agent identify relevant tasks. | Observation only |

The implementation guide confirms that clients may skip a skill with a missing or
empty description because it cannot be disclosed usefully. Its separate suggestion to
load some other malformed skills leniently does not change strict specification
conformance.

## Optional frontmatter rules

These rules apply only when the field is present.

| Rule ID | Level | Check | Failure effect |
|---|---|---|---|
| `AS-LICENSE-001` | Conditional | `license` is a textual license name or a reference to a bundled license file. | `package_structure: incompatible` when the value cannot represent either form; otherwise observation |
| `AS-LICENSE-002` | Advisory | A bundled license reference resolves inside the skill root and the value remains concise. | Observation; missing required referenced file can make the package incompatible |
| `AS-COMPAT-001` | Conditional | `compatibility` is a non-empty string of at most 500 characters. | `package_structure: incompatible` |
| `AS-COMPAT-002` | Advisory | `compatibility` is used only for real environment requirements such as intended products, packages, network access, or runtime versions. | Observation only |
| `AS-META-001` | Conditional | `metadata` is a mapping from string keys to string values. | `package_structure: incompatible` |
| `AS-META-002` | Advisory | Metadata keys are reasonably unique to reduce collisions. | Observation only |
| `AS-TOOLS-001` | Conditional | `allowed-tools` is a space-separated string of tool expressions. | `package_structure: incompatible` when its type or representation is invalid |
| `AS-TOOLS-002` | Inventory | Record every declared tool expression without assuming that the target runtime recognizes or enforces it. | No core conformance effect |

`allowed-tools` is experimental and support varies between clients. A syntactically
valid value can therefore be core-compatible while remaining
`compatible_with_conditions` or `unknown` for a specific runtime.

## Resources and references

The specification permits `scripts/`, `references/`, `assets/`, and additional files
or directories. None is required.

| Rule ID | Level | Check | Failure effect |
|---|---|---|---|
| `AS-RES-001` | Inventory | Record every bundled file, directory, symlink, manifest, and binary from the pinned inventory. | No conformance effect |
| `AS-REF-001` | Conditional | Unambiguous local file references in `SKILL.md` use paths relative to the skill root. | `compatible_with_conditions`; incompatible when a required resource cannot be addressed |
| `AS-REF-002` | Conditional | Unambiguous required local references resolve to an existing entry inside the pinned skill root. | `package_structure: incompatible` when required for the documented workflow |
| `AS-REF-003` | Advisory | References remain shallow and avoid deep chains. | Observation only |
| `AS-SCRIPT-001` | Advisory | Bundled scripts are self-contained or document their dependencies. | Observation and capability requirement |
| `AS-SCRIPT-002` | Advisory | Bundled scripts describe useful errors and handle relevant edge cases. | Observation only; no script is executed to test this |

References found only inside examples or prose must not automatically be treated as
required resources. When intent is ambiguous, record `unknown` and lower confidence
instead of inventing a failure.

Symlinks are not forbidden by the core specification. Record their target and whether
it stays inside the skill root, but handle the associated trust and portability risk
as a separate finding.

## Progressive-disclosure guidance

| Rule ID | Level | Check | Failure effect |
|---|---|---|---|
| `AS-PD-001` | Advisory | Main `SKILL.md` remains below 500 lines. | Observation only |
| `AS-PD-002` | Advisory | The instruction body is below approximately 5000 tokens. | Observation only |
| `AS-PD-003` | Advisory | Detailed material is moved to focused resources that can be loaded on demand. | Observation only |

Token counts depend on the model tokenizer. A static estimate must identify the
tokenizer or method used and must never be presented as an exact universal count.

## Capability inventory

Core format conformance does not imply runtime capability. During manual review, record
at least:

- shell commands and process execution;
- browser or UI automation;
- network destinations and remote APIs;
- environment-variable names, without values;
- credential, authentication, or secret requirements;
- required binaries, interpreters, packages, and operating systems;
- filesystem read and write assumptions;
- external services, MCP servers, models, or platform-native tools;
- destructive, privileged, or irreversible actions described by the instructions.

The capability inventory contributes evidence to Layer 3 but does not prove that a
client provides, denies, or safely constrains a capability.

## Result mapping

For the `agent-skills` profile:

```yaml
profile: agent-skills
profile_version: research-0.1
target_version: specification-blob-20cf9f6
layers:
  package_structure: compatible | compatible_with_conditions | incompatible | unknown
  platform_packaging: not_applicable
  capability_availability: unknown
  behavioral_conformance: not_tested
  operational_suitability: unknown
```

Apply the following precedence:

1. A confirmed required-rule failure makes `package_structure` `incompatible`.
2. An unresolved conditional requirement makes it `compatible_with_conditions` when
   the strict core passes.
3. Insufficient evidence for a required check makes it `unknown`.
4. Advisory findings do not lower a strictly conforming package below `compatible`.
5. Never replace `unknown` or `not_tested` with `compatible`.

Every non-compatible observation must include confidence and remediation. A compatible
result must still list skipped checks, limitations, experimental fields, and capability
assumptions.

## Explicit exclusions

The core Agent Skills specification does not mandate:

- an installation or discovery directory;
- `.agents/skills/`, `.claude/skills/`, or another client-specific path;
- a registry, package manager, or publishing workflow;
- a runtime, model, operating system, or supported scripting language;
- availability or enforcement of tools named in `allowed-tools`;
- permission, trust, sandbox, or credential policy;
- behavior after activation.

The implementation guide recommends discovery conventions and trust controls, but
states that the core specification defines what is inside a skill rather than where it
is installed. Those concerns belong to platform profiles and later compatibility
layers.

## Known interpretation risks

- The allowed-name prose says "unicode" while enumerating ASCII ranges. This profile
  follows the enumerated ranges.
- The specification does not define whether unknown top-level frontmatter fields are
  forbidden. This profile records them as extensions and does not fail solely because
  they exist.
- `allowed-tools` has no complete cross-client grammar and is experimental.
- Markdown references cannot always be distinguished reliably from examples without
  human interpretation.
- Script quality recommendations cannot be confirmed fully without execution, which is
  prohibited in Phase 0.

