# Confidentiality

This pipeline works with confidential research material. Here's what's allowed, what isn't, and where the line is.

## What counts as confidential

- **Interview recordings**: audio, video, screenshots of the respondent's screen.
- **Transcripts**: text with timecodes and speaker markers.
- **Coded transcripts**: JSON with quotes.
- **Interview guides and screeners**: until the project is closed, these are confidential too.
- **Recruitment data**: respondent names, phone numbers, emails, profiles.
- **Internal product metrics mentioned in the material**.

## What you must never do

- **Upload material to public services** without an explicit yes from the researcher: ChatGPT (web), Claude.ai (web), Gemini.app, Perplexity, and so on. Using the APIs of these services is fine (traffic runs under contractual agreements), but not the consumer web interfaces.
- **Put material in public repositories** (public GitHub, public GitLab). Private repositories are fine.
- **Quote respondents in shared discussions** (a shared chat, an article, a conference talk) without anonymization.
- **Reproduce PII** in output artifacts: names, phone numbers, emails, home addresses, recognizable biographical details.

## What is allowed

- Use LLM APIs (OpenAI, Anthropic, Gemini). Still, **keep the source material on your own machine or in private storage**, not on arbitrary third-party clouds.
- Share output artifacts (reports, presentations, links to the team wiki) internally with people working on the same product. With external partners — only after sign-off from the stakeholder.
- Use aggregated demographics: "woman, 34, urban, ~6 months of experience with the product." Avoid recognizable combinations (name + city + rare occupation).

## What `.gitignore` hides

See the repository's `.gitignore`. The following are never committed:

- All audio and video in `0-input/` and `2-interviews/`.
- All `.txt` transcripts.
- All `.json` coded transcripts.
- `*-summary.md` (confidentiality-sensitive).
- `.system/coded/`, `.system/runs/`.
- `.env` (API keys).

Prompt snapshots (`.system/prompts-versions/`) and the codebook (`.system/codebook/`) are kept (needed for debugging and retrospectives). They must contain no respondent-specific PII.

## How to check that nothing leaked

Before publishing a report to the team wiki or a presentation:

1. **PII scan.** Run `grep -ri "@" 4-output/` (emails), `grep -rE "\+7|8\(|9[0-9]{9}" 4-output/` (phone numbers), and scan for recognizable names.
2. **Check for "too specific."** "Maria, 34, from a mid-sized city, works as a logistics manager at a small firm" is already identifiable. Loosen the details.
3. **Quotes stay verbatim**, but the context around a quote must not reveal the respondent's identity.

## What to do with recordings after the project

After closing the project:
- Recordings (audio/video) should be deleted or moved to long-term storage with access restricted to the team (private storage with ACLs).
- Transcripts — keep them in the project (they may be useful for future desk research).
- Coded transcripts — keep them in `.system/coded/`.

For archival purposes (v2 `desk-research-index`): transcripts are de-identified and indexed. This is a separate process, not done automatically.

## If something does leak

1. Don't panic, but don't sit on it.
2. Remove it from the public location (if possible — revert the commit, request deletion from the third-party service).
3. Notify your lead and your information security team.
4. Record it in `feedback.md` under the `[security]` category — what happened and how to avoid it in the future. This is fuel for the pipeline.
