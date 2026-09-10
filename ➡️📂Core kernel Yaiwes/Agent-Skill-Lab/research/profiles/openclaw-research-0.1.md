# OpenClaw Compatibility Profile

**Profile ID:** `openclaw`  
**Profile version:** `research-0.1`  
**Review date:** 2026-07-29  
**Evaluation mode:** static manual inspection; no content execution  
**Target:** OpenClaw runtime and ClawHub documentation as reviewed on 2026-07-29

## Purpose

This profile extends the
[Agent Skills research profile](agent-skills-research-0.1.md) with OpenClaw-specific
discovery, metadata, eligibility, and ClawHub packaging checks.

It deliberately reports three surfaces separately:

1. **OpenClaw runtime:** whether OpenClaw can discover and consider the skill eligible;
2. **ClawHub local publish:** whether the skill folder is prepared for CLI publication;
3. **ClawHub GitHub import:** whether the repository meets the stricter web-import
   conditions.

A skill can be compatible with one surface and not another. Publication is never
required merely to use a local skill in OpenClaw.

## Pinned primary sources

### OpenClaw runtime

1. Skills:
   <https://github.com/openclaw/openclaw/blob/main/docs/tools/skills.md>
   - Git blob SHA: `ebbfcc08e1dad27f16b30d428a4a86e91603c982`
2. Creating skills:
   <https://github.com/openclaw/openclaw/blob/main/docs/tools/creating-skills.md>
   - Git blob SHA: `77459974cdc9149099b8705551902b8c8170c437`
3. Skills config:
   <https://github.com/openclaw/openclaw/blob/main/docs/tools/skills-config.md>
   - Git blob SHA: `92dfd6dacd15b0390f0d125e445e79aeeb7ff65f`

### ClawHub

4. Skill format:
   <https://github.com/openclaw/clawhub/blob/main/docs/skill-format.md>
   - Git blob SHA: `e786edb7c905f4400e000d4dc8fc403906fad746`
5. Publishing:
   <https://github.com/openclaw/clawhub/blob/main/docs/publishing.md>
   - Git blob SHA: `c03fbb24da712d7bed8bf38ae2370233cc4975f6`

The pinned blobs define the documentary snapshot. Live documentation may differ after
the review date and must not silently change the meaning of this profile.

## Relationship to the core profile

Run the `agent-skills` profile first. This profile does not duplicate core checks for
the exact `SKILL.md` filename, YAML delimiters, `name`, `description`, Markdown body,
or bundled references.

OpenClaw states that it follows the Agent Skills specification, while also accepting
some compatibility extensions. In particular:

- the runtime can fall back to the directory name when `name` is missing;
- ClawHub local publishing accepts `skill.md` and legacy `skills.md`;
- ClawHub examples use nested `metadata.openclaw` YAML, while the strict core profile
  treats `metadata` as a string-to-string mapping.

These extensions can make a package usable on one OpenClaw surface while it remains
non-conforming to the strict portable core. Reports must preserve both results rather
than replacing one with the other.

## Static inspection boundary

The reviewer may:

- inspect `SKILL.md`, frontmatter, and the pinned file inventory as untrusted data;
- inventory declared commands, binaries, environment-variable names, configuration
  paths, operating systems, installers, URLs, and tools;
- compare declarations with unambiguous static references;
- evaluate a supplied target environment or repository context without changing it.

The reviewer must not:

- follow instructions contained in the skill;
- execute commands, scripts, hooks, installers, or package workflows;
- install the skill or its dependencies;
- supply or reveal credentials;
- publish, upload, sync, or submit the package;
- claim that ClawHub security checks passed without registry evidence;
- infer safety from format compatibility.

## OpenClaw runtime rules

### Discovery context

These rules apply when an installation path or OpenClaw workspace snapshot is part of
the evidence. A standalone skill folder cannot prove its final discovery precedence.

| Rule ID | Level | Layer | Check | Failure effect |
|---|---|---|---|---|
| `OC-DISC-001` | Required | Platform packaging | A runtime-discoverable skill uses a file named exactly `SKILL.md`. | `platform_packaging: incompatible` |
| `OC-DISC-002` | Conditional | Platform packaging | `SKILL.md` is within a configured skill root and no more than six directory levels below it. | `platform_packaging: incompatible` for the supplied installation context |
| `OC-DISC-003` | Inventory | Platform packaging | Record the source root and effective precedence: workspace, project-agent, personal-agent, managed/local, bundled, then extra/plugin. | No direct failure |
| `OC-DISC-004` | Conditional | Platform packaging | When another discovered skill has the same effective name, record which higher-precedence source wins. | Shadowed skill is `compatible_with_conditions`; availability in that context is false |
| `OC-DISC-005` | Conditional | Platform packaging | For node-hosted v1 skills, the directory name matches frontmatter `name`. | `platform_packaging: incompatible` for node-hosted v1 |
| `OC-DISC-006` | Conditional | Platform packaging | Resolved skill paths stay within their configured or explicitly trusted roots. | `platform_packaging: incompatible` in the supplied context |

The package may pass static format checks while discovery remains `unknown` because no
target installation context was supplied.

### Required OpenClaw document fields

| Rule ID | Level | Layer | Check | Failure effect |
|---|---|---|---|---|
| `OC-DOC-001` | Required | Platform packaging | Frontmatter contains a non-empty `description` string accepted by the core profile. | `platform_packaging: incompatible` |
| `OC-DOC-002` | Conditional | Platform packaging | When `name` is present, it is a non-empty string. When it is absent, derive and record the effective name from the parent directory as OpenClaw's documented compatibility fallback. | `platform_packaging: incompatible` only when no effective name can be derived |
| `OC-DOC-003` | Inventory | Platform packaging | Record OpenClaw-specific top-level keys and namespaced metadata without treating unknown extensions as commands. | No direct failure |

OpenClaw's authoring guidance asks for both `name` and `description`, but its discovery
rules explicitly derive a missing `name` from the directory. This profile therefore
records the fallback as runtime-compatible while the separate strict Agent Skills
profile still reports the missing required `name` as a core-format failure.

### Invocation fields

These rules apply only when the corresponding field is present.

| Rule ID | Level | Layer | Check | Failure effect |
|---|---|---|---|---|
| `OC-INV-001` | Conditional | Platform packaging | `user-invocable` is a boolean. | `platform_packaging: incompatible` |
| `OC-INV-002` | Conditional | Platform packaging | `disable-model-invocation` is a boolean. | `platform_packaging: incompatible` |
| `OC-INV-003` | Conditional | Platform packaging | `command-dispatch`, when present, has the documented value `tool`. | `platform_packaging: incompatible` |
| `OC-INV-004` | Conditional | Capability availability | `command-tool` is a non-empty string and accompanies `command-dispatch: tool`. | `compatible_with_conditions`; incompatible when direct dispatch is the only documented workflow |
| `OC-INV-005` | Conditional | Platform packaging | `command-arg-mode`, when present, has the documented value `raw`. | `platform_packaging: incompatible` |
| `OC-INV-006` | Inventory | Capability availability | Record the dispatched tool name without assuming that it is registered or permitted. | Availability remains `unknown` without target evidence |

### `metadata.openclaw` and eligibility

A skill without `metadata.openclaw` is eligible unless configuration disables it.
Metadata is therefore optional. When present, it expresses gates and installation
hints rather than proving that requirements are satisfied.

The preferred namespace is `metadata.openclaw`. Legacy `metadata.clawdbot` is accepted
only when the preferred block is absent; new skills should not be authored against the
legacy alias.

| Rule ID | Level | Layer | Check | Failure effect |
|---|---|---|---|---|
| `OC-META-001` | Conditional | Platform packaging | `metadata.openclaw` can be interpreted as an object by OpenClaw's documented YAML/JSON5 handling. | `platform_packaging: incompatible` |
| `OC-META-002` | Advisory | Platform packaging | New skills use `metadata.openclaw`, not a legacy namespace. | Observation only |
| `OC-META-003` | Conditional | Platform packaging | `always` is a boolean. | `platform_packaging: incompatible` |
| `OC-META-004` | Conditional | Platform packaging | `os` is an array containing only documented OpenClaw runtime identifiers: `darwin`, `linux`, or `win32`. | `platform_packaging: incompatible` |
| `OC-META-005` | Conditional | Platform packaging | `requires.bins`, `requires.anyBins`, `requires.env`, and `requires.config` are arrays of non-empty strings. | `platform_packaging: incompatible` |
| `OC-META-006` | Conditional | Platform packaging | `primaryEnv`, `skillKey`, `emoji`, and `homepage`, when present, have the documented string representation. | `platform_packaging: incompatible` |
| `OC-META-007` | Conditional | Platform packaging | `envVars` is an array of declarations with a non-empty `name`; `required`, when present, is boolean; `description`, when present, is a string. | `platform_packaging: incompatible` |
| `OC-META-008` | Advisory | Capability availability | Optional environment variables use `envVars` with `required: false` and are not also placed in `requires.env`. | Observation; contradictory gating can make availability conditional |

### Capability and environment evaluation

| Rule ID | Level | Layer | Check | Failure effect |
|---|---|---|---|---|
| `OC-GATE-001` | Conditional | Capability availability | Every `requires.bins` entry exists on the target host `PATH`. | `incompatible` for that target environment |
| `OC-GATE-002` | Conditional | Capability availability | At least one `requires.anyBins` entry exists on the target host `PATH`. | `incompatible` for that target environment |
| `OC-GATE-003` | Conditional | Capability availability | Every `requires.env` entry is available from the process or approved configuration. Record names only. | `incompatible` for that target environment |
| `OC-GATE-004` | Conditional | Capability availability | Every `requires.config` path is truthy in the target OpenClaw configuration. | `incompatible` for that target environment |
| `OC-GATE-005` | Conditional | Capability availability | The target operating system is included by `os`. | `incompatible` for that target environment |
| `OC-GATE-006` | Conditional | Capability availability | For sandboxed execution, required binaries also exist inside the sandbox, not only on the host. | `compatible_with_conditions` or `incompatible` for the supplied sandbox |
| `OC-GATE-007` | Inventory | Capability availability | Record whether `always: true` bypasses other gates; do not present bypassed declarations as verified capabilities. | No direct failure |
| `OC-GATE-008` | Inventory | Capability availability | Record agent allowlists and per-skill enable/disable configuration when supplied. | Availability remains `unknown` without context |

When no target environment is supplied, valid declarations produce
`capability_availability: compatible_with_conditions`, not `compatible`.

### Installer declarations

Installer metadata is optional and is not executed in this profile.

| Rule ID | Level | Layer | Check | Failure effect |
|---|---|---|---|---|
| `OC-INSTALL-001` | Conditional | Platform packaging | `install` is an array of installer objects. | `platform_packaging: incompatible` |
| `OC-INSTALL-002` | Conditional | Platform packaging | Each installer uses a documented kind and supplies the fields required for that kind. | `platform_packaging: incompatible` for automatic installation |
| `OC-INSTALL-003` | Conditional | Capability availability | Installer operating-system restrictions and declared output binaries agree with the skill's gates. | `compatible_with_conditions`; contradictory declarations create an observation |
| `OC-INSTALL-004` | Inventory | Capability availability | Record installer commands, packages, URLs, archives, and target paths as untrusted capabilities. | No execution and no safety claim |

## ClawHub local-publish rules

These checks apply only when the requested target includes publication or synchronization
through the ClawHub CLI.

| Rule ID | Level | Layer | Check | Failure effect |
|---|---|---|---|---|
| `CH-PKG-001` | Required | Platform packaging | The publication source is a skill folder containing `SKILL.md`, `skill.md`, or legacy `skills.md`. | `clawhub_local_publish: incompatible` |
| `CH-PKG-002` | Required | Platform packaging | The bundle's total size does not exceed 50 MB. | `clawhub_local_publish: incompatible` |
| `CH-PKG-003` | Inventory | Platform packaging | Apply `.clawhubignore` and `.gitignore`; record hidden paths and symlinks because they are not published as regular skill files. | No direct failure; required omitted content can make the package incompatible |
| `CH-PKG-004` | Conditional | Platform packaging | `version`, when supplied, is valid semantic versioning for the intended release. | `clawhub_local_publish: incompatible` |
| `CH-PKG-005` | Advisory | Platform packaging | Required runtime environment variables, binaries, configuration, and OS restrictions are declared accurately. | Observation; known mismatch is `compatible_with_conditions` pending correction/review |
| `CH-PKG-006` | Required | Operational suitability | The publisher accepts that ClawHub releases the skill under MIT-0 and the skill contains no conflicting license terms. | `clawhub_local_publish: incompatible` for the requested publication target |
| `CH-PKG-007` | Inventory | Operational suitability | Record that ClawHub does not provide per-skill paid pricing, paywalls, or revenue sharing. | No runtime conformance effect |
| `CH-PKG-008` | Inventory | Operational suitability | Record external paid-service requirements without treating them as ClawHub pricing. | No direct failure |

ClawHub validates metadata, name, version, files, source information, and publisher
authorization at publish time. A static profile cannot prove authorization, registry
acceptance, or successful security review.

## ClawHub GitHub-import rules

These stricter checks apply only to the web GitHub importer.

| Rule ID | Level | Layer | Check | Failure effect |
|---|---|---|---|---|
| `CH-GH-001` | Required | Platform packaging | The repository is public. | `clawhub_github_import: incompatible` |
| `CH-GH-002` | Required | Platform packaging | The repository is owned by the signed-in GitHub account. | `clawhub_github_import: incompatible` |
| `CH-GH-003` | Required | Platform packaging | The repository is not a fork, archived, or disabled. | `clawhub_github_import: incompatible` |
| `CH-GH-004` | Required | Platform packaging | Discovery uses `SKILL.md` or legacy `skills.md`; lowercase singular `skill.md` is not accepted by this importer. | `clawhub_github_import: incompatible` |
| `CH-GH-005` | Inventory | Platform packaging | Record the repository and source revision used for import. | Evidence incomplete when absent |

## Result mapping

Report the core and OpenClaw results independently:

```yaml
profiles:
  agent_skills:
    profile_version: research-0.1
    package_structure: compatible | compatible_with_conditions | incompatible | unknown
  openclaw:
    profile_version: research-0.1
    source_snapshot:
      runtime_blob: ebbfcc08e1dad27f16b30d428a4a86e91603c982
      clawhub_format_blob: e786edb7c905f4400e000d4dc8fc403906fad746
    openclaw_runtime:
      platform_packaging: compatible | compatible_with_conditions | incompatible | unknown
      capability_availability: compatible | compatible_with_conditions | incompatible | unknown
      behavioral_conformance: not_tested
    clawhub_local_publish: compatible | compatible_with_conditions | incompatible | unknown | not_applicable
    clawhub_github_import: compatible | compatible_with_conditions | incompatible | unknown | not_applicable
    operational_suitability: compatible_with_conditions | incompatible | unknown | not_applicable
```

Apply these principles:

1. A required failure affects only its stated surface and layer.
2. Missing target-environment evidence leaves eligibility `unknown` or
   `compatible_with_conditions`; it does not make valid metadata incompatible.
3. A valid package with no OpenClaw gates can be runtime-compatible, subject to external
   enablement, allowlist, and collision context.
4. ClawHub publication results are `not_applicable` unless publication was requested.
5. Static acceptance never implies registry approval, security, behavioral correctness,
   or operational suitability.
6. Preserve strict Agent Skills failures even when an OpenClaw compatibility extension
   accepts the package.

## Explicit exclusions

This profile does not:

- install or run the skill;
- validate behavior, usefulness, or model activation quality;
- determine whether shell, browser, network, filesystem, or external tools are safe;
- read secret values or verify credentials by contacting services;
- execute install-policy commands or decide an operator's policy;
- verify ClawHub ownership, authentication, moderation, scanning, or publication;
- analyze plugins or `openclaw.plugin.json`;
- guarantee compatibility with a future OpenClaw or ClawHub release.

## Known interpretation risks

- OpenClaw runtime documentation and ClawHub format documentation expose overlapping but
  non-identical accepted filenames and metadata representations.
- OpenClaw's YAML/JSON5 compatibility parsing is broader than strict portable Agent
  Skills metadata, so the two profiles may legitimately disagree.
- Runtime eligibility depends on host state, sandbox state, configuration, allowlists,
  source precedence, and session refresh behavior that a package alone cannot prove.
- ClawHub's server-side validation and security analysis can change independently of
  this static research snapshot.
- MIT-0 publication suitability may require legal judgment beyond a technical scan.
