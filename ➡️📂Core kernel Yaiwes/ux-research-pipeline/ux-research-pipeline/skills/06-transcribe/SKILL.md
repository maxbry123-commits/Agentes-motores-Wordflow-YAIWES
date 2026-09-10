---
name: transcribe
description: A shim over the upstream `ux-transcribe` skill (lives in `skills/ux-transcribe/`). Transcribes audio/video from `0-input/` or `2-interviews/` via Voxtral. Trigger — a media file appears in one of these folders. Produces `<name>_transcript.txt` and `json/<name>.json` in a `transcripts/` subfolder of the same folder, plus `.system/runs/transcribe-<name>-<timestamp>.log`.
stage: 6.1
status: external (shim)
upstream_skill: ux-transcribe (vendored at `skills/ux-transcribe/`)
---

# 06-transcribe (shim)

## What it does

A thin wrapper over the upstream `ux-transcribe` skill, which lives **inside** this repository at `skills/ux-transcribe/`. No external downloads needed — the `transcribe_folder.py` script is available via a relative path.

## Trigger

A file with one of these extensions appears in `0-input/` or `2-interviews/`: `.m4a`, `.mp3`, `.wav`, `.mp4`, `.mov`, `.mkv`, `.webm`.

## What to check BEFORE running (hard checklist)

1. **`MISTRAL_API_KEY`** lives in `~/.config/ux-transcribe/.env` (not in the pipeline `.env`). This is the upstream skill's own store. If the file is missing — first try `bash shared/scripts/setup-mistral.sh` (it checks and, if needed, prompts the researcher). If the researcher hasn't obtained the key yet — follow step 0 in `skills/ux-transcribe/CLAUDE.md`.
2. **`ffmpeg`** is installed (`ffmpeg -version`). If not — `skills/ux-transcribe/SKILL.md` describes per-platform auto-install.
3. **Python packages**: `python3 -c "import mistralai, httpx, dotenv"`. On ImportError — `python3 -m pip install --break-system-packages mistralai httpx python-dotenv`.

If any item is unmet — **stop and ask the researcher**; do not write your own pipeline via direct HTTP calls. See AGENT.md §2.7 (stop-on-anomaly) and §2.8 (don't reinvent).

## Requesting companion materials (hard rule)

**When interview files first appear in `2-interviews/` (or right after transcription), you MUST actively ask the researcher about companion materials.** Don't silently transcribe and move on — that loses context you can't recover later.

What to ask (in a single message, don't fragment it):

> Before we go further — do you have anything else for these interviews besides the audio itself? It's useful to pull in:
>
> - notes you took during the interview (field notebook);
> - debrief notes from a partner (or your own right after the interview);
> - a sample log / recruitment request (who was invited, who agreed, who declined);
> - screenshots or artifacts the respondent showed.
>
> If you have them — put them in `2-interviews/inscriptions/` (naming by respondent is handy: `R03-notes.md`). If not, just say "none" and I'll proceed without them.

**Don't start `09-flat-coding` until the researcher has answered.** Responses:

- "none" / "nothing else" → continue without inscriptions. Note it in `agent-notes.md` (one line: "inscriptions — none, confirmed in chat").
- "here, I added them" / a list of files → go through `2-interviews/inscriptions/`, read the contents, add a short conspectus to `agent-notes.md` (what's in each file, 1–2 lines each). After that you can proceed to coding.
- Silence → wait. **Do not interpret silence as "none."**

If the interview files are already transcribed and the inscriptions are added later — pull them in before `13-axial-coding` too (that's the second reasonable point).

## Behavior

1. Determine the target folder and the recording type:
   - `0-input/<name>.<ext>` → stakeholder meeting (`--type meeting` or `auto`).
   - `2-interviews/<name>.<ext>` → in-depth interview (`--type ux-interview`).

2. Run the upstream script **with the absolute path** to the project folder. Spotlight won't find the `0-input/` or `2-interviews/` folder by name — pass the full path:

   ```bash
   nohup python3 "skills/ux-transcribe/scripts/transcribe_folder.py" \
     "<absolute path to 2-interviews>" \
     --skip-existing --type ux-interview \
     > ".system/runs/transcribe-$(date +%Y%m%d-%H%M%S).log" 2>&1 &
   echo "PID: $!"
   ```

3. **Monitor actively.** Every 60–90 seconds, `tail -20` the log file. Never go quiet in the background for more than 5 minutes — see CLAUDE.md (the intermediate-status rule).

4. After success (`exit code 0`, "Done." in the log):
   - Transcripts are in `<target folder>/transcripts/<name>_transcript.txt`.
   - JSON versions — in `<target folder>/transcripts/json/<name>.json`.
   - Diagnostics — in `<target folder>/transcripts/_diagnostic.json`.
   - Copy the final log from `/tmp/ux-transcribe.log` (if it's there) into `.system/runs/transcribe-<name>-<ts>.log`.

5. **Right after transcription, you MUST run `06.2-speaker-verify`** (if the interview is longer than 40 minutes, or upstream emitted the warning `⚠ Found N speakers, merging to 2`). Don't move on to `09-flat-coding` without this pre-pass — otherwise you risk a speaker swap.

## Inputs

- An audio/video file in `0-input/` or `2-interviews/`.
- `1-methodology/screener.md` (optional, for speaker → respondent_id mapping on the next step).

## Outputs (ux-transcribe schema)

```
<target folder>/
├── <name>.m4a                       ← original (deleted once shipped/archived)
└── transcripts/
    ├── <name>_transcript.txt        ← readable transcript
    ├── _diagnostic.json             ← pass diagnostics
    └── json/
        └── <name>.json              ← structured (input for 09-flat-coding)
```

And in `.system/runs/`:
```
transcribe-<name>-<timestamp>.log
```

## DoD

- [ ] `<name>_transcript.txt` exists and validates via `skills/ux-transcribe/scripts/validate_transcripts.py "<target folder>"`.
- [ ] The JSON version in `transcripts/json/` exists and is non-degenerate (`>= 50` utterances for an interview `>= 10` minutes long).
- [ ] A log file is created in `.system/runs/`.
- [ ] `06.2-speaker-verify` has been run (or explicitly deferred with a note in `agent-notes.md` flagged "needs speaker-verify").

## Failure modes — stop-on-anomaly

- **Voxtral returned an error or 0 characters** on the first chunk — this is a hard stop. Log to `.system/runs/`, message the researcher: "transcription of `<name>` failed on chunk 1, not continuing. Want me to show `_diagnostic.json`?" Don't write a partial result as a finished file.
- **Process killed by the harness / interrupted** (didn't reach "Done." in the log) — don't treat the surviving transcripts as final. Re-run with `--skip-existing` on the files that remain.
- **Poor diarization** (warning `⚠ Found N speakers, merging to 2`) — mandatory `06.2-speaker-verify` afterward.
- **Huge file** (>2GB video) — extract the audio track first via `ffmpeg -vn -acodec copy`, then pass only the audio. ux-transcribe can do this itself, but on a >2GB MP4 it may hit I/O limits.

## What it does NOT do

- Doesn't "clean up the meaning" of the transcript. Voxtral wrote "uhh" — we keep "uhh".
- Doesn't commit files to git (NDA).
- **Doesn't run a homegrown Mistral pipeline as a fallback.** If the upstream skill isn't working for some reason — stop and ask, don't write your own via direct HTTP calls.

## Audio — retention policy

Once a project moves to `status: shipped` or `archived`, the source audio/video in `2-interviews/` and `0-input/` is deleted (AGENT.md §11.5). Transcripts, JSON versions, and `_diagnostic.json` remain.
