# Worked Example: Fresh-Context Review Catches an Unverified PR

## Situation

A coding agent says it fixed a stale-news bug and reports that tests pass. The maintainer wants to merge quickly but does not fully trust the completion claim.

## Workflow selected

- [Fresh-Context Code Review](../workflows/04-fresh-context-code-review.md)
- [Regression-Test-First Bug Fix](../workflows/13-regression-test-first-bugfix.md)

## Agent brief

```text
Review this branch from a fresh context. Do not trust the author's summary.

Goal: verify that stale articles no longer dominate the digest.
Scope: selection logic, tests, docs touched by the branch.
Verification required: run the targeted test suite and one live dry-run or fixture-backed digest selection check.
Stop if: credentials, production delivery, destructive commands, or unrelated refactors are needed.
```

## What the reviewer checks

1. Reads the issue and intended behavior.
2. Inspects the diff for unrelated edits.
3. Finds the test that proves old articles are excluded.
4. Runs the targeted test command.
5. Runs the digest selection path in dry-run mode or with fixtures.
6. Reports exact evidence instead of saying “looks good.”

## Example finding

```text
Blocking issue: the PR updates ranking but does not add a regression test for undated articles.
Evidence: tests/test_selection.py has no case covering undated_seen_ge_24.
Required fix: add a fixture with undated and dated articles, then verify older_than_72h=0.
```

## Example final review

```text
Recommendation: approve after regression test added.
Verification run:
- python -m pytest tests/test_selection.py -q -> 12 passed
- python scripts/run_digest.py --dry-run -> final_digest_selected=42, older_than_72h=0
Residual risk: live source timestamps can still be wrong; scheduled monitoring should watch source age.
```

## Lesson

A fresh-context review is not a second summary. It is a distrustful evidence pass that protects the maintainer from merging an agent's confidence instead of verified behavior.
