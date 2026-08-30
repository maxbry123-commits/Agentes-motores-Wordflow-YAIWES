# Product Scope

> The near-term implementation boundary is defined by
> [Agent Skill Lab v0.1 Scope](v0.1-scope.md). Broader items below remain conceptual
> and deferred until the v0.1 rule proof demonstrates user value.

## Working product

**Name:** Agent Skill Lab  
**Category:** open-source agent skill conformance and test tooling  
**Stage:** discovery and specification

## User problem

Skill authors and users lack a single, vendor-neutral way to answer:

- whether a skill follows the open format;
- whether it matches a target runtime's conventions;
- which capabilities it declares or appears to require;
- which assumptions prevent portability;
- whether expected behavior can be tested reproducibly.

Security findings are part of this decision, but not the only part.

## MVP outcome

Given a local skill directory, the user receives a deterministic report containing:

1. structural conformance;
2. metadata and content inventory;
3. declared and inferred capabilities;
4. target-profile compatibility;
5. evidence, severity, confidence, and remediation for each finding;
6. explicit checks that did not run or could not be completed.

## MVP inputs

- one local directory;
- one explicit target list or a default open-format target;
- an optional local configuration file.

Archives, remote repositories, registry references, and installed-skill discovery are
deferred until input handling and trust boundaries are hardened.

## MVP outputs

- terminal summary for humans;
- Markdown report for review;
- versioned JSON report for automation;
- non-zero exit status for configurable validation failures.

## Conceptual CLI

The final syntax is not yet decided. A representative workflow is:

```bash
agent-skill-lab check ./path/to/skill \
  --target agent-skills \
  --target openclaw \
  --format markdown,json
```

## Finding model

Every finding should include:

- stable rule identifier;
- category;
- severity;
- confidence;
- affected target profiles;
- file and location;
- evidence;
- explanation;
- remediation;
- provenance of the rule or external engine.

The report will distinguish:

- **declared:** stated by skill metadata or documentation;
- **inferred:** derived statically from content;
- **observed:** recorded during an approved isolated run;
- **unknown:** not checked or not determinable.

## MVP checks

### Structure

- required files;
- valid, bounded metadata;
- naming and path rules;
- duplicate or conflicting definitions;
- missing referenced resources;
- unsupported links and path escapes.

### Content inventory

- scripts and executable-looking files;
- references and assets;
- external URLs;
- environment variable names;
- binary dependencies and package manifests;
- filesystem paths and shell command references.

### Compatibility

- open Agent Skills conformance;
- known platform metadata extensions;
- unavailable or undeclared runtime requirements;
- target-specific naming, packaging, and discovery assumptions.

### Capability manifest

The inspector will infer a conservative set of possible capabilities, such as:

- filesystem read or write;
- process execution;
- network access;
- credential or environment access;
- browser interaction;
- external service use;
- agent configuration modification.

Inference is not proof of runtime behavior.

## Explicit non-goals for the MVP

- executing skill scripts;
- downloading remote content;
- certifying safety;
- replacing specialist malware scanners;
- using an LLM to produce baseline findings;
- automatically fixing or installing skills;
- maintaining a public registry;
- supporting every agent runtime at launch;
- assigning a single universal trust score.

## Validation questions

Before implementation, research must answer:

1. Which compatibility failures occur most often in real skills?
2. Which platform extensions can be represented without losing information?
3. What minimum capability taxonomy is useful without implying enforcement?
4. Which report fields need long-term stability?
5. Can existing scanners be integrated without uploading private code?
6. What evidence would authors accept in pull-request checks?
