---
name: speaker-verify
description: Checks and fixes "Interviewer ↔ Respondent" role confusion in transcripts from ux-transcribe. Step 1 — a heuristic swap metric (`scripts/detect_swaps.py`). Step 2 — an LLM re-attribute pass, if the heuristic raised a flag. Trigger — after `06-transcribe`, before `09-flat-coding`. Mandatory for interviews longer than 40 minutes and on the `⚠ Found N speakers, merging to 2` warning from ux-transcribe.
stage: 6.2
status: core
---

# 06.2-speaker-verify

## Why

In long interviews, Voxtral (via Mistral) **systematically swaps the interviewer and respondent roles** — especially in the second half of the recording, on long summarizing turns, and in usability scenarios. Across recordings we've seen swaps in nearly every long file (from a couple to several dozen swaps per interview).

If left unfixed, every JSON coded by `09-flat-coding` without a corrected mapping contains "evidence" where the interviewer's speech is masked as the respondent's. The worst case is an artifact like "the respondent admitted X" when X was actually a leading question from the interviewer. This is critical for verbatim quotes and for hypothesis testing.

## Trigger

Run it **mandatorily** after `06-transcribe`, before `09-flat-coding`, in these cases:

1. **All interviews with a recording length > 40 minutes — no conditions.** Duration alone is a sufficient signal; don't rely on the heuristic only, since swaps can occur even when the heuristic pass shows no warning.
2. ux-transcribe emitted the warning `⚠ Found N speakers, merging to 2` (visible in the log or in `_diagnostic.json.events`).
3. The heuristic script (`scripts/detect_swaps.py`) returned exit code 2 for at least one file in the folder.
4. The researcher explicitly asked to "check the speakers."

In all other cases (interviews ≤ 40 min, clean heuristic) — skip it. Don't over-engineer on short meeting recordings where roles are stable from the start.

## Inputs

- `<project>/2-interviews/transcripts/json/<name>.json` — output of `06-transcribe` (an array of `{start,end,speaker,text}`).
- `<project>/2-interviews/transcripts/<name>_transcript.txt` — human-readable version (for the final rewrite).
- `1-methodology/guide.md` (optional) — interview structure, helps the LLM understand which turns are the leading ones.
- `1-methodology/screener.md` (optional) — baseline demographics.

## Outputs

- `<project>/.system/runs/speaker-verify-<name>-<timestamp>.json` — report of the heuristic stage (input for the LLM pass).
- `<project>/2-interviews/transcripts/json/<name>.json` — updated JSON with corrected roles + a `_speaker_verified: true` field in the first object of the array (optionally — a manifest object).
- `<project>/2-interviews/transcripts/<name>_transcript.txt` — updated text version (roles in the header/turn labels rewritten).
- `<project>/.system/runs/speaker-verify-<name>-<timestamp>.log` — log of the LLM pass with the count of flipped turns and the rationale.

The old JSON version is kept as `<name>.json.pre-verify` in the same `json/` folder — so you can roll back if the LLM pass overcorrected.

## Step 1 — heuristic detect_swaps

```bash
python3 "skills/06.2-speaker-verify/scripts/detect_swaps.py" \
  "<absolute path to 2-interviews>/transcripts/json/"
```

The script reads all `*.json` files and, for each, computes:

- `suspicious_interviewer` — turns labeled as Respondent but containing interviewer markers ("Could you tell me", "Describe", "And why", "To summarize", "Click", "Press", a standalone "Got it.", etc.) in short turns (<250 characters).
- `suspicious_respondent` — long (>300 character) turns labeled as Interviewer, with personal-narrative markers ("I was looking", "I had", "When I", "Personally I").
- `suspicion_rate` — share of suspicious turns out of the total.
- `needs_llm_pass: true` triggers when:
  - duration > 40 minutes, OR
  - ≥ 3 suspicious turns, OR
  - suspicion_rate ≥ 2%, OR
  - the share of respondent turns < 30%.

Exit code: `0` if no file needs an LLM pass, `2` if at least one does, `1` — technical error.

**Don't run the LLM pass for files where `needs_llm_pass: false`** — it saves time and avoids false-positive edits.

## Step 2 — LLM re-attribute pass

Runs for files flagged `needs_llm_pass: true` **or** for any interview > 40 min (see triggers). Done as a **separate subagent** via the Agent tool.

### Worker model

Default — **Claude Haiku 4.6**. Rationale: role attribution is a binary task that doesn't require deep methodology — Haiku 4.6 handles it and costs a fraction of Sonnet. Across a dozen-plus interviews the difference is noticeable.

The `worker_model` in the Agent tool **must be specified explicitly** (just as for `09-flat-coding` workers). Template:

```
Agent(
  description="speaker-verify worker <interview name>",
  subagent_type="general-purpose",
  model="haiku",                    # ← required
  prompt="<full worker prompt + json contents>"
)
```

Escalate to Sonnet 4.6 only if **a double Haiku pass disagrees on >10% of labeled turns** (see "Double-pass with disagreement" below).

### Double-pass with disagreement

To catch cases where Haiku systematically errs, we run **two independent passes** on the same file:

1. Worker A with Haiku 4.6 — goes in "fresh," no hints.
2. Worker B with Haiku 4.6 — same prompt, but with the instruction "be stricter: if you have the slightest doubt that speech is from the respondent, leave it as interviewer."
3. The manager compares the outputs: for each utterance, it checks whether A and B agree on `speaker`.
4. If **disagreement ≤10% of utterances** — accept the consensus (where they agree, lock it; where they diverge, take the more conservative one, i.e. respondent → interviewer).
5. If **disagreement >10%** — that's a signal the task is ambiguous. Then:
   - Run a third pass on Sonnet 4.6 with the same prompt.
   - If Sonnet resolves the disagreement (its output matches one of the Haiku passes ≥90%) — accept the one it matches.
   - If Sonnet also diverges — set `verification_confidence: "uncertain"` on the contested utterances and **ask the researcher** to eyeball them in assistive mode. In autonomous mode — list the specific timecodes in `concerns.md`.

This algorithm sharply reduces false-positive swaps: a single pass can leave residual swaps in a majority of long files, while a double pass should bring that down to nearly none.

### Worker prompt

> You receive an array of utterances from a Voxtral transcription of a UX interview (fields `start`, `end`, `speaker`, `text`). Voxtral systematically confuses the "Interviewer" and "Respondent" roles in long recordings. Your task is to **decide, from the content of each turn, who is speaking**, and to change `speaker` where needed.
>
> Role signals:
>
> - **Interviewer**: asks questions, runs the script, gives instructions ("Could you tell me", "Describe", "Click", "Press"), summarizes the respondent's words ("If I understood correctly, you…", "You said that…"), uses fillers ("Okay", "Got it", "Right", a standalone "Mm-hm"), follow-up questions ("And why?", "What did you mean by that?").
> - **Respondent**: recounts personal experience in the first person ("I was looking", "I had", "when I"), describes their own actions, preferences, emotions. Long narratives. Concrete details from life.
>
> **Hard rule**: change `speaker` **only when you're sure**. On doubt, leave it as is and add the field `verification_confidence: "uncertain"`. On confident edits — `verification_confidence: "high"`. On confident confirmations — `verification_confidence: "confirmed"`.
>
> **Don't merge turns, don't change text, don't change timecodes** — only `speaker`. Keep all utterances in the same order.
>
> On each change, add an `original_speaker` field (what it was before the edit) so it can be rolled back.
>
> At the end, add a manifest object: `{"_speaker_verified": true, "verified_at": "<timestamp>", "swaps_applied": N, "uncertain": M, "model": "<your model>"}` — as the first element of the array.

### Result control

After the worker finishes, the manager (you) checks:

1. **The array length is the same** (the worker must not merge or delete turns).
2. **Timecodes are unchanged.**
3. **The skew didn't grow**: after the edit, the share of respondent turns should be in the 50–80% range. If the worker flipped, say, 80% of turns and made the interviewer the respondent — that signals the prompt fired in reverse (a pendulum). Roll back to `<name>.json.pre-verify` and ask the researcher to eyeball it.
4. **The manifest object is present** — `_speaker_verified: true`, `swaps_applied`, `model`.
5. **Re-run `detect_swaps.py`** on the corrected file. `suspicion_rate` should drop (if it was >5% → now <2%). If it didn't drop — log to `.system/runs/` and escalate.

## Rewriting `_transcript.txt`

Once the JSON is corrected — regenerate `<name>_transcript.txt`:

1. Read the updated JSON.
2. Group by `speaker`, line format: `[HH:MM:SS – HH:MM:SS] Role: text` (the same as in the source file).
3. Save, overwriting the source `_transcript.txt`.
4. The old version is kept as `<name>_transcript.txt.pre-verify`.

## DoD

- [ ] `detect_swaps.py` has run, result saved to `.system/runs/speaker-verify-<name>-<timestamp>.json`.
- [ ] If the `needs_llm_pass: true` flag fired — the LLM pass ran and its result confirms `suspicion_rate` dropped by at least half.
- [ ] `<name>.json` updated, `<name>.json.pre-verify` saved.
- [ ] `<name>_transcript.txt` updated, `<name>_transcript.txt.pre-verify` saved.
- [ ] The manifest object `_speaker_verified: true` is present in the JSON.
- [ ] `agent-notes.md` records: "verify ran, N swaps fixed" (a short line).

## Failure modes

- **`detect_swaps.py` failed with a JSON-decode error** — the JSON from ux-transcribe is corrupt. Re-run transcription with `--skip-existing` on that file.
- **LLM pass flipped more than 50% of turns** — the prompt fired in reverse, or the markers are interfering. Roll back to `.pre-verify`, note it in `agent-notes.md`, ask the researcher to check manually (or call a second pass on a stronger model).
- **After the LLM pass, `suspicion_rate` didn't drop** — the worker couldn't tell the roles apart (happens in interviews where the interviewer narrates a lot). Flag it in `concerns.md`; don't pass this file to `09-flat-coding` without an explicit "ok" from the researcher.
- **The heuristic `detect_swaps.py` gives a false positive** on the respondent's short clarifying turns ("Got it?", "Okay.") — that's normal. The LLM pass will filter it out.

## Mode behavior

- **assistive**: after the run — a short chat message: "checked speakers on N files, fixed attribution in M of them (Sonnet, X swaps on average). We can code now." If there are `uncertain` >= 5 per file — raise a flag and ask the researcher whether to redo it.
- **autonomous**: quietly, in `concerns.md` — a list of files where `suspicion_rate` stayed > 2% after the pass, plus which turns are marked `uncertain`.

## What it does NOT do

- Doesn't transcribe from scratch — that's `06-transcribe`.
- Doesn't do embedding-based diarization — that's the domain of `ux-transcribe`, not ours.
- Doesn't code — that's `09-flat-coding`.
- Doesn't try to recover missing turns — only reshuffles `speaker` on existing ones.

## History

- **v0.2** — Calibration after a repeat run:
  - The trigger for interviews > 40 min is now **unconditional** (previously it also required a heuristic flag or warning; that missed several swaps).
  - The LLM pass moved from Sonnet to **Haiku 4.6** — the task is binary, the quality difference is negligible, the savings are large.
  - Introduced **double-pass with disagreement**: two independent Haiku passes; on ≤10% disagreement — consensus, on >10% — a third pass on Sonnet or an uncertain flag.
- **v0.1** — created to address speaker swaps. Previously swaps were fixed manually after coding, which was methodologically poor. We moved this in as a pre-pass.
