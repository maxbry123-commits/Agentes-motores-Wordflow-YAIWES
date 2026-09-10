# Controlled Fixture Policy

Controlled fixtures will test deterministic validation rules without collecting live
malware or republishing third-party skill contents.

## Rules

- Fixtures must be authored specifically for this project.
- They must use inert placeholder commands and domains reserved for documentation.
- They must never contain working credentials, exploit payloads, obfuscated malware,
  or destructive commands.
- A fixture must test one primary behavior unless interaction is the test subject.
- Each fixture needs an expected result and a short threat-model justification.
- Fixtures must not be installed into a real agent profile.
- Any future execution fixture requires separate sandbox approval.

## Planned static fixtures

### ASL-FX001 — Missing required metadata

A minimal skill without one required frontmatter field.

Expected use: confirm deterministic format validation and source locations.

### ASL-FX002 — Escaping resource reference

A skill containing an inert reference to a path outside its package root.

Expected use: confirm path-boundary reporting without following the path.

### ASL-FX003 — Undeclared capability reference

A skill that documents a placeholder external service call without declaring any
runtime requirement.

Expected use: compare declared and inferred capabilities without making a malicious
intent judgment.

These fixtures are specifications only. Their package files will be added when the
first parser contract is approved.
