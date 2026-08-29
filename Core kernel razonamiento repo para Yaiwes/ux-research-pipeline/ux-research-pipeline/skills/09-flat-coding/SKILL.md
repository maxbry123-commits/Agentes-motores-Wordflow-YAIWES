---
name: flat-coding
description: Flat coding of an interview transcript. Trigger — a transcript appears in `2-interviews/<name>.txt`. Produces `.system/coded/<name>.json` per the `coded-interview.v1` schema with segments per the `coded-segment.v1` schema (verbatim, content_codes, content_type ∈ {fact, interpretation, hypothesis}, mapping to RQ and hypotheses). Supports two modes: `agent` (the agent itself, default) and `external` (a shim over `transcript-coding`).
stage: 7
status: core
---

# 09-flat-coding

## What it does

Flat coding of a single interview. The foundational analysis stage — without it, only `07-quick-summary` and `10-saturation-map` work.

Stays close to the respondent's words, no hierarchy. Grouping codes into themes and categories is `13-axial-coding`, **not** this skill.

## Trigger

After `06-transcribe` **and** `06.2-speaker-verify`: `2-interviews/transcripts/json/<name>.json` holds a JSON with verified role attribution (`_speaker_verified: true` in the manifest object). We don't run on long interviews without the verify stage — the swap risk is too high.

## Modes

In `project-config.yaml.analysis.coding_mode`:

- **`agent`** — the assistant codes in its own context. No external LLM API keys required. Long interviews (>1 hour) are coded in parallel by subagents (`use_subagents: true`).
- **`external`** — delegation to the vendored `skills/transcript-coding/` skill. Requires `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GEMINI_API_KEY` in `.env`. Makes sense at ≥10 interviews or when strict Pydantic validation is needed.

Both modes write the result **to the same schema** — `shared/schemas/coded-interview.v1.schema.json`. Downstream skills (10–18) don't distinguish who coded.

### Default by N interviews

At the moment `09-flat-coding` runs, the agent **checks the actual N** (the count of transcripts in `2-interviews/transcripts/json/`) and compares it to the `coding_mode` setting:

| N interviews in project | Recommended mode | What the agent does |
|---|---|---|
| 1–3 | `agent` (no subagents) | If `coding_mode: agent` and `use_subagents: false` — it runs. Otherwise — asks whether the complex mode is really needed. |
| 4–9 | `agent` + `use_subagents: true` | If the config has `use_subagents: false` — proposes to the researcher: "we have N interviews; without subagents this will be slow. Enable use_subagents: true?" |
| ≥10 | `external` | If the config has `coding_mode: agent` — it **must** propose: "we have N≥10 interviews; on this sample size external (via API) is cheaper and more predictable than N parallel agent subagents. Switch? If yes — we'll need an API key; I'll help set it up." In autonomous mode — no switch, but a note in `concerns.md`: "coding_mode kept as agent at N≥10 — this will be expensive." |

This rule does **not** forbid the researcher from keeping `coding_mode: agent` on 10+ interviews — they can confirm that explicitly. But without confirmation, the default is to propose the switch.

### API-key onboarding for external

If the researcher accepted the switch to `external` (or opened a project with `coding_mode: external` from the start) — the agent, **before** the first `transcript-coding` call:

0. **Checks that the `transcript-coding` skill is vendored locally.** If `skills/transcript-coding/SKILL.md` doesn't exist — run `bash shared/scripts/install-transcript-coding.sh`. The script looks for upstream at `~/.claude/skills/transcript-coding/`, copies it into the pipeline, and clears readonly. If it didn't find it — it prints instructions for the researcher.
   Don't call `transcript-coding` from the system path directly: the pipeline uses only the vendored version, so upstream updates don't break projects.

1. Checks `.env` for the key from `analysis.external_coding.api_key_env_var` (default `OPENAI_API_KEY`).
2. If the key exists — tries a short test call on one utterance from the first transcript. If 200 OK — proceeds.
3. If the key is missing — **stops and asks the researcher**:

   > "External mode needs the API key `<variable_name>`. I didn't find it in `.env`. Where to get it:
   > - **OpenAI**: https://platform.openai.com/api-keys → create a key → save it.
   > - **Anthropic**: https://console.anthropic.com/settings/keys → Create key.
   > - **Gemini**: https://aistudio.google.com/app/apikey → Create API key.
   >
   > Put a line `<variable_name>=sk-...` in `.env` (it's in `.gitignore`, it won't leak), save the file, and I'll try again. Or say 'switch to agent' and I won't require a key."

4. If the key existed but the test call returned 401/403 — tell the researcher the key is invalid and to check it.
5. On 429 (rate limit) — warn that processing will be slower (with exponential backoff between requests) and ask whether to continue.

**Don't save the key** in `agent-notes.md`, in `.system/runs/`, or in logs. It's a `secret`. Only presence check and a test call.

## Inputs

- `2-interviews/transcripts/<name>_transcript.txt` (readable version) **and** `2-interviews/transcripts/json/<name>.json` (structured, from ux-transcribe, after speaker-verify).
- `project-config.yaml` — `research_questions`, `hypotheses`, `analysis.coding_mode` and parameters.
- `1-methodology/brief.md` — short project context.
- `1-methodology/screener.md` or explicit notes — for the `speaker → respondent_id` mapping.
- `shared/coding-vocabulary.md` — the team's canonical codes (if present).
- `shared/calibration-examples/flat-coding-examples.md` — domain reference standards for fact / interpretation / hypothesis. **Must be read** before the first pass.

## Outputs

- `.system/coded/<name>.json` — per the `coded-interview.v1` schema.
- `.system/runs/flat-coding-<name>-<timestamp>.log` — run log.
- `.system/prompts-versions/flat-coding-<name>-<timestamp>.json` — prompt snapshot.

Does not write: anything to `3-analysis/` directly. The next step does that (`11-matrix-pivot`, `13-axial-coding`, etc.).

## Behavior — `agent` mode

See the full prompt in `prompts/flat-coding.md`. Condensed logic:

1. Read the transcript. Parse it into utterances (one turn — one record with timecode and speaker).
2. Map speaker → respondent_id from the screener or from the researcher's notes. If ambiguous — ask (assistive) or note it in `concerns.md` (autonomous).
3. Segment: each meaningful chunk = one segment (`coded-segment.v1`). A segment can be shorter or longer than one turn, depending on meaning.
4. For each segment, produce the schema fields:
   - `verbatim` — the exact text from the transcript.
   - `content_type` — `fact` / `interpretation` / `hypothesis` (see definitions in the schema).
   - `content_codes` — 1–4 flat codes close to the words.
   - `research_question_ids` — which RQs it addresses.
   - `hypothesis_support` — link to hypotheses, if any.
   - `confidence` — your confidence in the coding being correct.
5. Verbatim check: each `verbatim` must exist in the source transcript word for word. If not — flag the segment `confidence: low` and put it in `coding_meta.verbatim_check.failed_segment_ids`.
6. Write `coding_meta` with `coded_by: agent`, `coding_mode: agent`, `model: <your name>`, `schema_version: coded-segment.v1`.

## Behavior — `external` mode (shim over transcript-coding)

1. Prepare the input for `transcript-coding`:
   - `transcript`: path to `<name>-raw.json` or the read `<name>.txt`.
   - `brief`: RQ + hypotheses from `project-config.yaml` + short business context.
   - `respondents_map`: speaker → respondent_id.
   - `config`: backend and hermeneutic_preset from `project-config.yaml.analysis.external_coding`.
2. Call `transcript-coding`.
3. Take the result, map it to the `coded-interview.v1` schema (field names may differ — normalize them).
4. Write to `.system/coded/<name>.json` with `coding_meta.coded_by: external:transcript-coding`.

## Subagent strategy (optional, for `agent` mode)

Apply when `analysis.agent_coding.use_subagents: true` OR when:
- interview duration > 60 minutes;
- several interviews are queued at once (a batch);
- you're a high-tier model and it makes sense to delegate to a cheaper one.

Architecture — **manager / worker / judge**:

1. The **manager** (current agent) slices the transcript into chunks of `chunk_size_utterances` (default 40 utterances, ~5–7 minutes of conversation). Chunks **overlap by 2 utterances** — so a worker can segment across the boundary.
2. The **worker** applies the full `prompts/flat-coding.md` prompt, but only to its chunk. Produces partial JSON.

   ### The worker model is NOT optional

   The worker is **always called with an explicitly specified model**. This is a rule, not a recommendation. If workers launch without `model:`, they inherit the parent's model — expensive and slow.

   Default: `claude-sonnet-4-6`. That's enough for flat coding against the project vocab.

   Agent-tool call template (Claude Code / Cowork):

   ```
   Agent(
     description="flat-coding worker chunk N",
     subagent_type="general-purpose",
     model="sonnet",     # ← required
     prompt="<full prompt from prompts/flat-coding.md with chunk N>"
   )
   ```

   Possible overrides via `project-config.yaml.analysis.agent_coding.worker_model`:
   - `null` (or field absent) → uses the default `claude-sonnet-4-6`.
   - `"claude-haiku-4-5"` → acceptable for short chunks (≤30 utterances), but requires a stricter `judge_model` on self-check.
   - `"claude-sonnet-4-6"` → default.
   - `"claude-opus-4-7"` → only on the researcher's explicit request for critically important interviews.

   **Never leave `model:` empty in a worker's Agent call.** The manager must fill in the value before the call.
3. The **manager** stitches the results:
   - dedup at chunk seams (if workers extracted the same segment);
   - renumber `segment_id` across the whole file;
   - reconcile `respondent_id` (all workers must use the same mapping — passed in their prompt).
4. The **judge** (if `judge_model` is set) does a sampling QA:
   - a random sample of 10% of segments;
   - verbatim check of 100% of quotes against the source transcript;
   - a sanity check of `content_type` (no `fact` segments where the respondent is clearly speculating).
5. Judge results → `coding_meta.verbatim_check` + a log in `.system/runs/`.

Without `use_subagents`, the manager does all of this itself, sequentially. It's slower but simpler to verify.

### Mandatory programmatic validation after each worker

Once a worker returns JSON, **before considering that piece of work closed**, the manager runs:

```bash
python3 "shared/scripts/validate-coded.py" \
  ".system/coded/<name>.json" \
  --expected-model "<requested model, e.g. claude-sonnet-4-6>"
```

The script checks:

- JSON-schema validation against `coded-interview.v1`;
- `segments_per_minute` in the 0.5–5.0 corridor (FAIL outside), 1.0–2.5 ok;
- `content_type` shares (fact 35–75 / interp 15–50 / hyp 0–25 — FAIL outside);
- `respondent_share` ≥ 30% (FAIL below — almost always a speaker swap);
- `verbatim_failed_share` ≤ 5%;
- `coding_meta.model` matches the requested one (FAIL on subagent drift);
- `schema_version = 'coded-segment.v1'`;
- blacklisted category codes (warn / strict-fail).

Exit codes: `0` ok, `2` sanity FAIL, `3` schema FAIL, `1` technical.

**Manager behavior by exit code:**

| Exit | What the manager does |
|---|---|
| `0` | Accepts the result; marks the interview processed, moves to "After the pass — mandatory". |
| `2` (sanity) | Analyzes the FAILs. If a `content_type` skew or `segments_per_minute` — re-runs the same worker with a refined instruction ("your hypothesis is 23%, needs 5–15"). If `coding_meta.model` mismatch — re-runs on the correct model. No more than two retries per file, then escalate to the researcher. |
| `3` (schema) | Re-run, citing the specific schema error from the report. |
| `1` (technical) | Check that the file was written and is valid JSON. If `jsonschema` isn't installed — `pip install --break-system-packages jsonschema referencing`. |

**Don't stockpile FAIL results** in `.system/coded/` as finished. Until validation succeeds, the file counts as a draft; `agent-notes.md` records the attempt with its exit code and reason.

## DoD

- [ ] `shared/scripts/validate-coded.py` returned exit code `0` (with `--expected-model` equal to the requested one).
- [ ] `coding_meta.verbatim_check.failed` ≤ 5% of segments.
- [ ] Every segment has `content_codes` (at least 1) and `content_type`.
- [ ] Segments with `speaker: interviewer` are kept, but should **not** have `hypothesis_support` (it's not evidence).
- [ ] `coding_meta.schema_version = 'coded-segment.v1'`.
- [ ] `coding_meta.model` matches the requested model (no subagent drift).
- [ ] The prompt snapshot (`flat-coding.md` v0.3) is saved in `.system/prompts-versions/`.
- [ ] The transcript passed `06.2-speaker-verify` (or was explicitly skipped with a note in `agent-notes.md`).

## What it does NOT do

- Doesn't do axial coding (that's `13-axial-coding`).
- Doesn't look for links between interviews (`12-link-detector`).
- Doesn't group codes into themes (`13-axial-coding`).
- Doesn't build respondent cards (orchestration does that afterward; see `## After the pass — mandatory`).

## Failure modes

- **Verbatim validation failed on >5% of segments** — this happens on hard diarizations or speech with self-corrections. Flag the segments `confidence: low`, note the count in `concerns.md`, and ask the researcher whether to redo the transcript.
- **Very long transcript (>2 hours)** — use the subagent strategy with `chunk_size_utterances: 30` and `use_subagents: true`. Without subagents you risk hitting the context limit.
- **`transcript-coding` not installed in `external` mode** — in chat: "coding_mode: external was chosen, but the `transcript-coding` skill isn't found. Install it (Cowork → Plugins → Install) or switch to `coding_mode: agent` in `project-config.yaml`." Don't fall back automatically — this is a methodologically significant decision.
- **Too many codes per segment (>5)** — usually a sign the segment is too large. Split it.
- **Context bloated by a long transcript** — switch to `use_subagents: true`, don't try to be a hero in a single pass.

## After the pass — mandatory

After a successful `09-flat-coding` for an interview:

1. Create or update `3-analysis/respondents/<ID>.md` (using the `_template-respondent.md` template).
2. Update `3-analysis/themes/*.md` for themes mentioned in this interview (create new maps for new themes). At this stage a theme is just a label; the full theme structure per `theme.v1` appears after `13-axial-coding`.
3. Run `11-matrix-pivot` — update `3-analysis/matrix.xlsx`.
4. Run `10-saturation-map` — update saturation in the matrix and `3-analysis/_index.md`.

This is an incremental process — **don't batch 5 interviews, do it right after each one**. Otherwise you lose the early "no saturation yet" signal.

## Mode behavior

- **assistive**: after coding — a short chat message: "transcribed and coded {{name}}, {{N segments}}, brief summary — here." If verbatim_check.failed > 5% — raise a flag.
- **autonomous**: quietly, put it in `.system/coded/` and move on. In `concerns.md` — segments with `confidence: low` and failed verbatim.

## STOP — handoff after this skill

`09-flat-coding` is one of the "heaviest" boundaries of the pipeline (see AGENT.md §14.1). Hard rule §14.0: **don't run the next skill without the researcher's explicit confirmation.**

Handoff triggers by `session_budget` (from `project-config.yaml`):

- `low` — handoff is **mandatory** every 3–4 interviews within `09` AND mandatory once all interviews are done.
- `normal` — handoff is **mandatory** once all interviews are done; within `09` — on request.
- `high` — handoff only on an objective heuristic ("session > 2 h / >200K tokens read").

When a trigger fires:

1. Add a **"Handoff to next session"** section to the top of `.system/agent-notes.md` (format — AGENT.md §14.3). Inside: what's been coded, which interviews aren't yet, what to read in the new session (minimum — `_index.md`, `coded/*.json`, the last updated respondent file), what NOT to read (raw transcripts).
2. Output a STOP-handoff block per the §14.2 template — with separators, as the end of the answer, not in passing.
3. **Don't run** `10-saturation-map`, `11-matrix-pivot`, `13-axial-coding`. Wait for the researcher's answer.

If the researcher answers "continue here" — record that decision as a short dated entry in `agent-notes.md` and continue in the current session. **Silence ≠ confirmation**, wait.
