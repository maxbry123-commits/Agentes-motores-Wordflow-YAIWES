# Regression tests

Minimal infrastructure for checking that prompt edits don't degrade coding quality.

**Contents:** [Layout](#layout) · [Quick check (no API)](#quick-check-no-api) · [Regression run (with API)](#regression-run-with-api) · [Updating the golden](#updating-the-golden) · [Growing the set](#growing-the-set)

---

## Layout

- `test_schemas.py` — smoke tests of Pydantic schemas; no API calls, no key needed. Runs instantly.
- `compare.py` — structural diff of a new output vs the golden.
- `golden/` — golden fixtures:
  - `input_transcript.json` — small transcript (3 semantic blocks)
  - `input_brief.json` — brief with research questions / hypotheses / one respondent
  - `golden_output.json` — expected coded output

---

## Quick check (no API)

```bash
python3 tests/test_schemas.py
```

Should print `PASS` for every test. Failures here mean basic contracts (schemas, citation normalization) are broken — fix these first.

---

## Regression run (with API)

Before committing a prompt edit:

```bash
# 1. Run the pipeline on the golden input
cd tests/golden
python3 ../../scripts/code_transcript.py run input_transcript.json input_brief.json \
  --respondent-id r_1 --fresh

# 2. Compare with the golden
python3 ../compare.py input_transcript.coded.json golden_output.json
```

If `compare.py` prints `✅ Regression-compatible` — the edit is safe.

If there are differences — read them carefully. Small shifts in `interpretive_notes` are expected (free-text field). Shifts in the core (`quote`, `subject_codes`, `content_type`, `research_question_ids`, `hypothesis_support`) signal the edit is changing behavior.

---

## Updating the golden

If a prompt edit deliberately improves quality and you accept the new output as the new standard:

```bash
cp tests/golden/input_transcript.coded.json tests/golden/golden_output.json
```

Commit with a clear message describing what changed and why.

---

## Growing the set

One fixture is not enough for serious regression. As the skill stabilizes, add one fixture per notable case:

- `golden/product_test_interview.*` — tests of product tasks
- `golden/free_form_interview.*` — free-form conversation without tasks
- `golden/difficult_segments.*` — segments where quality historically broke

Rule: when you catch a bug that slipped through existing tests, add exactly that case to `golden/` so it can't pass unnoticed again.
