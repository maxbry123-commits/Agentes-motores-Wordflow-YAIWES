# Reproducibility: R1–R4

“Reproducible” is not one binary property. This project uses four levels.

| Level | Promise | Evidence required |
|---|---|---|
| R1 — reviewable | Architecture, interfaces, claims, and limitations can be inspected | source allowlist, license review, secret scan, claim ledger |
| R2 — runnable | A licensed synthetic example completes input → control → artifact → independent validation | clean-environment test, Before → Action → After assertion, failure-path test |
| R3 — rebuildable | A complete scientific environment can be rebuilt | pinned dependencies, public base, asset URLs and checksums, SBOM, offline notes |
| R4 — historically repeatable | A historical platform result or stable interval can be repeated under equivalent conditions | equivalent data/hardware, immutable version, seed policy, weights, logs, repeated runs |

## Current public claim

- **R1:** verified for v0.1 by the file manifest, publication scan, and separate review passes.
- **R2:** verified for the POSIX synthetic example locally and in Python 3.10–3.14 CI; see the [current verification record](../audit/CURRENT_VERIFICATION.md).
- **R3:** not claimed for the historical scientific stacks.
- **R4:** not claimed for any competition score.

Each case study reports its own level. A documentation-only case can be R1 while a synthetic control pattern is R2.

## Publication verification procedure

1. Clone into an empty environment with no private configuration.
2. Confirm that the repository has an independent history and contains no imported restricted competition source or artifacts.
3. Install only the dependencies declared by this repository.
4. Run formatting/static checks if configured.
5. Run unit tests and the synthetic end-to-end example.
6. Verify Before → Action → After:
   - a valid floor exists before exploration;
   - an accepted candidate changes the output;
   - an invalid or failed candidate does not replace the floor;
   - the final artifact passes an independent validator.
7. Run secret, license, link, and large-artifact scans.
8. Record commands and results in the current verification record.

## Randomness and online services

A fixed seed does not remove nondeterminism from GPU kernels, parallel scheduling, timeouts, online services, or variable tool availability. Random systems should report repeated-run center, spread, and failure rate, not only a best seed.

The minimum R2 example must not depend on a private language-model service. Optional planners should have a deterministic local fallback.

## Why the historical scores are not R4 here

- official inputs and some evaluation assets cannot be redistributed;
- exact scoring images and private base layers are not published;
- third-party weights and data have separate terms;
- some score lines were not fully seeded;
- scoring versions, later audit packages, and current source were not always identical;
- an immutable task/version/log/output/score chain is incomplete for some causal claims.

The correct public behavior is to preserve these boundaries, not to simulate precision.

## Case-study matrix

| Case | Public level | Historical result status |
|---|---|---|
| Virtual screening | R1 narrative; R2 only for generic floor/gate/rollback control | platform result reported, scoring environment not reproduced |
| Molecule design | R1 narrative; R2 only for generic event and promotion/rollback flow | platform result reported, docking/route stack not redistributed |
| Protein ensemble | R1 narrative; R2 only for generic verifier/rollback control | best and seeded interval reported, selector and full stack not rebuilt |
| Tool governance | R1 postmortem; R2 generic verifier/rollback example | penalty reported; ruled-out tools are excluded |

## What never enters R2 fixtures

Official test inputs, platform predictions, original logs, checkpoints, internal endpoints, private image digests, authenticated downloads, and unresolved third-party assets are not synthetic fixtures.
