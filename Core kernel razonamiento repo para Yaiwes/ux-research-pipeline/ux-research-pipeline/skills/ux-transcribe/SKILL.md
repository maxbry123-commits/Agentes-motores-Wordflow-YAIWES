---
name: ux-transcribe
description: >-
  Transcribe audio files (interviews, meetings, any recordings) from a local
  folder using Mistral Voxtral API. Use when the user says "Transcribe" or
  "Transcription" followed by a folder name or task ID.
  Finds audio files on disk, processes them, and saves transcript .txt files.
  Automatically detects recording type and speaker roles.
---

# Transcribe

Transcribe audio files (in-depth interviews, meetings, any recordings) via Mistral Voxtral Mini API.
Automatically detects session type (interview, meeting, presentation) and assigns speaker roles.

## Trigger

Activate when the user message matches: keyword + folder name or task ID.

Keywords (case-insensitive): transcribe, transcription, transcript.
Folder/task ID examples: `TICKET-123`, `Meeting 2026-04-01`, `Sprint Review`, any folder name.

## Prerequisites check — auto-install

Before first run, verify and **automatically fix** each prerequisite. On Windows use `python` and `pip` instead of `python3` and `pip3`.

1. **API key** — check if `~/.config/ux-transcribe/.env` (macOS/Linux) or `%APPDATA%\ux-transcribe\.env` (Windows) exists and contains `MISTRAL_API_KEY`.

   If missing, ask the user: "I need a Mistral API key. Get one at https://console.mistral.ai/ (API Keys → Create new key, the free tier works) and paste it here."

   When the user provides the key, **save it automatically**:

   **macOS/Linux:**
   ```bash
   mkdir -p ~/.config/ux-transcribe && echo "MISTRAL_API_KEY=<key>" > ~/.config/ux-transcribe/.env
   ```
   **Windows:**
   ```powershell
   New-Item -ItemType Directory -Force -Path "$env:APPDATA\ux-transcribe"; Set-Content "$env:APPDATA\ux-transcribe\.env" "MISTRAL_API_KEY=<key>"
   ```

2. **ffmpeg / ffprobe** — check: `ffmpeg -version`. If not found, **install automatically**:

   **macOS:** `brew install ffmpeg` (if brew missing: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`, then retry)
   **Windows:** `winget install ffmpeg`

   Tell the user: "Installing ffmpeg — it is required for working with audio."

3. **Python packages** — check: `python3 -c "import mistralai, httpx, dotenv"`.
   If ImportError, **install automatically**:

   ```bash
   python3 -m pip install mistralai httpx python-dotenv
   ```

   Tell the user: "Installing the Python packages for the Mistral API."

After all prerequisites are satisfied, proceed to the workflow.

## Locating the script

The pipeline script is `scripts/transcribe_folder.py` **relative to this SKILL.md file**.

### Cursor

Run directly:
```bash
python3 ~/.cursor/skills/ux-transcribe/scripts/transcribe_folder.py "/path/to/TICKET-123"
```

### Claude Code

The user runs `claude` from the `ux-transcribe` directory. The script is at `scripts/transcribe_folder.py` relative to `CLAUDE.md`:
```bash
python3 scripts/transcribe_folder.py "/path/to/TICKET-123"
```

## Workflow

### Step 1 — Parse folder name

Extract the folder name from the user message (e.g. `TICKET-123`, `Meeting 2026-04-01`, `Sprint Review`).
If the user provides a full path, use it directly.

### Step 2 — Find the folder

Search for a folder with the given name. Use platform-appropriate commands:

**macOS:**
```bash
mdfind "kMDItemFSName == 'FOLDER_NAME' && kMDItemContentTypeTree == 'public.folder'" 2>/dev/null
```
Fallback:
```bash
find ~/Documents ~/Desktop ~/Downloads -maxdepth 3 -type d -name "FOLDER_NAME" 2>/dev/null
```

**Windows:**
```powershell
Get-ChildItem -Path "$env:USERPROFILE\Documents","$env:USERPROFILE\Desktop","$env:USERPROFILE\Downloads" -Directory -Recurse -Depth 3 -Filter "FOLDER_NAME" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
```

If multiple folders found, ask the user which one. If none found:

```
Couldn't find a folder named FOLDER_NAME. Create a folder with that name and put the audio files into it.
```

### Step 3 — Ask recording type

Before running, ask the user:

```
What are we transcribing?
1. In-depth interview (2 participants: interviewer + respondent)
2. Working meeting (several participants)
3. Presentation / lecture
4. Detect automatically
```

Map the answer to `--type` flag:
- 1 → `--type ux-interview`
- 2 → `--type meeting`
- 3 → `--type presentation`
- 4 → `--type auto` (default)

### Step 4 — Show summary and confirm

List audio files in the folder and get their durations:

```bash
ls /path/to/TICKET-123/
```

For each audio/video file get duration:
```bash
ffprobe -v quiet -print_format json -show_format "path/to/file" | python3 -c "import sys,json; print(json.load(sys.stdin)['format']['duration'])"
```

Check if any `*_transcript.txt` files already exist in the folder (in `transcripts/` subfolder or root).

Display to the user:

```
Found folder TICKET-123: /path/to/TICKET-123/
Audio files: 8 (2 already transcribed)
  • interview_01.m4a (47 min) — ✅ transcript exists
  • interview_02.m4a (32 min)
  • ...

Type: in-depth interview
Estimated processing time: ~X-Y min
Transcripts will appear in TICKET-123/transcripts/

Starting processing.
```

### Step 5 — Run transcription

**Flags:**
- `--skip-existing` — skip files that already have a `*_transcript.txt`. **Always use** for retry safety.
- `--raw` — skip LLM formatting, output raw transcript with Speaker 0/1 labels. ~2x faster.
- `--type TYPE` — recording type: `ux-interview`, `meeting`, `presentation`, or `auto` (default). Use the value from Step 3.

#### For short runs (≤3 files, all <45 min) in Cursor

Run directly:
```bash
python3 <SCRIPT_PATH> "/path/to/TICKET-123" --skip-existing --type ux-interview
```

Set `block_until_ms` proportionally: ~3 min per file minimum.

#### For long runs (>3 files or files >45 min) or Claude Code

**Always** run in background with log file:
```bash
nohup python3 <SCRIPT_PATH> "/path/to/TICKET-123" --skip-existing --type ux-interview > /tmp/ux-transcribe.log 2>&1 &
echo "PID: $!"
```

Monitor progress:
```bash
tail -20 /tmp/ux-transcribe.log
```

Poll the log every 60–90 seconds until you see "Done." in the output.

The script automatically:
- Finds all .m4a/.mp3/.wav files in the folder
- Falls back to .mp4 (extracts audio) if no audio files found
- **Pipelines** transcription and formatting: formats file N while transcribing file N+1
- Formats text chunks in parallel (3 at a time)
- Merges extra speakers when type is known (e.g. ux-interview → always 2 speakers)
- Runs QA validation on each transcript (JSON fragments, timestamp consistency, role consistency)
- Saves `*_transcript.txt` in `<folder>/transcripts/` subfolder
- Saves structured JSON in `<folder>/transcripts/json/`

#### Speed tips

| Scenario | Estimated time | Notes |
|---|---|---|
| 6 files × 60 min, full formatting | ~30-35 min | Pipeline saves ~30% vs old sequential |
| 6 files × 60 min, `--raw` | ~15-20 min | No LLM formatting, raw Speaker labels |
| Retry 2 failed files | ~8-10 min | `--skip-existing` skips 4 done files |

### Step 6 — Report results

When the script finishes (exit code 0), tell the user:

```
Done! Transcripts are in TICKET-123/transcripts/:
  ✅ interview_01_transcript.txt
  ✅ interview_02_transcript.txt
  ...

JSON versions: TICKET-123/transcripts/json/
```

If some files have QA warnings (the script prints `⚠ QA warnings`), mention them to the user.

If some files failed (exit code 1), show which files succeeded and which failed.
Suggest re-running with `--skip-existing` to retry only the failed ones.

If exit code is non-zero and ALL files failed, show the error from the log.

### Diagnostic report

The script automatically saves `_diagnostic.json` in `<folder>/transcripts/` after every run.
It contains environment info, per-file metrics (duration, retries, timing, errors), and an event log
(API retries, model fallbacks, JSON parse failures). If a user reports problems, ask them to send
this file — it has everything needed for debugging.

## Configuration

These values are hardcoded in `transcribe_folder.py` and match empirically tested Mistral free-tier limits:

| Parameter | Value | Meaning |
|---|---|---|
| Folder search | Spotlight → find fallback | Searches for folder by name |
| Output | `<folder>/transcripts/` | Transcript .txt + json/ + _diagnostic.json |
| MAX_CHUNK_DURATION_MINUTES | 40 | Chunk size for splitting |
| MINI_SPLIT_THRESHOLD_MINUTES | 45 | Split if audio > this |
| CHUNK_OVERLAP_SECONDS | 30 | Overlap between chunks |
| FORMATTER_CHUNK_CHARS | 10000 | Max chars per formatting request |
| FORMAT_CONCURRENCY | 3 | Parallel formatting requests |
| Formatting timeout | 600s | Per-request timeout for chat API |

Do NOT change these without testing — see [reference.md](reference.md) for details.

## Troubleshooting

### SSL certificate error on a corporate network

The script automatically detects corporate proxies with SSL inspection.
On macOS it exports system CA certificates and uses them for verification — no security is compromised.

If the script exits with a message about contacting IT, the system certificates did not help.
In that case, the user should get the corporate root CA certificate from IT and set:
```bash
export SSL_CERT_FILE=/path/to/corporate-ca.pem
```
