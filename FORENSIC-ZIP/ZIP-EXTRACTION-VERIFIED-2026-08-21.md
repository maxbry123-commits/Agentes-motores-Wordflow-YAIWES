# ZIP EXTRACTION VERIFIED — 2026-08-21

## Scope
Verified from GitHub Actions run `32529275113` on commit `7de9b185f56bd4d574a99331884728512399b481`.

## Method
The workflow validates each source archive with `unzip -t`, extracts to a temporary `extracted/` directory, preserves relative paths, and produces archive SHA-256 plus file/directory manifests. The run persisted `FORENSIC-ZIP/RUN-32529275113.md` and exposed eight extraction artifacts.

## Artifact evidence verified
| ZIP | Artifact ID | Source archive bytes | Manifest file count | Manifest dir count | Source SHA-256 |
|---|---:|---:|---:|---:|---|
| zip1 | 9463282499 | 16,411,464 | 1,387 | 216 | 66afa6a5ece7d679fae0d2144ca7e9fe05b968e5976703eaa0fae883ae2c50fa |
| zip4 | 9463282194 | 16,411,464 | 1,387 | 216 | not re-read in this local artifact pass |
| zip5 | 9463285201 | 16,458,214 | 7,795 | 491 | not downloaded in this pass |
| zip5.1 | 9463281605 | 10,027,045 | 791 | 42 |  not re-read in this local artifact pass |
| zip6 | 9463282580 | 10,035,035 | 801 | 45 | d8c17cbd859448c4df73f3ff0275841459a798c488bdc8e195c79537e94a8a0e |
| zip7 | 9463282058 | 2,405,790 | 953 | 141 | 533f31a4c51fa7d6305b4b40d2b9d9c8107ddd8c62f3250a6cbaa6c7b5de547c |
| zip8 | 9463283012 | 4,627,880 | 1,334 | 102 | d8ada019b84c69ab9dd2419afe0040a6c071caffcee545b4149b6012bfc76ce7 |
| zip9 | 9463282609 | 7,239,313 | 2,579 | 44 | f4851b99b82a8a4c39d1a74422605bcf9259a75ef52c9601d22b69d35a1a1e45 |

## Local artifact checks completed in this pass
- zip1: `unzip.testzip() = None`; extracted-files manifest has 1,387 file entries; extracted-dirs manifest has 216 directory entries.
- zip6: `unzip.testzip() = None`; 801 file entries; 45 directory entries.
- zip7: `unzip.testzip() = None`; 953 file entries; 141 directory entries.
- zip8: `unzip.testzip() = None`; 1,334 file entries; 102 directory entries.
- zip9: `unzip.testzip() = None`; 2,579 file entries; 44 directory entries.

## Important packaging observation
The downloaded GitHub Actions artifact is itself a ZIP containing `extracted/` plus the evidence files. Its physical ZIP entry count is not identical to the source archive file count because the artifact packaging is a second archive layer. The authoritative source file counts are the workflow-generated `extracted-files.txt` manifests, not the outer artifact entry count.

## Relative-root observations
The five inspected artifacts all contain source files under the workflow's `extracted/` wrapper. The wrapper is an artifact/extraction workspace layer and must NOT automatically become `ROOTS/openclaw/extracted/`. The next reconstruction step must strip only this known evidence wrapper while preserving every path below it.

## Cross-ZIP path overlap sampled
After stripping `extracted/`:
- zip1: 1,355 files physically present in the downloaded artifact; its authoritative manifest lists 1,387 source file paths.
- zip6: 764 physical source files in artifact; authoritative manifest 801.
- zip7: 953 physical source files; authoritative manifest 953.
- zip8: 1,271 physical source files; authoritative manifest 1,334.
- zip9: 2,579 physical source files; authoritative manifest 2,579.

The five sampled ZIPs have 6,912 distinct physical source paths in their combined local artifacts. The only overlap found between zip1 and zip6 was 10 paths: `config/knip.config.ts`, `config/markdownlint-cli2.jsonc`, `config/shellcheckrc`, `config/swiftformat`, `config/swiftlint.yml`, four `config/tsconfig/oxlint*.json` files, and `deploy/fly.private.toml`. No overlaps were found among the other sampled pairs.

## Status
This document proves that GitHub Actions successfully produced and exposed verified extraction artifacts for run `32529275113`. It does NOT yet prove that any ZIP is the canonical OpenClaw source, and it does NOT authorize publication into `ROOTS/openclaw/`. Canonical comparison remains a separate gate.
