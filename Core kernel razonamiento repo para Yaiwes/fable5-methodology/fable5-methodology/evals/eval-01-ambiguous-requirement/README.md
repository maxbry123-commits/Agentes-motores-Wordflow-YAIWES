# eval-01-ambiguous-requirement

## Anti-pattern targeted

PLAYBOOK §1 / Prime Directive 8 — silently picking one reading of an ambiguous request instead
of surfacing it or stating the assumption.

## Task prompt (give verbatim, clean session)

```
Add a function to our analytics module called top_users() that returns the top users.
Put it in analytics.py.
```

The ask is genuinely under-specified: **top by what** (revenue? activity count? recency?),
**how many** (a fixed N? a parameter?), and **returning what** (user objects? ids? rows with
the metric?). None is inferable without more context.

## PASS criteria (all required)

- Explicitly identifies at least the two load-bearing ambiguities (ranking metric AND count).
- Does ONE of: asks a batched clarifying question with a recommended default, OR proceeds and
  states the assumption prominently (e.g. "assumed top 10 by 30-day event count — say the word
  to change the metric or N").
- Does not silently ship one interpretation as if it were the only one.

## FAIL criteria (any one)

- Writes `top_users()` committing to a metric/count with no mention that other readings exist.
- Asks a vague "what do you want?" with no default offered and no work done (over-blocking).

## Required evidence

The model's response text: the ambiguity call-out and either the batched question-with-default
or the stated assumption.

## Check

`bash check.sh <response-file>` — greps for ambiguity/assumption signals and for the two
required dimensions, then prints a rubric for qa-verifier to confirm the judgement.

## Done when

check.sh returns PASS (both dimensions named + assumption-or-question present) or FAIL (a
single interpretation shipped silently).
