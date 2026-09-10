---
name: link-detector
description: Finds links between segments (within-interview and cross-interview): confirmations, contradictions, recurrences. Trigger — after 3+ coded interviews. Takes all segments with global summaries and returns a structured list of links. Links are added to respondent and theme maps as wikilinks. The main risk is random "contradictions," so every link requires justification.
stage: 8.2
status: stretch
---

# 12-link-detector

## Why

Flat coding (`09-flat-coding`) works per-segment and doesn't see links. Cross-segment work is a separate analysis step.

Link types:
- **Confirmation** within-interview: the respondent says the same thing in different ways in different places.
- **Contradiction** within-interview: the respondent says one thing, then the opposite.
- **Recurrence** cross-interview: different respondents mention the same phenomenon.
- **Divergence** cross-interview: different respondents give opposite assessments/experiences on the same theme.

## Trigger

After 3+ coded interviews. Earlier there's not enough data for cross-interview work.

Can be re-run after each subsequent interview so new links are taken into account.

## Inputs

- All `.system/coded/*.json` (coded transcripts).
- Global summaries from the `transcript-coding` global pass (inside the JSON).

## Outputs

- `.system/links.json` — a structured list of links:

```json
{
  "links": [
    {
      "type": "contradiction_within",
      "respondent": "R03",
      "source_segment": "R03:seg-12",
      "target_segments": ["R03:seg-25"],
      "note": "In seg-12 the respondent says onboarding was easy; in seg-25 that they struggled for a week.",
      "confidence": "high"
    },
    {
      "type": "convergence_cross",
      "respondents": ["R01", "R03", "R07"],
      "source_segments": ["R01:seg-15", "R03:seg-08", "R07:seg-22"],
      "note": "All three describe the same usage pattern: open → close with no actions.",
      "confidence": "high"
    },
    {
      "type": "divergence_cross",
      "respondents": ["R04", "R08"],
      "source_segments": ["R04:seg-30", "R08:seg-11"],
      "note": "R04 — feature X helps; R08 — feature X gets in the way. Possibly a segment effect.",
      "confidence": "medium"
    }
  ]
}
```

- Updates in respondent and theme cards (3-analysis/respondents/R03.md → the "Links to other interviews" section gets new wikilinks).

## Prompt skeleton

```
You are looking for links between interview segments. Be careful — links must be substantive, not "both said the word X."

You are given:
1. A global summary of each interview.
2. Segments with quotes and codes on theme {{T}}.

Task:
- Find confirmations (within or cross): when several places say the same thing substantively.
- Find within contradictions (one respondent contradicts themselves).
- Find cross divergences (different respondents say different things).
- For each link, specify:
  - type (confirmation / contradiction / convergence / divergence);
  - source (segment_id);
  - target (segment_id or list);
  - a one-line justification;
  - confidence high/medium/low.

Don't:
- create links on superficial word matches.
- create "links" of the "themes are similar" kind — that's the job of axial-coding.
- create too many links: take only the substantive ones. 1–3 per pair of interviews is normal.
```

## DoD

- [ ] Every link has a type, source, target, and justification.
- [ ] Low-confidence links are flagged explicitly.
- [ ] Respondent cards are updated with wikilinks.
- [ ] All cross-interview links have a list of respondents (not just a pair).

## Failure modes

- **Too many links (>20 across 5 interviews).** You're most likely catching superficial matches. Trim to the substantive ones.
- **"Contradictions" that are actually clarifications.** The respondent said "I don't use it" at the start, then "but sometimes I check in on Wednesdays" — that's a clarification, not a contradiction. Don't mark it.
- **Convergence = one segment in the sample.** If everyone who "agrees" is from one segment, that's not convergence but a segment trait. Flag it.
- **No contradictions found at all.** Suspicious — data usually has plenty of contradictions. If there are none, double-check whether you're grouping too coarsely.

## Mode behavior

- **assistive**: after the pass, a summary in chat: "found N links. 3 interesting contradictions in R03." No pause (this is a working step).
- **autonomous**: write and move on.
