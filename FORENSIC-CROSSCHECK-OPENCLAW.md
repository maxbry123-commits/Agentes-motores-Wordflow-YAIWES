# FORENSIC CROSS-CHECK — OPENCLAW

## Authority
- Canonical repository: `openclaw/openclaw`
- Canonical ref: `a4178c7eb15a0dd2b8b44804348e256f1a109a34`
- Destination under audit: `maxbry123-commits/Agentes-motores-Wordflow-YAIWES@main`

## Evidence matrix

| Path | Canonical ref | Current repo | Verdict | Evidence |
|---|---|---|---|---|
| `package.json` | Exists; version `2026.8.1`; contains `openclaw.schemaVersions` state 9 / agent 17; author OpenClaw Foundation; declares `node-version.mjs` in `files` | Exists; version `2026.7.1`; no observed schemaVersions block; author empty; package file set differs | **MODIFIED / NO MATCH** | Direct GitHub file reads |
| `node-version.mjs` | Exists; blob `dc7876dd0ce35116aaef535d342647ebb1ad16e7` | Not found at current repo root | **MISSING** | Direct GitHub file reads |
| `npm-shrinkwrap.json` | Not found | Exists at current repo root | **EXTRA / NON-CANONICAL** | Direct GitHub file reads |
| `pnpm-workspace.yaml` | Exists; blob `5ffb3a0e59272237670f60b5448931290d5b9a65`; includes workspace globs and canonical dependency policy | Exists; blob `05d3a199ce86c756006b698af705ae45e2855dd3`; same top-level workspace globs but materially different exclusions/overrides/versions and patched dependency section | **MODIFIED / NO MATCH** | Direct GitHub file reads |
| `README.md` | Exists; blob `c74989cee8a9c1e8648aa892175de3c9e375bafe`; canonical current README content and installation/onboarding guidance | Exists; blob `c656353ef50013d27756c1717fd2df6e2645c1db`; content differs materially in installation/setup wording and sponsor section | **MODIFIED / NO MATCH** | Direct GitHub file reads |

## Canonical tree observation
The pinned canonical tree is a large recursive Git tree. Direct tree retrieval returned the pinned SHA and real paths/modes/blobs; for example `.agents/skills/agent-transcript/SKILL.md` and other nested paths are present. The full response is tool-truncated, so no claim of a complete manually enumerated list is made from the truncated display. The tree endpoint itself is the authority for subsequent exact path queries.

## Interpretation
The current repository root is not an exact copy of the pinned OpenClaw ref. Existing OpenClaw-looking files must therefore be treated as candidates, not as canonical source.

## Multi-root rule
OpenClaw must be reconstructed under `ROOTS/openclaw/`. The repository is a multi-agent/multi-motor repository; future agent roots must remain siblings and must not be mixed into OpenClaw. Documentation, manifests and forensic control files remain outside the agent roots.

## ZIP status
Eight ZIP files are present in the destination repository inventory. ZIP 1 and ZIP 4 have the same GitHub blob SHA and size and are therefore exact duplicate blobs at GitHub level. The actual binary extraction of the ZIPs is not yet verified because the current connector cannot directly read the large ZIP blob contents. No ZIP-derived file is considered canonical until its bytes are acquired, extracted, inventoried and cross-checked.

## Next verification
1. Acquire ZIP bytes through a reproducible mechanism that returns the actual archive file reference.
2. Extract each ZIP without altering relative paths.
3. Generate per-ZIP manifests and SHA-256 values.
4. Compare ZIP trees against the canonical ref.
5. Expand the canonical↔repo matrix for critical root files/directories.
6. Build `ROOTS/openclaw/` only from verified source paths.
7. Read back GitHub and compare the resulting root against the manifest.

## Anti-hallucination rule
A path is `MATCH` only when evidence demonstrates equivalence. Presence alone is not equivalence. A version string alone is not equivalence. A filename alone is not evidence of canonical origin. A truncated API display is not evidence of a complete inventory.
