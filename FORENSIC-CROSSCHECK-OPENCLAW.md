# FORENSIC CROSS-CHECK — OPENCLAW

## Authority
- Canonical repository: `openclaw/openclaw`
- Canonical ref: `a4178c7eb15a0dd2b8b44804348e256f1a109a34`
- Destination under audit: `maxbry123-commits/Agentes-motores-Wordflow-YAIWES@main`

## Evidence matrix

| Path | Canonical ref | Current repo | Verdict | Evidence |
|---|---|---|---|---|
| `package.json` | Exists; version `2026.8.1`; contains `openclaw.schemaVersions` state 9 / agent 17; author OpenClaw Foundation | Exists; version `2026.7.1`; no observed schemaVersions block; author empty; package file set differs | **MODIFIED / NO MATCH** | Direct GitHub file reads |
| `node-version.mjs` | Exists | Not found at current repo root | **MISSING** | Direct GitHub file reads |
| `npm-shrinkwrap.json` | Not found | Exists at current repo root | **EXTRA / NON-CANONICAL** | Direct GitHub file reads |

## Interpretation
The current repository root is not an exact copy of the pinned OpenClaw ref. Existing OpenClaw-looking files must therefore be treated as candidates, not as canonical source.

## Next verification
1. Audit all candidate ZIPs.
2. Extract and inventory them without changing relative paths.
3. Compare ZIP trees against the canonical ref.
4. Build `ROOTS/openclaw/` only from verified source paths.
5. Read back GitHub and compare the resulting root against the manifest.

## Anti-hallucination rule
A path is `MATCH` only when evidence demonstrates equivalence. Presence alone is not equivalence. A version string alone is not equivalence. A filename alone is not evidence of canonical origin.
