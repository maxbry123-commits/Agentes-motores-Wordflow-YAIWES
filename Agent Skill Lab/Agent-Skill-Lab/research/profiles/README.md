# Research Compatibility Profiles

Compatibility profiles turn primary platform documentation into repeatable manual
checks. They are research artifacts, not executable validators and not claims that a
sample is safe.

## Profile contract

Every profile must include:

- a stable profile identifier and research version;
- the target specification or platform version, when one exists;
- primary sources and an immutable source identity where practical;
- a review date;
- stable rule identifiers;
- the compatibility layer affected by each rule;
- a distinction between required rules and advisory guidance;
- result-mapping rules and explicit exclusions.

## Requirement levels

- **Required:** a documented format or platform requirement. A confirmed failure can
  make the evaluated layer `incompatible`.
- **Conditional:** applies only when the relevant optional field, resource, feature, or
  capability is present.
- **Advisory:** documented recommendation or quality guidance. Failure creates an
  observation but does not, by itself, make the package incompatible.
- **Inventory:** records evidence without assigning conformance.

Profiles must not silently strengthen `should`, `recommended`, or experimental
documentation into mandatory requirements.

## Evidence rules

Each applied rule must record:

- rule ID and profile version;
- source path and line range in the sample;
- bounded evidence or a structured fact;
- expected and observed behavior;
- result and confidence;
- primary-source reference;
- remediation when the result is not `compatible`;
- reviewer and review date.

An absent finding is not evidence that a capability is available or that a skill is
safe.

## Profiles

- [Agent Skills research profile 0.1](agent-skills-research-0.1.md)
- [OpenClaw research profile 0.1](openclaw-research-0.1.md)
- [Hermes Agent research profile 0.1](hermes-agent-research-0.1.md)
