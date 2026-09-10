# Project manifest

Status: **VERIFIED FOR PERSONAL PUBLICATION**

This manifest describes the current personal public research tree. The project does not use a GitHub software Release or tag as its identity.

## Personal original materials

| Area | Content | License |
|---|---|---|
| Root documents | project overview, authorship, contribution, security, research agenda, history, citation | Apache-2.0 where copyright applies |
| `docs/` | architecture, research loop, results, capability, evidence, provenance, reproducibility | Apache-2.0 |
| `case_studies/` | four independently written, evidence-bounded technical narratives | Apache-2.0 |
| `lab_notebook/` | curated problem framing, timeline, negative results, postmortem | Apache-2.0 |
| `evidence/` | trace schema and labeled personal reconstructions | Apache-2.0 |
| `benchmarks/` | evaluation design and status matrix | Apache-2.0 |
| `audit/` | publication boundary, file manifest, and current verification | Apache-2.0 |
| `src/`, `examples/`, `tests/` | personal control-loop implementation and synthetic fixtures | Apache-2.0 after file review |

## Third-party content redistributed

None. Names, links, and short factual descriptions are recorded in [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

## Historical artifacts redistributed

None. Historical scores and method summaries are reported as bounded context; original competition artifacts are not published here.

## Required audit checks

- [x] Every candidate file classified in `FILE_MANIFEST.tsv`.
- [x] No restricted historical file copied.
- [x] No secret, private endpoint, digest, or user-specific absolute path detected.
- [x] No official data, raw log, output, checkpoint, or submission artifact included.
- [x] All JSONL traces parse and carry both reconstruction flags.
- [x] Markdown internal links resolve.
- [x] Tests and synthetic end-to-end example pass in a clean local environment.
- [x] License and third-party notices reviewed.
- [x] Current verification record updated with exact local commands and observed results.

Remote CI status is shown by the repository badge and Actions page. It is not copied into this single-snapshot record.
