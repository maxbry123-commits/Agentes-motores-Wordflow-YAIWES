# Transcribe

Transcription of audio recordings (interviews, meetings, any recordings) via the Mistral Voxtral API.
Automatically detects the recording type and participant roles.

## Trigger

When the user writes "Transcribe" (or "transcription", "transcript") + a folder or task name:

## Step 0 — Check and install dependencies

Before the first run, check everything in order and **install automatically** whatever is missing. Tell the user what you are installing.

### System certificates (corporate network)

Export the system CA certificates — this is needed to work behind a corporate proxy:
```bash
security find-certificate -a -p /Library/Keychains/System.keychain > /tmp/ux-transcribe-ca-bundle.pem 2>/dev/null
security find-certificate -a -p /System/Library/Keychains/SystemRootCertificates.keychain >> /tmp/ux-transcribe-ca-bundle.pem 2>/dev/null
```

Set the variable for the current session:
```bash
export SSL_CERT_FILE=/tmp/ux-transcribe-ca-bundle.pem
export NODE_EXTRA_CA_CERTS=/tmp/ux-transcribe-ca-bundle.pem
```

This is a safe operation — certificates are not disabled, they are augmented with the system ones.

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

Tell the user: "Installing ffmpeg — it is required for working with audio."

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

Extract the folder name from the message (for example `TICKET-123`, `Meeting 2026-04-01`, `Sprint Review`).
If the user gives a full path, use it directly.

Search for the folder via Spotlight:
```bash
mdfind "kMDItemFSName == 'NAME' && kMDItemContentTypeTree == 'public.folder'" 2>/dev/null
```

If not found, use find:
```bash
find ~/Documents ~/Desktop ~/Downloads -maxdepth 3 -type d -name "NAME" 2>/dev/null
```

If the folder isn't found: "Couldn't find a folder named NAME. Create a folder with that name and put the audio files into it."

If several are found, ask the user which one to use.

## Step 2 — Ask the recording type

Ask the user before running:
"What are we transcribing? In-depth interview / Working meetings / Presentation / Detect automatically"

Map the answer to the `--type` flag:
- In-depth interview → `--type ux-interview`
- Working meetings → `--type meeting`
- Presentation → `--type presentation`
- Automatically → `--type auto`

## Step 3 — Show the list and durations

For each file, get the duration:
```bash
ffprobe -v quiet -print_format json -show_format "/path/to/file"
```

Check whether `*_transcript.txt` already exists for any of the files (in the `transcripts/` subfolder or in the folder root).

Show the user the list of files with durations and state the estimated processing time (~3-5 minutes per 10 minutes of audio). Mark files that already have transcripts.

## Step 4 — Run transcription

Script: `scripts/transcribe_folder.py` relative to this file.

Run it in the background with a log:
```bash
nohup python3 scripts/transcribe_folder.py "/path/to/TICKET-XXX" --skip-existing --type ux-interview > /tmp/ux-transcribe.log 2>&1 &
echo "PID: $!"
```

Flags:
- `--skip-existing` — skips files that already have transcripts. Always use it.
- `--type TYPE` — recording type from Step 2. Always use it.
- `--raw` — skips LLM formatting, produces a raw transcript. 2x faster.

Monitor progress every 60-90 seconds:
```bash
tail -20 /tmp/ux-transcribe.log
```

## Step 5 — Report back

When "Done." appears in the log, show the user which files were created.
Transcripts are saved to `<folder>/transcripts/`, JSON versions to `<folder>/transcripts/json/`.

The script automatically saves `_diagnostic.json` to `<folder>/transcripts/`. This file contains the environment, timings, errors, and retries — it is needed for debugging. If something goes wrong, ask the user to send this file to the developer.

If the script produced QA warnings (`⚠ QA warnings`), tell the user.
If some files failed, suggest re-running with `--skip-existing` (it skips the ones already done).

## Important

- Don't change the script's parameters (chunk size, timeouts) — they were tuned empirically for the Mistral free tier
