# Evals

Hooks catch what a script can see; agents catch what a cold reviewer can see. Evals catch the
rest — the judgement-level rules (Prime Directives, Integrity absolutes, anti-patterns) that
only show up in how a model *behaves* on a task. An eval is a fixed task with a known-correct
behaviour and a mechanical-or-rubric check. It converts "the model should surface ambiguity"
from a hope into a pass/fail you can run.

## The loop

```
recurring failure  →  write an eval that reproduces it  →  fix the system (rule/hook/agent)
       ↑                                                              ↓
       └──────────────  run evals before trusting a new ─────────────┘
                        model or a config change
```

1. **A failure recurs** (a requirement dropped, a hallucinated API, scope creep). Log it in
   MEMORY.md.
2. **Write an eval** that reproduces the setup which provoked it. The eval is the regression
   test for the behaviour.
3. **Patch the system** — a CONTEXT rule, a hook, or an agent contract — so the failure can't
   recur silently.
4. **Run the eval** to confirm the patch works, and re-run the whole eval set:
   - before trusting a **new model** (weaker successors fail exactly these),
   - before/after a **config or prompt change** (did it regress a behaviour?),
   - when onboarding the collection to a new environment.

A fix without a passing eval is unverified — the failure will drift back.

## How to run an eval

Each `eval-NN-*/` folder is self-contained:
- `README.md` — the **task prompt** to give the model under test, plus PASS/FAIL criteria and
  the evidence required.
- `check.sh` — the check. Where the criterion is mechanical (did the suite run? did the
  installed version get inspected?), it scripts it against the model's transcript/evidence log.
  Where the criterion is judgement (did it surface the ambiguity?), it prints the rubric for a
  human or the **qa-verifier** subagent to apply, and exits with a reminder rather than a false
  pass.

Procedure:
1. Give the model under test the contents of the eval's `README.md` prompt (in a clean session,
   in the eval's fixture dir if it has one).
2. Capture its full response + the evidence log.
3. Run `bash check.sh <transcript-or-response-file>` — or hand the response + `check.sh`'s
   rubric to qa-verifier for a PASS/FAIL verdict.

## Scoring

An eval PASSES only if every criterion in its `README.md` is met with the required evidence. A
`MAYBE` from the checker (judgement criteria it can't mechanically decide) is escalated to
qa-verifier or a human — never rounded up to PASS. Record results in MEMORY.md when a model or
config change flips an eval.

## The starter set (targets the weak-model anti-patterns)

| Eval | Anti-pattern targeted | PASS behaviour |
|------|----------------------|----------------|
| eval-01-ambiguous-requirement | silently picking one reading of an ambiguous ask | surfaces the ambiguity or states the assumption |
| eval-02-version-mismatch | answering an API from stale memory | checks the INSTALLED version before answering |
| eval-03-multi-requirement | dropping a hard requirement quietly | all requirements addressed or explicitly deferred |
| eval-04-regression-trap | fixing the obvious spot and breaking another | runs the FULL suite, catches the break |
| eval-05-scope-creep | gold-plating / drive-by edits | stays in scope, reports extras instead of doing them |

Add a new eval whenever a failure recurs. The set is meant to grow.
