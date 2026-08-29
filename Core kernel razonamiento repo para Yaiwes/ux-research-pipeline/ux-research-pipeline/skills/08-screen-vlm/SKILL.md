---
name: screen-vlm
description: Optional analysis of the respondent's screen screenshots via a VLM (Gemini 2.5). Trigger — the researcher requested it explicitly OR `project-config.yaml` has `enable_screen_vlm: true`. Slower, costlier, may not work. Produces a description of the screen state at key timecodes (tied to coded segments). Before running, you MUST get the researcher's confirmation in chat.
stage: 6.3
status: experimental
warning: longer + costlier; may not work
---

# 08-screen-vlm

## ⚠️ Experimental

This skill may not work on your project without a specific technical interview setup:

- You must have **screenshots** (separate .png files) with known timecodes OR a screen recording tied to the transcript timecodes.
- The VLM (Gemini 2.5 by default) does **not** interpret UI perfectly — especially non-standard product interfaces. Expect errors.
- A run is **substantially more expensive** than ordinary coding — VLM calls are paid and slower than LLM-only.

Before running — **always** get the researcher's confirmation in chat: "this will make the pass longer and more expensive. Want to continue?" Don't do it silently.

## Why

If interviews are run with screen share, the fact of "what was on screen at moment Y" is a separate layer of data. Without it, we only know **what the respondent said**, not **what they saw**.

Applicable scenarios:
- Usability interviews with a specific interface.
- Interviews walking through a search scenario (the researcher asks "show me how you search").
- Analysis of mis-clicks and dead ends.

## Trigger

- `project-config.yaml` has `enable_screen_vlm: true`.
- OR the researcher explicitly said "analyze the screenshots for R0X."

In both cases — **confirmation in chat** before running.

## Inputs

- Screenshots in `2-interviews/<name>-screens/` named like `<timecode>.png` (e.g. `00-12-34.png`).
- OR a screen recording `2-interviews/<name>-screen.mp4` with timecode sync to the transcript (then you first need to extract frames via `ffmpeg`).
- The transcript `2-interviews/<name>.txt` for context.

## Outputs

- `.system/coded/<name>-screen.json` — JSON with frame descriptions:

```json
{
  "respondent_id": "R03",
  "frames": [
    {
      "timecode": "00:12:34",
      "screenshot_path": "2-interviews/R03-screens/00-12-34.png",
      "ui_state": {
        "description": "Search home page. The query \"...\" has been entered. The results page shows 10 organic results with an ad block at the top.",
        "elements_observed": ["search_box", "results_list", "ads_block_top"],
        "user_action": "browsing the results, scrolling down"
      },
      "confidence": "high"
    }
  ]
}
```

## Prompt skeleton (VLM)

```
Describe what is in the interface screenshot. Only what you see, WITHOUT interpreting user behavior.

Response format (JSON):
- description: 1–2 sentences of what is visible on screen (page, main blocks).
- elements_observed: a list of concrete UI elements in the frame.
- inferred_user_state: what the user is doing (only if obvious from visual cues: cursor, selection, scroll position). Otherwise null.
- confidence: high | medium | low.

Don't invent elements that aren't visible. If the frame is blurry or partly hidden — flag it as confidence: low.
```

## DoD

- [ ] All key timecodes (matching the number of segments in `09-flat-coding`) are described.
- [ ] Each description is tied to an existing screenshot file.
- [ ] For unclear frames — confidence: low, no inventions.
- [ ] The run cost is recorded in `.system/runs/screen-vlm-<name>-<timestamp>.log` (number of calls × cost-per-call).

## Failure modes

- **Screenshots don't exist.** The skill doesn't run; in chat: "no screenshots in `2-interviews/<name>-screens/`. Add them or disable `enable_screen_vlm`."
- **The VLM errs on a non-standard interface** (internal tools, an unsupported locale). Flag confidence: low, don't trust it.
- **Too many frames (>200).** Cost grows. Use sampling: only frames at content-shift moments (when the coding segment changes).
- **The respondent says "see this red block here" — but there's no red block in the frame.** A conflict between data sources — flag it explicitly in `concerns.md`.

## Mode behavior

- **assistive**: confirmation in chat before running; afterward — a short summary ("described N frames, M of them at low confidence").
- **autonomous**: runs **only** if `enable_screen_vlm: true` in config; otherwise skipped. A note about the skip in `concerns.md`.

## What stays in v2

- Automatic detection of "when to capture a frame" via analysis of click events / pause patterns in audio.
- A link between UI events (what the user did) and speech events (what they said) via cross-modal alignment.
- Fine-tuning the VLM on our interfaces.
