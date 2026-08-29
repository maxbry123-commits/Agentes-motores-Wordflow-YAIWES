# Project feedback

> What didn't work in the assistant and the pipeline. Material for a regular retro — to fix prompts, skills, and flows. Write it down as soon as you notice it; otherwise you'll forget.

Free-form, but if you can, stick to these categories so it's easier to aggregate later:

- `[hallucination]` — the agent made up a fact, quote, or number.
- `[inaccuracy]` — didn't make it up, but interpreted it inaccurately.
- `[style]` — stylistically poor (tone, structure, length).
- `[insufficient-context]` — failed to account for something that was in the materials.
- `[schema]` — output format doesn't match expectations (not Obsidian-friendly, no timecode, etc.).
- `[ux]` — the conversation with the agent was awkward, unnecessary questions / missed pauses.
- `[other]`

## Example

```
[hallucination] in the key findings a quote attributed to R04 appeared that isn't in her transcript — looks like the agent mixed it up with R07. Fixed by hand; the verbatim check didn't catch it.

[ux] after the second interview the agent asked twice whether to do a quick summary — it should have just done it right away.

[insufficient-context] in `thoughts.md` I noted that the stakeholder ultimately changed their mind about the metric — that wasn't reflected in the recommendations.
```

---

<!-- write freely -->
