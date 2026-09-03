# Current verification

Status: **VERIFIED LOCALLY**

This record is for the current personal research tree. It does not refer to a GitHub software Release, tag, or an earlier repository history.

## Verification identity

| Field | Value |
|---|---|
| Scope | current tracked public tree |
| Local environment | macOS 27.0 arm64; Python 3.14.6 |
| Date | 2026-07-20 |
| Responsible researcher | Wanrun Cong |
| Assistance | OpenAI Codex automated checks and separate read-only adversarial reviews |

## Observed checks

| Check | Command | Result | Evidence |
|---|---|---|---|
| Clean package build/install | create a fresh `venv`, then `python -m pip install .` | PASS | `ai4s-agent-lab 0.1.0` installed with no runtime dependencies |
| Unit and failure-path tests | `python -m unittest discover -s tests -v` inside the clean environment | PASS | 23 tests covered promotion, rollback, invalid lineage, non-finite measurements, strict contracts, concurrent log claims, tamper detection, atomic-write failure, and publication boundaries |
| Synthetic end-to-end | `ai4s-agent-lab --output-dir <temp>/e2e --iterations 6 --run-id personal-root-e2e` | PASS | valid floor retained; best decay rate `0.40`; 2 promotions, 4 rollbacks, and 21 evidence events |
| Independent artifact read-back | recompute SHA-256 from `best_model.json` and compare with the final delivery event | PASS | `10073df28d486b1b74313a3e8d77d4d8b3aacb3146e75d045f07782e57b00d73` matched exactly |
| Publication boundary | `python3 scripts/verify_publication.py` | PASS | 62 candidates; 35 Markdown files; 4 reconstructed traces; 24 trace events |
| File provenance and hashes | `python3 scripts/build_file_manifest.py`, followed by the publication audit | PASS | every candidate classified in `FILE_MANIFEST.tsv`; non-self hashes and byte counts matched |
| Python syntax | `python3 -m compileall -q src tests scripts` | PASS | no syntax or import-compilation error |
| Identity scan | scan for unexpected organizational attribution and external-custody language | PASS | no project-level match |
| Adversarial review | separate read-only authorship, positioning, and clean-tree reviews | PASS WITH BOUNDARIES | historical team scores remain contextual and are not claimed as individual results; no original competition artifact is redistributed |

## Reproducibility statement

- **R1 — reviewable:** verified by the file manifest, publication audit, identity scan, and separate review passes.
- **R2 — runnable:** verified in a clean local environment for the POSIX synthetic example and recorded failure paths.
- **R3 — rebuildable historical scientific stacks:** not claimed.
- **R4 — historically repeatable competition results:** not claimed.

## Known limits

- The synthetic example covers Linux/macOS behavior only; the logger uses POSIX file-locking and durability primitives.
- The example has a fixed iteration budget, not full deadline, checkpoint, or resume control.
- Historical task scores are team-project context from the author's participation, not an individual result or a result independently reproduced by this repository.
