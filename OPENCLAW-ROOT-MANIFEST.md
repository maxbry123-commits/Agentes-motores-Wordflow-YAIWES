# OPENCLAW ROOT MANIFEST — WORKING DRAFT

Status: PRE-PUBLISH / EVIDENCE-ONLY
Canonical source: `openclaw/openclaw@a4178c7eb15a0dd2b8b44804348e256f1a109a34`
Destination: `ROOTS/openclaw/`

## Rule
No path is approved for publication until it has a reproducible source and verification evidence. ZIP-derived paths remain pending until the actual archive bytes are acquired and extracted.

## Schema
| Path | Canonical source | ZIP source | Destination | Type/mode | Size | Blob/SHA-256 | Verdict | Action | Evidence |
|---|---|---|---|---|---:|---|---|---|---|

## Verified cross-check entries
| Path | Canonical source | Current repo | Verdict | Action |
|---|---|---|---|---|
| `LICENSE` | blob `ebaebf7c416761a32f932ad70ebe5d1d2e214f68` | same blob | MATCH | KEEP/COPY after final build |
| `package.json` | version `2026.8.1`; schemaVersions state 9/agent 17 | version `2026.7.1` | MODIFIED / NO MATCH | REPLACE only after full manifest verification |
| `node-version.mjs` | blob `dc7876dd0ce35116aaef535d342647ebb1ad16e7` | missing | MISSING | ADD from verified canonical/ZIP source |
| `npm-shrinkwrap.json` | absent at pinned ref | present | EXTRA / NON-CANONICAL | EXCLUDE from canonical root unless separately justified |
| `pnpm-workspace.yaml` | blob `5ffb3a0e59272237670f60b5448931290d5b9a65` | blob `05d3a199ce86c756006b698af705ae45e2855dd3` | MODIFIED / NO MATCH | REPLACE only after full manifest verification |
| `README.md` | blob `c74989cee8a9c1e8648aa892175de3c9e375bafe` | blob `c656353ef50013d27756c1717fd2df6e2645c1db` | MODIFIED / NO MATCH | REPLACE only after full manifest verification |
| `openclaw.mjs` | canonical file reads `node-version.mjs` and contains supported runtime logic | current file has materially different launcher implementation | MODIFIED / NO MATCH | REPLACE only after full manifest verification |
| `THIRD_PARTY_NOTICES.md` | blob `6b6721901b7590d20774ba0504d975e1be70a57a` | same blob | MATCH | KEEP/COPY after final build |

## ZIP status
Eight ZIPs are known from the repository tree. ZIP 1 and ZIP 4 share the same GitHub blob SHA/size. Actual extraction remains pending; no ZIP path is marked canonical until extraction evidence exists.

## Multi-root destination
OpenClaw is isolated at `ROOTS/openclaw/`. Future agents are siblings under `ROOTS/` and must not be merged into the OpenClaw tree.

## Next gates
1. Acquire actual ZIP bytes.
2. Extract without altering relative paths.
3. Generate per-ZIP manifests and SHA-256.
4. Cross-check ZIP trees against the pinned canonical tree.
5. Complete root manifest.
6. Build `ROOTS/openclaw/` only from approved entries.
7. Local verify, publish, remote read-back, forensic XRAY.
