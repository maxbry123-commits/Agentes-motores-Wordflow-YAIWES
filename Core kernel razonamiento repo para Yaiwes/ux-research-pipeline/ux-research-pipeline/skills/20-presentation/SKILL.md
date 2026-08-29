---
name: presentation
description: A shim over a .pptx presentation export step. Assembles a presentation from `4-output/report.md` and the key findings. Merges 11.1 (key messages) + 11.2 (assembly). Structure — 1–2 key slides up top → findings with evidence → recommendations → appendices. Trigger — the researcher says "make a presentation."
stage: 11.1+11.2
status: external (shim)
upstream_skill: pptx-export
---

# 20-presentation (shim)

## What it does

A thin wrapper over an external .pptx presentation export step. Does not duplicate its logic.

## Trigger — NEVER AUTOMATICALLY

The researcher **explicitly** said "make a presentation" / "put it in pptx" / "I need slides for a meeting."

In autonomous mode it is **also not invoked automatically** — even if the researcher said "go all the way to the end." A presentation is a final artifact that needs its own separate "yes."

A presentation is a **different contract** from "take the analysis through to a report." Don't conflate them: "I need a presentation" is not the same ask as "finish the analysis."

If you're in autonomous and have finished `19-format` — stop and write explicitly in `4-output/handoff.md`: "No presentation was made; run `20-presentation` as a separate command if you need one." Don't run it yourself.

## Behavior

1. Check that `4-output/report.md` and `3-analysis/findings/` exist. If not — say: "I need the report; shall I run `18-report-draft`?".

2. **Extract the key messages** (part 11.1):
   - 1–2 main statements that answer the business question.
   - These go on the first 1–2 slides ("the key message"). The rest is the supporting evidence.

3. Pass to the .pptx export step:
   - `report_path`: `4-output/report.md`.
   - `findings_path`: `3-analysis/findings/`.
   - `key_messages`: the list from step 2.
   - `template`: `default`.
   - `audience`: `internal` (default) or `external` (if the researcher specified).

4. Get `4-output/presentation.pptx`.

## Presentation structure ("pyramid" pattern)

1. **Slide 1**: a single headline statement that answers the business question. No bullets.
2. **Slide 2** (optional): the second statement (if there are two key messages).
3. **Slides 3–5**: study context (brief, method, sample).
4. **Slides 6–N**: findings. One slide — one finding, with quotes and evidence.
5. **Slides N+1 — N+M**: recommendations, one per slide.
6. **Appendix slides**: typology, paradigm model, methodological caveats.

## Inputs

- `4-output/report.md`.
- `3-analysis/findings/F0X.md`.
- `3-analysis/typology.md` (if any).
- `3-analysis/model.canvas` or `3-analysis/model.md` (for the appendix slides).

## Outputs

- `4-output/presentation.pptx`.

## DoD

- [ ] The first 1–2 slides are the key messages.
- [ ] Each finding is its own slide with quotes.
- [ ] Quotes are verbatim, with a timecode (or at least a respondent ID).
- [ ] Each recommendation is its own slide.
- [ ] A consistent presentation style is applied.

## Failure modes

- **Slides overloaded with text.** A typical error. One slide — one statement + minimal evidence.
- **Quotes without context.** "It's awful" — with no sense of what about, the quote is useless. Add context in the caption.
- **Recommendations with no grounding.** The slide should make the link to a finding visible.
- **Distracting illustrations.** If an icon/image doesn't help convey the meaning — drop it.

## What it does NOT do

- Does not make factual edits to the report — only repackaging.
- Does not publish the presentation (sending it out via email or file storage is a separate step for the researcher).
