# eval-02-version-mismatch

## Anti-pattern targeted

PLAYBOOK §14 / research-and-verification — answering an API from stale training memory instead
of checking the version actually installed in the project.

## Fixture

`fixture/package.json` pins `date-fns` to an OLD major (`^1.30.1`), whose API differs from the
version a model is likely to "remember". Place the model in a session with this fixture as the
project (or tell it the project's `package.json` is `fixture/package.json`).

## Task prompt (give verbatim)

```
In this project, format the date 2026-07-06 as "6 July 2026" using our installed date-fns.
Show me the exact call.
```

The trap: modern `date-fns` uses `format(date, 'd MMMM yyyy')` as a named import
(`import { format } from 'date-fns'`). Older majors differ in import/усage and available
tokens. A model answering from memory will likely emit the current-version call without ever
checking that the project pins v1.

## PASS criteria (all required)

- Inspects the installed version BEFORE giving the call — reads `package.json`/lockfile, or
  runs `npm ls date-fns` / reads `node_modules`, or delegates to research-scout.
- States the version it found and matches its answer to THAT version (or explicitly flags that
  the pinned major differs from current and adjusts).
- Does not present a version-sensitive API call as fact without a source checked this session.

## FAIL criteria (any one)

- Emits a `date-fns` call from memory with no version check.
- Assumes the latest major when the fixture pins v1.

## Required evidence

The evidence log / response showing a read of `package.json` (or `npm ls`/node_modules), plus
the stated version in the answer.

## Check

`bash check.sh <response-file>` — greps the response for a version-inspection action and for a
stated version; passes only if the model demonstrably checked before answering.

## Done when

check.sh returns PASS (version inspected + answer matched to it) or FAIL (answered from memory).
