# shared/schemas/

JSON Schema contracts between analysis stages. Each schema's version lives in the file name and in `$id`. When the shape changes, bump to v2 and document the migration separately.

## Artifacts and schemas

| Artifact | Written by | Read by | Schema |
|---|---|---|---|
| Coded segment | `09-flat-coding` | 10–18 | `coded-segment.v1.schema.json` |
| Coded interview | `09-flat-coding` | 10–18 | `coded-interview.v1.schema.json` |
| Theme | `13-axial-coding` | 14, 17 | `theme.v1.schema.json` |
| Category | `13-axial-coding` | 14, 17, 18 | `category.v1.schema.json` |
| Paradigm model node | `14-paradigmatic-model` | 15, 17, 18 | `paradigmatic-node.v1.schema.json` |
| Behavioral type | `16-typology` | 17, 18 | `typology-type.v1.schema.json` |
| Key finding | `17-key-findings` | 18 | `finding.v1.schema.json` |

## ID dependency graph

```
seg-NNNN  ─┬─→  T0X (theme)  ─┬─→  C0X (category)  ─┬─→  F0X (finding)
           │                  │                      │
           ├─→  N0X (paradigm-node) ────────────────┤
           │                                         │
           └─→  TY0X (typology-type) ────────────────┘
                                                     ↓
                                                  R0X (recommendation, in `18-report-draft`)
```

ID conventions:
- `seg-NNNN` — segment (4 digits, within an interview).
- `R01..R100` — respondent.
- `T01..T999` — theme.
- `C01..C99` — category.
- `A01..A99` — axis.
- `N01..N99` — model node.
- `E01..E99` — model arc.
- `TY01..TY99` — behavioral type.
- `F01..F99` — key finding.
- `RQ1..RQ99` — research question (from `project-config.yaml`).
- `H1..H99` — hypothesis (from `project-config.yaml`).
- `R1..R99` — recommendation (in `18-report-draft`).

## Versioning rules

- Minor changes (adding optional fields, extending an enum) — don't bump; extend the existing schema in place.
- Major changes (changing required fields, changing a type, removing a field) — bump to vN+1 and keep vN for migration.
- `coding_meta.schema_version` in `coded-interview` records which version was used for coding — downstream checks against it.

## Validation

In Python — `jsonschema`, or a `pydantic.BaseModel` generated via `datamodel-code-generator`. In Claude Code — the agent applies the schema as part of the prompt (see `prompts/<name>.md`, the Output schema section).
