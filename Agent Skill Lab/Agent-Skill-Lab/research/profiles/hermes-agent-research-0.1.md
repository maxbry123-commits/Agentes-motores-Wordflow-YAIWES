# Hermes Agent Compatibility Profile

**Profile ID:** `hermes-agent`  
**Profile version:** `research-0.1`  
**Review date:** 2026-07-29  
**Evaluation mode:** static manual inspection; no content execution  
**Target:** Hermes Agent skills runtime and distribution documentation as reviewed on
2026-07-29

## Purpose

This profile extends the
[Agent Skills research profile](agent-skills-research-0.1.md) with Hermes-specific
discovery, metadata, conditional activation, setup, and distribution checks.

It reports three surfaces separately:

1. **Hermes runtime:** discovery, visibility, setup declarations, and capability
   assumptions;
2. **Hermes Hub installation:** bundle completeness, provenance, and the limits of
   static security evidence;
3. **Hermes GitHub tap:** the optional repository layout used to distribute skills.

A local skill does not need to be published or installed through the Hub. Passing a
format check does not prove that the skill is safe or that its documented procedure
works.

## Pinned primary sources

1. Skills System:
   <https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/skills.md>
   - Git blob SHA: `1857648c1f45177c3a961cc6700ab6c90541c375`
2. Creating Skills:
   <https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/creating-skills.md>
   - Git blob SHA: `25d023ed57c826d473a451b83921103e4f465d56`
3. Working with Skills:
   <https://github.com/NousResearch/hermes-agent/blob/main/website/docs/guides/work-with-skills.md>
   - Git blob SHA: `2a011a2b7bf57d17652cec98eb4fa907b1307334`
4. Hermes Agent Skill Authoring:
   <https://github.com/NousResearch/hermes-agent/blob/main/skills/software-development/hermes-agent-skill-authoring/SKILL.md>
   - Git blob SHA: `b8a9dc2fd7f050e98777c723b636a98c99c33743`

The pinned blobs define the documentary snapshot. Live documentation and runtime
behavior may change after the review date.

## Relationship to the core profile

Run the `agent-skills` profile first. This profile does not duplicate core checks for
the `SKILL.md` document, `name`, `description`, body, and bundled resources.

Hermes declares compatibility with the Agent Skills open standard and also accepts
Hermes-specific nested metadata and backward-compatible fallbacks. Reports must retain
both results. A Hermes extension must not silently turn a strict core-format failure
into portable conformance.

## Static inspection boundary

The reviewer may:

- inspect skill files and frontmatter as untrusted data;
- inventory declared tools, toolsets, platforms, settings, environment-variable names,
  credential filenames, scripts, commands, URLs, and automation metadata;
- compare exact local references with the pinned file inventory;
- evaluate a supplied Hermes configuration or environment without changing it;
- record external provenance and existing scanner evidence without trusting it blindly.

The reviewer must not:

- follow the skill's instructions;
- load the skill into Hermes;
- execute scripts, inline shell snippets, commands, installers, or automations;
- collect, display, or test secret values;
- install, update, publish, or schedule the skill;
- use `--force` to bypass a policy decision;
- claim safety because a static scan has no findings.

## Hermes runtime rules

### Discovery and precedence

| Rule ID | Level | Layer | Check | Failure effect |
|---|---|---|---|---|
| `HA-DISC-001` | Required | Platform packaging | A discoverable skill directory contains a file named exactly `SKILL.md`. | `platform_packaging: incompatible` |
| `HA-DISC-002` | Conditional | Platform packaging | The skill is under the active profile's `~/.hermes/skills/` tree or a configured `skills.external_dirs` root. | `platform_packaging: incompatible` for the supplied installation context |
| `HA-DISC-003` | Inventory | Platform packaging | Record the local or external source root and the effective skill name. | No direct failure |
| `HA-DISC-004` | Conditional | Platform packaging | When a local and external skill share a name, record that the local skill shadows the external one. | Shadowed skill is `compatible_with_conditions`; visibility is false in that context |
| `HA-DISC-005` | Conditional | Platform packaging | Each configured external directory resolves after documented `~` and `${VAR}` expansion. | `unknown` or `incompatible` for the supplied context |
| `HA-DISC-006` | Inventory | Operational suitability | Record whether an external directory is writable by Hermes; configuration alone is not a write-protection boundary. | Observation only |

A missing external directory is silently skipped by Hermes. That is not a malformed
skill, but it means the skill is unavailable in the evaluated context.

### Document and progressive disclosure

| Rule ID | Level | Layer | Check | Failure effect |
|---|---|---|---|---|
| `HA-DOC-001` | Required | Platform packaging | The skill supplies the core `name` and `description` needed for the skill index and slash-command discovery. | `platform_packaging: incompatible` |
| `HA-DOC-002` | Inventory | Platform packaging | Record optional `version`, `author`, `license`, `platforms`, Hermes metadata, environment, and credential declarations. | No direct failure |
| `HA-DOC-003` | Advisory | Platform packaging | The body clearly states when to use the skill, its procedure, pitfalls, and verification guidance. | Observation only |
| `HA-DOC-004` | Advisory | Platform packaging | Common instructions stay in `SKILL.md`; detailed references and supporting material are loaded on demand. | Observation only |
| `HA-DOC-005` | Advisory | Platform packaging | The trigger and distinctive behavior are clear near the start of the description because Hermes truncates long descriptions in its prompt index; the `/learn` authoring path targets approximately 60 characters. | Observation only |

Hermes enforces the core maximum of 1024 characters, while its authoring reference says
the prompt index shows the first 57 characters plus an ellipsis. The approximately
60-character guidance belongs to the `/learn` authoring path; it is not a separate
format limit or runtime incompatibility threshold.

### Platform visibility

| Rule ID | Level | Layer | Check | Failure effect |
|---|---|---|---|---|
| `HA-PLAT-001` | Conditional | Platform packaging | `platforms`, when present, is an array containing only `macos`, `linux`, or `windows`. | `platform_packaging: incompatible` |
| `HA-PLAT-002` | Conditional | Capability availability | The evaluated operating system is included in a non-empty `platforms` list. | `incompatible` for that target environment |
| `HA-PLAT-003` | Inventory | Capability availability | Record that an omitted or empty `platforms` list is visible on all supported platforms. | No direct failure |

An incompatible platform hides the skill from the system-prompt index, `skills_list`,
and slash commands. It does not mean the underlying Markdown package is malformed.

### Conditional tool and toolset activation

The following fields live under `metadata.hermes`.

| Rule ID | Level | Layer | Check | Failure effect |
|---|---|---|---|---|
| `HA-ACT-001` | Conditional | Platform packaging | `requires_toolsets`, `requires_tools`, `fallback_for_toolsets`, and `fallback_for_tools` are arrays of non-empty strings. | `platform_packaging: incompatible` |
| `HA-ACT-002` | Conditional | Capability availability | Every `requires_toolsets` entry is available in the supplied session. | `incompatible` for that session; skill is hidden |
| `HA-ACT-003` | Conditional | Capability availability | Every `requires_tools` entry is available in the supplied session. | `incompatible` for that session; skill is hidden |
| `HA-ACT-004` | Conditional | Capability availability | No listed `fallback_for_toolsets` entry is available in the supplied session. | `not_applicable` as a fallback when a listed primary toolset exists |
| `HA-ACT-005` | Conditional | Capability availability | No listed `fallback_for_tools` entry is available in the supplied session. | `not_applicable` as a fallback when a listed primary tool exists |
| `HA-ACT-006` | Inventory | Capability availability | Record all referenced names without assuming that a similarly named command or tool exists. | Availability remains `unknown` without session evidence |

When no session inventory is supplied, syntactically valid activation declarations
produce `capability_availability: compatible_with_conditions`, not `compatible`.

### Environment variables and secrets

`required_environment_variables` declares setup needs without hiding the skill from
discovery. Missing values can be skipped, so the affected feature may remain
unavailable even while the skill loads.

| Rule ID | Level | Layer | Check | Failure effect |
|---|---|---|---|---|
| `HA-ENV-001` | Conditional | Platform packaging | `required_environment_variables` is an array of objects. | `platform_packaging: incompatible` |
| `HA-ENV-002` | Conditional | Platform packaging | Every declaration has a non-empty string `name`; optional `prompt`, `help`, and `required_for` values are strings. | `platform_packaging: incompatible` |
| `HA-ENV-003` | Advisory | Platform packaging | New skills use `required_environment_variables`, not legacy `prerequisites.env_vars`. | Observation only |
| `HA-ENV-004` | Inventory | Capability availability | Record variable names and the features identified by `required_for`; never record values. | No direct failure |
| `HA-ENV-005` | Conditional | Capability availability | Variables required for the evaluated feature are configured for the target environment. | `compatible_with_conditions` or `incompatible` for that feature |
| `HA-ENV-006` | Inventory | Operational suitability | Record the interaction surface: local CLI may prompt securely; messaging surfaces must direct setup locally rather than request secrets in chat. | No format effect |

Static analysis cannot prove Hermes' runtime secret-handling behavior or the validity
of a credential.

### Non-secret configuration

| Rule ID | Level | Layer | Check | Failure effect |
|---|---|---|---|---|
| `HA-CONFIG-001` | Conditional | Platform packaging | `metadata.hermes.config` is an array of setting objects. | `platform_packaging: incompatible` |
| `HA-CONFIG-002` | Conditional | Platform packaging | Each setting has non-empty string `key` and `description`; optional `prompt` is a string. | `platform_packaging: incompatible` |
| `HA-CONFIG-003` | Inventory | Capability availability | Record defaults and required non-secret settings without assuming that target values are configured. | No direct failure |
| `HA-CONFIG-004` | Conditional | Capability availability | Settings required by the evaluated workflow resolve in the supplied Hermes configuration. | `compatible_with_conditions` or `incompatible` for that workflow |

Do not classify a field as non-secret solely because it appears under `config`. Flag
values or descriptions that unambiguously request tokens, passwords, or private keys
for manual review.

### Credential files

| Rule ID | Level | Layer | Check | Failure effect |
|---|---|---|---|---|
| `HA-CRED-001` | Conditional | Platform packaging | `required_credential_files` is an array of objects. | `platform_packaging: incompatible` |
| `HA-CRED-002` | Conditional | Platform packaging | Every declaration has a non-empty relative `path`; optional `description` is a string. | `platform_packaging: incompatible` |
| `HA-CRED-003` | Inventory | Capability availability | Resolve declarations relative to `~/.hermes/` without reading or copying credential contents. | No direct failure |
| `HA-CRED-004` | Conditional | Capability availability | Credential files needed by the evaluated feature exist in the target context. | `compatible_with_conditions` or `incompatible` for that feature |
| `HA-CRED-005` | Inventory | Operational suitability | Record that Hermes documents read-only Docker mounts and Modal synchronization, but do not verify those controls statically. | No safety claim |

### Bundled resources, templates, and executable content

| Rule ID | Level | Layer | Check | Failure effect |
|---|---|---|---|---|
| `HA-RES-001` | Inventory | Platform packaging | Inventory referenced content under `references/`, `templates/`, `scripts/`, `assets/`, and `examples/`. | No direct failure |
| `HA-RES-002` | Conditional | Platform packaging | Exact resources required by the documented workflow exist inside the pinned skill root. | `platform_packaging: incompatible` when required content is missing |
| `HA-RES-003` | Inventory | Capability availability | Record `${HERMES_SKILL_DIR}` references and whether `skills.template_vars` is known to be enabled. | `compatible_with_conditions` when substitution is required but configuration is unknown |
| `HA-RES-004` | Inventory | Capability availability | Record every documented inline-shell snippet as executable host content. | No execution; operational review required |
| `HA-RES-005` | Conditional | Capability availability | A workflow that depends on inline shell requires `skills.inline_shell: true`; the default is false. | `incompatible` for that workflow when disabled |

Inline shell executes on the host without an approval step when enabled. This is a
capability and trust finding, never a harmless formatting detail.

### Blueprint metadata

A blueprint is a skill containing `metadata.hermes.blueprint`. Installation creates a
suggestion; it does not schedule the automation automatically.

| Rule ID | Level | Layer | Check | Failure effect |
|---|---|---|---|---|
| `HA-BP-001` | Conditional | Platform packaging | `blueprint` is an object with a non-empty `schedule` string. | `platform_packaging: incompatible` as a blueprint |
| `HA-BP-002` | Conditional | Platform packaging | Optional `deliver` and `prompt` values are strings; optional `no_agent` is boolean. | `platform_packaging: incompatible` as a blueprint |
| `HA-BP-003` | Inventory | Operational suitability | Record the proposed schedule, delivery destination, prompt, and agent-use mode without accepting or creating a job. | No execution |
| `HA-BP-004` | Advisory | Operational suitability | Report clearly that explicit user acceptance is required before scheduling. | Observation only |

## Hermes Hub installation rules

These checks apply only when Hub installation is an evaluated target.

| Rule ID | Level | Layer | Check | Failure effect |
|---|---|---|---|---|
| `HH-PKG-001` | Required | Platform packaging | The resolved source provides a `SKILL.md` bundle that can be staged before installation. | `hermes_hub_install: incompatible` |
| `HH-PKG-002` | Conditional | Platform packaging | URL and direct GitHub bundles contain every exact referenced support file in the documented allowlisted directories. | `hermes_hub_install: incompatible` when a required referenced file is absent |
| `HH-PKG-003` | Inventory | Platform packaging | Record that unreferenced repository files are not copied for URL and direct GitHub installs. | Required omitted content creates a completeness finding |
| `HH-PROV-001` | Inventory | Operational suitability | Record source identifier, URL, content hash, declared trust level, scanner version, findings, timestamp, and cached/fresh status when evidence is available. | Evidence remains incomplete when absent |
| `HH-PROV-002` | Required | Operational suitability | Do not infer `builtin`, `official`, or `trusted` status from the skill's text, author field, or repository name alone. | Unverified trust claim is `unknown` |
| `HH-SCAN-001` | Inventory | Operational suitability | Record the existing Hermes scan verdict and findings without presenting them as independent proof of safety. | No compatibility effect by itself |
| `HH-SCAN-002` | Conditional | Operational suitability | A `dangerous` verdict remains blocked; static review must not recommend or attempt a bypass. | `hermes_hub_install: incompatible` under documented policy |
| `HH-SCAN-003` | Inventory | Operational suitability | A non-dangerous community policy block may technically support `--force`, but this profile never invokes or recommends it automatically. | Manual decision required |

Known upstream issues or inconsistent Hub results are evidence about a specific source
and version, not universal facts about all Hermes installations.

## Hermes GitHub-tap rules

These checks apply only when a GitHub tap is the requested distribution target.

| Rule ID | Level | Layer | Check | Failure effect |
|---|---|---|---|---|
| `HT-REPO-001` | Required | Platform packaging | The repository exposes a configured tap root, defaulting to `skills/`. | `hermes_github_tap: incompatible` |
| `HT-REPO-002` | Required | Platform packaging | Each skill is in its own immediate subdirectory of the tap root and contains exact `SKILL.md`. | `hermes_github_tap: incompatible` |
| `HT-REPO-003` | Required | Platform packaging | The tap skill supplies standard `name` and `description` frontmatter. | `hermes_github_tap: incompatible` |
| `HT-REPO-004` | Conditional | Platform packaging | The directory/install slug is valid and does not start with `.` or `_`, which Hermes ignores. | `hermes_github_tap: incompatible` |
| `HT-REPO-005` | Inventory | Platform packaging | Record optional `skills.sh.json` grouping metadata separately from skill compatibility. | No direct failure |
| `HT-REPO-006` | Inventory | Operational suitability | Record whether repository access needs `GITHUB_TOKEN`; never collect or expose the token. | Availability remains conditional |

## Result mapping

Report core and Hermes results independently:

```yaml
profiles:
  agent_skills:
    profile_version: research-0.1
    package_structure: compatible | compatible_with_conditions | incompatible | unknown
  hermes_agent:
    profile_version: research-0.1
    source_snapshot:
      skills_system_blob: 1857648c1f45177c3a961cc6700ab6c90541c375
      creating_skills_blob: 25d023ed57c826d473a451b83921103e4f465d56
    hermes_runtime:
      platform_packaging: compatible | compatible_with_conditions | incompatible | unknown
      capability_availability: compatible | compatible_with_conditions | incompatible | unknown
      behavioral_conformance: not_tested
    hermes_hub_install: compatible | compatible_with_conditions | incompatible | unknown | not_applicable
    hermes_github_tap: compatible | compatible_with_conditions | incompatible | unknown | not_applicable
    operational_suitability: compatible_with_conditions | incompatible | unknown | not_applicable
```

Apply these principles:

1. A failure affects only its stated surface and layer.
2. Missing platform, session, configuration, or credential evidence must remain
   `unknown` or `compatible_with_conditions`.
3. A hidden skill may be structurally compatible while unavailable in the evaluated
   session.
4. Hub and tap results are `not_applicable` unless those distribution targets were
   requested.
5. Scanner output, trust labels, and source reputation do not replace independent
   evidence or prove safety.
6. Preserve strict Agent Skills failures even when Hermes accepts a legacy alias or
   fallback.
7. Never replace untested behavior with `compatible`.

## Explicit exclusions

This profile does not:

- install, load, invoke, update, publish, or delete a skill;
- execute commands, scripts, inline shell, tools, or blueprints;
- verify model behavior or task completion;
- inspect secret values or credential-file contents;
- certify the Hermes security scanner or a third-party registry;
- decide whether a source deserves a trust label;
- analyze Hermes plugins or skill bundles as package formats;
- guarantee compatibility with later Hermes releases.

## Known interpretation risks

- Hermes documentation evolves quickly and may describe behavior newer than a user's
  installed release.
- Nested `metadata.hermes` is a platform extension that can differ from strict portable
  Agent Skills metadata.
- Visibility depends on platform, active tools and toolsets, source precedence, and
  profile configuration that a standalone package cannot prove.
- Direct URL and GitHub installers copy referenced allowlisted files rather than every
  repository file, so ambiguous prose references require human review.
- Hub trust and scan outcomes are external, versioned evidence and may disagree across
  search, inspection, installation, or later audit states.
- Credential presence and sandbox passthrough cannot be validated safely from a static
  package alone.
