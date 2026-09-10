# Contribution and authorship statement

This repository separates four kinds of contribution because describing all of them as “the Agent” would erase important responsibility and provenance boundaries.

## 1. Personal authorship

Wanrun Cong defined this repository's research questions, architecture, public tool boundaries, action and validation contracts, fallback policies, evidence model, tests, and publication decisions. The original code, synthetic examples, and documentation committed here are part of this personal project.

The historical competition cases came from the author's participation in collaborative work. Project-level scores and rulings are retained only as bounded context; this repository does not claim sole authorship or redistribute the original submissions.

## 2. Development-time programming agents

Programming agents assisted implementation, debugging, code review, test generation, documentation, and repository organization. Their assistance does not make them runtime components of every competition image, nor does it remove the author's responsibility for the code and public claims in this repository.

## 3. Runtime language models

Some task versions used a language model or planner during evaluation for bounded decisions, candidate proposals, or explanatory review. Runtime model configuration changed during development, and the evidence strength differs by version. This repository therefore avoids score attribution to a model brand unless task, immutable version, runtime log, output, and platform score are bound together.

## 4. Scientific backends

Specialized tools performed the domain computation: molecular representation and scoring, docking, retrosynthesis, protein folding and sampling, and neural-operator training. These tools are distinct from both development-time agents and runtime planners. Their names, licenses, and redistribution boundaries are recorded in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Personal public work

The code and documentation in this repository were created for this personal project under Wanrun Cong's direction, review, and publication responsibility, with the programming-agent assistance described above. They intentionally omit original raw logs, official data, restricted infrastructure, model weights, submission artifacts, and source files with unresolved third-party provenance.
