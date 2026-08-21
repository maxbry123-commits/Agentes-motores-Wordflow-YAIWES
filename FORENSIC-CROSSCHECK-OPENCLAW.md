# FORENSIC CROSS-CHECK — OPENCLAW

## Authority
- Canonical: `openclaw/openclaw@a4178c7eb15a0dd2b8b44804348e256f1a109a34`
- Destination: `maxbry123-commits/Agentes-motores-Wordflow-YAIWES@main`

## Verified matrix
| Path | Canonical | Current repo | Verdict |
|---|---|---|---|
| `package.json` | 2026.8.1; schemaVersions state 9/agent 17; OpenClaw Foundation | 2026.7.1; no observed schemaVersions; author empty | MODIFIED / NO MATCH |
| `node-version.mjs` | Exists; blob `dc7876dd0ce35116aaef535d342647ebb1ad16e7` | Missing | MISSING |
| `npm-shrinkwrap.json` | Absent | Present | EXTRA / NON-CANONICAL |
| `pnpm-workspace.yaml` | blob `5ffb3a0e59272237670f60b5448931290d5b9a65` | blob `05d3a199ce86c756006b698af705ae45e2855dd3` | MODIFIED / NO MATCH |
| `README.md` | blob `c74989cee8a9c1e8648aa892175de3c9e375bafe` | blob `c656353ef50013d27756c1717fd2df6e2645c1db` | MODIFIED / NO MATCH |
| `LICENSE` | blob `ebaebf7c416761a32f932ad70ebe5d1d2e214f68` | same blob | MATCH |
| `THIRD_PARTY_NOTICES.md` | blob `6b6721901b7590d20774ba0504d975e1be70a57a` | same blob | MATCH |
| `openclaw.mjs` | imports `./node-version.mjs`, recommends Node 26 | current launcher embeds different Node-version logic and recommends Node 24 | MODIFIED / NO MATCH |

## Rules
The visible canonical tree response can truncate. Therefore a truncated display is never used as complete inventory evidence. Exact path claims require direct file/tree evidence.

OpenClaw will be rebuilt only at `ROOTS/openclaw/`. Future agent roots remain siblings. Existing root files are candidates, not canonical source, until verified.

Eight ZIPs are known. ZIP 1 and ZIP 4 share the same GitHub blob SHA/size. Actual binary extraction is still pending; no ZIP-derived path is canonical until archive bytes are acquired and extracted.

## Next gates
1. Acquire ZIP bytes reproducibly.
2. Extract without changing relative paths.
3. Produce per-ZIP manifests and SHA-256.
4. Compare ZIP trees against canonical ref.
5. Complete `OPENCLAW-ROOT-MANIFEST.md` from evidence only.
6. Build `ROOTS/openclaw/`.
7. Local verify → publish → GitHub read-back → final XRAY.

## Anti-hallucination
Filename presence, version strings, memory, inference, or truncated output are not equivalence evidence. Every MATCH requires reproducible evidence.
