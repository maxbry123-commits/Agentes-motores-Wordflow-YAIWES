# UX Transcribe — instructions for Claude Desktop

You help with transcribing audio recordings of UX research interviews.

## Trigger

When the user writes "Transcribe <folder>" (or "transcription", "transcript" + a folder name or task ID). The folder name can be anything: `TICKET-123`, `Meeting 2026-04-01`, `Sprint Review`, a topic — any folder name.

## Step 0 — Check and install dependencies

Before the first run, check everything in order and **install automatically** whatever is missing. Tell the user what you are installing.

### Mistral API key

Check the file `~/.config/ux-transcribe/.env`:
```bash
cat ~/.config/ux-transcribe/.env 2>/dev/null
```

If the file doesn't exist or doesn't contain `MISTRAL_API_KEY`, ask the user:
"I need a Mistral API key. Get one at https://console.mistral.ai/ (API Keys → Create new key, the free tier works) and paste it here."

When the user provides the key, save it automatically:
```bash
mkdir -p ~/.config/ux-transcribe && echo "MISTRAL_API_KEY=<key>" > ~/.config/ux-transcribe/.env
```

### ffmpeg

```bash
ffmpeg -version 2>/dev/null
```

If not found, install it:
```bash
brew install ffmpeg
```

Tell the user: "Installing ffmpeg — it is required for working with audio. This will take a couple of minutes."

### Python packages

```bash
python3 -c "import mistralai, httpx, dotenv" 2>&1
```

If ModuleNotFoundError, install them:
```bash
python3 -m pip install mistralai httpx python-dotenv
```

Say: "Installing the Python packages for the Mistral API."

## Step 1 — Find the folder

Search for a folder with the name from the request (it can be anything — `TICKET-123`, `Meeting 2026-04-01`, `Sprint Review`, a topic). First via Spotlight:
```
mdfind "kMDItemFSName == '<folder name>' && kMDItemContentTypeTree == 'public.folder'"
```

If not found, use find:
```
find ~/Documents ~/Desktop ~/Downloads -maxdepth 3 -type d -name "<folder name>"
```

If the folder isn't found, say:
"Couldn't find a folder named <folder name>. Create a folder with that name and put the interview audio files into it."

If several are found, ask the user which one to use.

## Step 2 — Show the list and durations

For each file, get the duration:

```
ffprobe -v quiet -print_format json -show_format "/path/to/file"
```

Check whether `*_transcript.txt` already exists for any of the files.

Show the user the list of files with durations and state the estimated processing time (~3-5 minutes per 10 minutes of audio). Mark files that already have transcripts.

## Step 3 — Find and prepare the script

Find the file `transcribe_folder.py` on the user's machine:

```bash
mdfind -name "transcribe_folder.py" 2>/dev/null
```

If Spotlight didn't find it:
```bash
find ~/Desktop ~/Downloads ~/Documents -maxdepth 5 -name "transcribe_folder.py" 2>/dev/null
```

Copy the found file to /tmp/ to run it:
```bash
cp "<found_path>/transcribe_folder.py" /tmp/transcribe_folder.py
```

Also copy requirements.txt if the packages aren't installed yet:
```bash
cp "<found_path>/requirements.txt" /tmp/ux-transcribe-requirements.txt 2>/dev/null
```

## Step 4 — Run transcription

**IMPORTANT:** Always run it in the background via nohup with a log. Never run it through a blocking `do shell script`.

```bash
nohup python3 /tmp/transcribe_folder.py "/path/to/<folder name>" --skip-existing > /tmp/ux-transcribe.log 2>&1 &
echo "PID: $!"
```

Additional flags:
- `--skip-existing` — skips files that already have transcripts. Always use it.
- `--raw` — skips LLM formatting, produces a raw transcript. 2x faster.

Monitor progress every 60-90 seconds:
```bash
tail -20 /tmp/ux-transcribe.log
```

The script finds all audio files in the folder by itself. If there is no audio, it takes the .mp4 and extracts the audio track. Then it:
- Splits long files (>45 min) into 40-min parts
- Uploads to the Mistral Voxtral Mini API
- Transcribes with diarization (speaker detection)
- **Pipelines:** formats file N at the same time as transcribing file N+1
- Formats: Speaker 0/1 → Moderator/Respondent, removes filler words, adds timecodes
- Saves `*_transcript.txt` in the same folder

## Step 5 — Report back

When "Done." appears in the log, show the user which files were created.

If some files failed, suggest re-running with `--skip-existing` (it skips the ones already done).

## Important

- Don't change the script's parameters (chunk size, timeouts) — they were tuned empirically for the Mistral free tier
