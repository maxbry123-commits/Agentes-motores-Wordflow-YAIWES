# Troubleshooting

Common failures and their fixes. The pipeline logs to stderr (capture it with the `nohup ... > /tmp/coding.log 2>&1` pattern for long runs); also check the validation report at `coding/*.validation.md`.

**Contents:** [API key not found](#openai_api_key-is-not-set) · [JSON parse failures](#model-did-not-return-parseable-json) · [Citation mismatches](#citation-mismatch-on-every-other-segment) · [Unknown hypothesis ID](#hypothesis_id-x-not-in-brief-in-the-validation-report) · [Slow pipeline](#pipeline-is-slow) · [Checkpoints not picked up](#checkpoints-are-not-resumed) · [Missing respondent ID](#respondent_id-not-found-in-brief) · [Code zoo](#project-accumulates-a-zoo-of-codes) · [Regression tests fail](#regression-tests-fail-after-a-prompt-edit) · [Something else](#something-else)

---

## `OPENAI_API_KEY is not set`

The key was not picked up from `.env`. Check:
1. `.env` is in the **current working directory** (where `claude` or the Python script runs), not inside the skill folder.
2. No spaces around `=`: `OPENAI_API_KEY=sk-...`, not `OPENAI_API_KEY = sk-...`.
3. No quotes around the value (dotenv strips them but the habit is sloppy).
4. No `.env` in the home directory or `~/.config/` shadowing yours — we only load CWD.

---

## "Model did not return parseable JSON"

A structured-output stage failed to parse. Causes:
1. **Rate limit** — the error text may be in the response body instead of JSON. Wait a minute or drop to `gpt-5.4-mini`.
2. **`max_completion_tokens` too small** — the model got truncated mid-JSON. Bump `local_coding.max_completion_tokens` to 6000.
3. **Invalid JSON schema** (a bug in our files) — shows up as "Invalid schema" in the log. Cross-check `CODED_SEGMENT_SCHEMA` in code against the Pydantic class.
4. **Anthropic backend**: JSON parsing is weaker because there's no native strict mode. Either switch this stage to OpenAI or rely on retries — they usually succeed.

---

## "Citation mismatch" on every other segment

The model paraphrases instead of copying verbatim. Options:
1. Loosen the mode: `validation.citation_match_mode: fuzzy` and `fuzzy_threshold: 0.88`. Tolerates minor word edits.
2. If even fuzzy fails often — the model is the problem. Raise `max_retries` to 5 or switch `local_coding` to a stronger model (`gpt-5.4` with `reasoning_effort: high`).
3. Check for weird punctuation or invisible characters in the transcript that break normalization. Open the file in an editor with hidden characters visible.

---

## "hypothesis_id X not in brief" in the validation report

The model invented a hypothesis ID. The prompt isn't strict enough about using only IDs from the brief.
1. Short-term: ignore the warning (the analysis stage filters them out).
2. Long-term: update `references/prompt_local_coding.md` — in the `hypothesis_support` section, include an explicit list of valid IDs in the example. Don't change the schema — this is a prompt issue.

---

## Pipeline is slow

A typical interview (60 min, ~500 utterances, ~80 segments) takes 3–6 minutes on `gpt-5.4` with `reasoning_effort: medium`. If much longer:
1. Check the log to see which stage is slow. Usually `local_coding`.
2. Reduce `context_window_size` from 3 to 1 — shortens every call.
3. Set `local_coding.reasoning_effort: low` — quality drops slightly, speed jumps noticeably.
4. For large runs (>3 interviews), use `nohup` — don't wait synchronously.

---

## Checkpoints are not resumed

A re-run on the same folder starts from scratch:
1. Confirm `--fresh` is not passed.
2. Check that `interview_id` matches the transcript filename — checkpoints live in `coding/<interview_id>/`.
3. If the transcript was edited after the first run, clear checkpoints manually or pass `--fresh`.

---

## `respondent_id` not found in brief

For batch mode, a `respondents_map.json` is required in the project folder, mapping `{"<transcript_filename>.json": "<respondent_id>"}`. Without it, batch mode won't start. For single-interview mode, pass `--respondent-id` explicitly.

---

## Project accumulates a zoo of codes

Run `unify <project_dir>` after every 3–5 interviews, review `unification_proposal.csv`, set `approved=Y` on merges you accept, save. Apply — for now manual or via a TODO `apply-unification` subcommand.

---

## Regression tests fail after a prompt edit

If the golden fixture no longer matches after a deliberate prompt improvement — that's expected. Update the golden by promoting the latest run's output (see `tests/README.md`):
```bash
cp tests/golden/input_transcript.coded.json tests/golden/golden_output.json
```
Then diff carefully to confirm nothing regressed by accident.

---

## Something else

Open an issue with:
1. The captured stderr log (full) — e.g. `/tmp/coding.log` if you used the `nohup` pattern
2. The config used
3. Expected vs actual behavior
4. An anonymized transcript or fragment if data is sensitive
