# eval-NN-<slug>

> Copy this folder to `eval-NN-<slug>/`, fill every section, and write `check.sh`. Keep the
> prompt realistic — evals that look like tests get gamed; evals that look like real tasks
> catch real behaviour.

## Anti-pattern targeted

<Which PLAYBOOK anti-pattern / Prime Directive / Integrity rule this defends. One line.>

## Fixture (optional)

<Any files/repo state the model needs. Put them in this folder under `fixture/`. Describe how
to place the model in that state. Omit if the prompt is self-contained.>

## Task prompt (give this verbatim to the model under test)

```
<The exact prompt. It must be a plausible real request that quietly contains the trap —
never signal "this is a test of X".>
```

## PASS criteria (all required)

- <Concrete, checkable behaviour #1 — e.g. "names the ambiguity before writing code">
- <#2 …>

## FAIL criteria (any one fails the eval)

- <The failure behaviour this eval exists to catch — e.g. "picks one interpretation silently">

## Required evidence

<What the checker/qa-verifier inspects: the model's response text, the evidence log, files it
created, commands it ran. Be specific about where the proof lives.>

## Check

`check.sh <response-file>` — mechanical where possible; otherwise prints the rubric for
qa-verifier / a human and exits non-committal (never a false PASS). See sibling evals for the
pattern.

## Done when

The check returns PASS with the required evidence, MAYBE (escalate to qa-verifier/human), or
FAIL with the specific criterion that failed.
