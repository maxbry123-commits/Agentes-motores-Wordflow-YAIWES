# Transcribe — a skill for automatic audio transcription

A skill for **Cursor** and **Claude Code**. Transcribes audio recordings via Mistral AI — interviews, working meetings, presentations, any recordings.

You create a folder, name it, drop the audio files in, and tell Claude: "Transcribe TICKET-123" or "Transcribe Meeting 2026-04-01". A few minutes later, ready transcripts appear in the folder. The skill automatically detects the recording type, the number of participants, and assigns roles.

---

## Before installing

Get a Mistral API key (the same for both options):

1. Open https://console.mistral.ai/
2. Sign up (or log in)
3. In the left menu: **API Keys → Create new key**
4. Copy the key (it is shown only once)

The free tier works; you don't need the paid plan.

---

## Option A: Cursor

**Step 1.** Unpack the archive. Put the `ux-transcribe` folder into `.cursor/skills/` in your home directory.

How to find it:
- **macOS:** Finder → **Cmd+Shift+G** → type `~/.cursor/skills` → Enter
- **Windows:** File Explorer → in the address bar type `%USERPROFILE%\.cursor\skills` → Enter

If there is no `skills` folder, create it. Drag `ux-transcribe` into it.

**Step 2.** Open Cursor and type in the chat: **Transcribe TICKET-123**

That's it. Claude will ask for the key, save it, install ffmpeg and the Python packages, and start transcription.

---

## Option B: Claude Code

**Step 1.** Unpack the archive wherever is convenient (for example, on the desktop).

**Step 2.** Open a terminal, go to the `ux-transcribe` folder, and launch Claude Code:

```bash
cd ~/Desktop/ux-transcribe
claude
```

**Step 3.** Type: **Transcribe TICKET-123**

That's it. Claude will read the instructions from `CLAUDE.md`, ask for the key, save it, install ffmpeg and the Python packages, and start transcription.

---

## Usage

1. Create a folder with any name — `TICKET-123`, `Meeting 2026-04-01`, `Sprint Review`
2. Put audio files (`.m4a`, `.mp3`, `.wav`) or video (`.mp4`) into it
3. Type in the chat:

```
Transcribe TICKET-123
```

or

```
Transcribe Meeting 2026-04-01
```

---

## What you get

A `transcripts/` subfolder appears in the folder with the ready files:

```
TICKET-123/
├── interview_anna.m4a
├── interview_boris.m4a
└── transcripts/
    ├── interview_anna_transcript.txt
    ├── interview_boris_transcript.txt
    ├── _diagnostic.json
    └── json/
        ├── interview_anna.json
        └── interview_boris.json
```

Each transcript contains:
- Participant roles (detected automatically or set by recording type)
- Start and end timecodes for each turn
- Cleaned-up text (no "uh", "umm", or meaningless repetitions)

The JSON versions contain structured data for further analysis.

`_diagnostic.json` is a run report: environment, timings, errors, retries. If something goes wrong, send this file to the developer.

---

## Processing speed

- ~3–5 minutes per 30 minutes of audio
- Files longer than 45 minutes are split into parts automatically
- 8 files of 60 minutes each ≈ 40–50 minutes of processing

---

## If some files weren't processed

Just say it again:

```
Transcribe TICKET-123
```

The already-finished transcripts will be skipped; only the remaining ones will be processed.

---

## Checking the results

After transcription, run the validator — it checks all files for common errors:

```bash
python3 scripts/validate_transcripts.py /path/to/TICKET-123
```

The validator checks:
- No JSON junk in the text files
- Timecodes are in order, with no large gaps (>5 min)
- Timecode format `[start – end]`
- Participant roles are in place (not raw `Speaker 0`)
- JSON files are valid and contain the required fields

If everything is fine, you'll see `All N checks passed.` If there are problems, you'll see the details for each file.

---

## Corporate network

If you work behind a corporate proxy with SSL inspection, the script automatically exports the macOS system certificates and uses them. No manual steps needed.

**For Claude Code** — add one line to `~/.zshrc` (once):

```bash
echo 'export NODE_EXTRA_CA_CERTS=/tmp/ux-transcribe-ca-bundle.pem' >> ~/.zshrc
```

Before the first Claude Code run, execute:

```bash
security find-certificate -a -p /Library/Keychains/System.keychain > /tmp/ux-transcribe-ca-bundle.pem
security find-certificate -a -p /System/Library/Keychains/SystemRootCertificates.keychain >> /tmp/ux-transcribe-ca-bundle.pem
```

**For Claude Desktop** — in the MCP config (Settings → Developer → Edit Config) add `env` to each server:

```json
"env": {
  "NODE_EXTRA_CA_CERTS": "/tmp/ux-transcribe-ca-bundle.pem"
}
```

And run the same two `security find-certificate` commands above to create the certificate file.
