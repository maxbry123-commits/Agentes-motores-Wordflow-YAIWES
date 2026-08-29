# Mistral API — Known Constraints (Free Tier)

These limits were discovered empirically. Do not change without testing.

## Transcription (audio/transcriptions endpoint)
- Model: `voxtral-mini-latest` → Voxtral Mini Transcribe V2
- Max reliable chunk: **~40 minutes**. Files >50 min cause "Server disconnected".
- Split threshold: 45 min, chunk size: 40 min
- Rate limit: ~1 req/s. A 3-second delay between chunks is required.
- Always upload via `files.upload()` + use `file_id` (not `file_url` or base64).
- Always delete uploaded files after transcription.
- Retry: 6 attempts, exponential backoff starting at 5s.

## Formatting (chat/completions endpoint)
- Model: `mistral-small-latest`, fallback: `mistral-medium-latest` (sticky: once fallback triggers, all subsequent calls use it)
- Max input per chunk: 10,000 chars. Reduced from 15k to improve JSON stability.
- Max total before splitting: 12,000 chars.
- Parallel formatting: 3 concurrent requests.
- Retry: 6 attempts, exponential backoff starting at 10s.
- Timeout: 600s per request (increased from 300s to handle long chunks).

## Audio splitting
- Uses pure ffmpeg subprocess calls (no pydub — works on any Python version).
- Split uses `-acodec copy` for speed (no re-encoding).
- Overlap of 30 seconds between chunks prevents lost content at boundaries.

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| "Server disconnected" during transcription | Audio chunk >50 min | Lower MAX_CHUNK_DURATION_MINUTES |
| "Server disconnected" during formatting | Chunk too large or API instability | Re-run with `--skip-existing` |
| HTTP 429 | Rate limit hit | Increase INTER_CHUNK_DELAY |
| "MISTRAL_API_KEY not found" | Key not configured | Create ~/.config/ux-transcribe/.env |
| "ffprobe not found" | ffmpeg not installed | `brew install ffmpeg` / `winget install ffmpeg` |
| Formatting garbled | Chunk too large for chat | Lower FORMATTER_CHUNK_CHARS |
| Some files failed, some OK | API instability | Re-run with `--skip-existing` flag |
| Need debug info | Any issue | Send `_diagnostic.json` from the `transcripts/` folder |

## First-time setup

### macOS

```bash
brew install ffmpeg
pip3 install mistralai httpx python-dotenv
mkdir -p ~/.config/ux-transcribe
echo "MISTRAL_API_KEY=your-key-here" > ~/.config/ux-transcribe/.env
```

### Windows (PowerShell)

```powershell
winget install ffmpeg
pip install mistralai httpx python-dotenv
New-Item -ItemType Directory -Force -Path "$env:APPDATA\ux-transcribe"
Set-Content "$env:APPDATA\ux-transcribe\.env" "MISTRAL_API_KEY=your-key-here"
```
