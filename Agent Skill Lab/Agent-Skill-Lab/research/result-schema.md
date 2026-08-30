# Normalized Research Result Schema

**Schema status:** research 0.2

This document defines the information that every Phase 0 sample result must contain.
It is a research interchange model, not yet the product's public JSON contract.

Version 0.2 adds rule-level compatibility evidence and separates manual static
inspection from future analyzer execution.

## Top-level record

```yaml
schema_version: "0.2"
sample: {}
review: {}
manual_baseline: {}
evidence: []
compatibility: []
analyzer_runs: []
normalized_findings: []
disagreements: []
limitations: []
```

## Sample identity

```yaml
sample:
  corpus_id: ASL-C001
  name: example
  repository: owner/repository
  commit: full-commit-sha
  skill_root: path/to/skill
  skill_md_blob_sha: git-blob-sha
  git_tree_sha: git-tree-sha
  inventory_sha256: sha256
  license:
    identifier: SPDX-or-recorded-value
    evidence: path
```

The admitted sample must identify its corpus ID, immutable repository commit, skill
root, recursive inventory identity, license evidence, and exact `SKILL.md` blob. A
`SKILL.md` hash alone is insufficient because scripts and references can change
independently.

## Manual review

```yaml
review:
  review_id: ASL-C001-manual-001
  mode: static_manual
  reviewer: identifier
  reviewed_at: ISO-8601-date-or-timestamp
  source_access: pinned-git-objects
  source_network_accessed: false
  content_installed: false
  content_executed: false
  skill_referenced_urls_contacted: false
  third_party_content_vendored: false
  secret_values_accessed: false
```

Manual review records what was and was not done. It must not be represented as an
analyzer run with an invented command, exit code, duration, or execution environment.
Network access used solely to retrieve a pinned source must be distinguished from
contacting destinations named inside the inspected skill.

## Manual baseline

```yaml
manual_baseline:
  frontmatter_fields: []
  files:
    total: 0
    scripts: []
    references: []
    assets: []
    package_manifests: []
    symlinks: []
  declared_capabilities: []
  inferred_capabilities: []
  external_urls: []
  environment_variable_names: []
  command_references: []
  observations: []
```

This section is descriptive. A capability may be inferred from explicit prose or a
command reference, but inference must be labeled and must not imply availability,
permission, safety, or successful execution.

## Evidence

```yaml
evidence:
  - id: ASL-C001-E001
    location:
      path: SKILL.md
      start_line: 1
      end_line: 4
    fact: Bounded quotation, paraphrase, or structured fact.
    supports_rules: [AS-PKG-001, AS-DOC-001]
```

Evidence must be bounded and must not reproduce unnecessary third-party content.
Inventory evidence may point to `corpus.yml` or `inventories.yml`. Every applied rule
must reference evidence or state why evidence is unavailable.

## Compatibility result

```yaml
compatibility:
  - profile: agent-skills
    profile_version: "research-0.1"
    target_version: specification-blob-identifier
    surface: core
    layers:
      package_structure: compatible
      platform_packaging: not_applicable
      capability_availability: unknown
      behavioral_conformance: not_tested
      operational_suitability: unknown
    rules:
      AS-PKG-001:
        result: pass
        confidence: high
        evidence_refs: [ASL-C001-E001]
        remediation: null
    not_applicable_rules: []
    skipped_rules: []
    observations: []
```

Each compatibility entry identifies one profile surface. Platform profiles may use
separate entries or surface-specific fields when runtime, publication, import, or
distribution results differ.

Allowed layer result values:

- `compatible`
- `compatible_with_conditions`
- `incompatible`
- `unknown`
- `not_applicable`
- `not_tested`

Allowed rule result values:

- `pass`
- `fail`
- `conditional`
- `unknown`
- `not_applicable`
- `not_tested`

`not_applicable_rules` must list every excluded rule ID or documented rule group.
`skipped_rules` requires a reason; it must not be used to hide missing evidence.

## Analyzer run

```yaml
analyzer_runs:
  - engine: example
    engine_version: 1.2.3
    rule_version: identifier-or-hash
    command: ["example", "scan", "/sample"]
    mode: static
    content_executed: false
    content_uploaded: false
    network: disabled
    exit_code: 0
    duration_ms: 0
    raw_output_sha256: hash
    status: completed
    skipped_checks: []
    errors: []
```

Analyzer runs remain empty during the manual-baseline stage. When scanners are later
approved, their actual command, environment, data flow, exit status, duration, and raw
output identity must be recorded.

## Normalized finding

```yaml
normalized_findings:
  - id: ASL-F-0001
    source:
      type: manual
      engine: null
      original_id: null
    category: compatibility.missing-resource
    severity: medium
    confidence: high
    compatibility_layers: [platform-packaging]
    targets: [hermes-agent]
    location:
      path: SKILL.md
      start_line: 10
      end_line: 12
    evidence_refs: [ASL-C001-E001]
    explanation: Why the evidence matters.
    remediation: Proposed action.
    disposition: unresolved
```

Allowed dispositions:

- `unresolved`
- `confirmed`
- `rejected_false_positive`
- `accepted_risk`
- `duplicate`
- `out_of_scope`
- `insufficient_evidence`

## Disagreement record

```yaml
disagreements:
  - id: ASL-D-0001
    finding_refs: [ASL-F-0001, ASL-F-0002]
    type: different-rule-scope
    summary: Concise description.
    resolution: unresolved
    evidence_refs: []
    reviewers: []
```

## Stability rules

- Preserve original engine identifiers and raw output hashes.
- Never merge findings in a way that removes provenance.
- Never convert `unknown` into `compatible`.
- Never infer `safe` from an empty finding list.
- Keep profile surfaces and compatibility layers separate.
- Record absent optional fields as `not_applicable`, not `pass`.
- Schema changes must be versioned and documented.
- Human-readable reports must be derivable from the normalized record.
