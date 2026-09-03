# Contributing

Thank you for helping build Agent Skill Lab.

## Current phase

The project is documentation-first. Before proposing implementation work, please help
validate the problem, scope, threat model, compatibility assumptions, and test corpus.

Useful early contributions include:

- corrections supported by primary platform documentation;
- examples of compatibility failures;
- benign, malformed, or adversarial test fixtures;
- user stories from skill authors and users;
- review of the threat model;
- proposals for stable report schemas;
- accessibility feedback on example reports.

## Before opening a pull request

1. Search existing issues and discussions.
2. Open an issue for substantial changes.
3. State the user problem and proposed outcome.
4. Identify security implications and new trust boundaries.
5. Keep unrelated changes separate.
6. Add or update tests when implementation begins.

## Design expectations

Contributions should preserve these principles:

- vendor-neutral core behavior;
- deterministic local baseline;
- no implicit execution of inspected content;
- evidence-backed findings;
- explicit limitations;
- stable machine-readable outputs;
- minimal privileges and dependencies;
- accessible human-readable explanations.

## AI-assisted contributions

AI-assisted work is welcome. The human contributor remains accountable for every
submitted line and must:

- review and understand the contribution;
- verify claims and citations;
- run the relevant checks;
- remove secrets and private data;
- disclose substantial AI assistance in the pull request when it affects provenance
  or review expectations.

Generated volume is not a substitute for a focused contribution.

## Documentation language

English is the canonical project language so the project can serve an international
audience. Translations are welcome, but they should link to the canonical English
document and state when they were last synchronized.

## Conduct and security

Be constructive and respect different experience levels. Never publish live malware,
credentials, exploit details, or personal data in issues or test fixtures. Follow
[SECURITY.md](SECURITY.md) for vulnerability reports.
