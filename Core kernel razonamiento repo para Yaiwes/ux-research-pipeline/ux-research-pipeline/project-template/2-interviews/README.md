# 2-interviews

Drop interview recordings here.

## What to put here

- Audio or video files of the interviews (mp3 / mp4 / m4a / wav / mov / mkv).
- **Notes, debrief protocols, sample log, respondent screenshots** — into the `inscriptions/` subfolder. This isn't raw material for transcription, but it's important context for the analysis (see `inscriptions/README.md`).

If you only have transcripts (no audio), drop them here too as `.txt`. The agent will understand.

The filename can be anything. A handy convention: `R01.mp4`, `R02.mp4`, and so on, but it's not critical.

## What happens automatically

Once a file appears in this folder:
1. The agent transcribes it (alongside it — `<name>.txt` with timecodes and diarization).
2. It writes a short summary for the team (`<name>-summary.md`) — 3–5 takeaways + strong quotes. You can paste it into the team chat.
3. It codes it — the coded JSON lands in `.system/coded/<name>.json` (you don't need it, but it's there).
4. It updates the respondent map in `3-analysis/respondents/`.
5. It updates the theme maps in `3-analysis/themes/`.
6. It regenerates `3-analysis/matrix.xlsx` and `3-analysis/_index.md`.

In chat you'll get a short summary along the lines of: "Transcribed R03. Saturation: theme X is 80% closed, theme Y is just starting to show up. I'll propose a draft of findings after the next interview."

## What's stored here

- `.mp4`, `.mp3`, etc. — your original recordings. **They are not committed to git** (see `.gitignore`). Store them on your machine or in your own cloud storage.
- `.txt` — transcripts. Also not in git.
- `*-summary.md` — short team summaries. Also not in git (NDA).

Everything system-related (coded JSON, codebook) lives in the hidden `.system/` folder.
