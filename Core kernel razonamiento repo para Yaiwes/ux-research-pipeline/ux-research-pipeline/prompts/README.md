# prompts/

Production prompts for the skills. This is what the agent actually applies to project data; a skill's SKILL.md describes the contract (inputs, outputs, rules), while the prompt holds the concrete execution instructions.

## Why a separate folder instead of keeping prompts inside SKILL.md

- **Versioning.** A prompt gets calibrated more often than a skill's contract changes. A separate file means a separate commit history.
- **A/B testing.** You can keep v0.2 and v0.3 side by side and compare them on a golden case.
- **Calibration in a single edit.** Every prompt opens with a "Calibration" section — a YAML block with thresholds. Change it there and the behavior changes; you don't need to rewrite the body.
- **Worker prompts live next to manager prompts.** If a skill uses subagents, the `## Worker prompt` and `## Judge prompt` sections sit in the same file.

## Which prompts exist

| Prompt | Skill | What it does |
|---|---|---|
| `flat-coding.md` | `09-flat-coding` | Flat coding of one interview. Manager + worker + judge. |
| `axial-coding.md` | `13-axial-coding` | Grouping codes into themes and categories, finding axes. |
| `paradigmatic-model.md` | `14-paradigmatic-model` | Building the paradigm model (causal → context → action → consequence). |
| `typology.md` | `16-typology` | Behavioral typology with an anti-pattern check. Per-type workers. |
| `key-findings.md` | `17-key-findings` | 5–7 key findings with a verbatim check. Per-finding workers. |
| `report-draft.md` | `18-report-draft` | Report draft in `4-output/report.md`. |
| `narrative-adapt.md` | `18.5-narrative-adapt` | Adapts the academic report into clear stakeholder language (jargon/plain-language pass). |

## Versioning

- v0.X — pre-production, calibrated on pilots.
- v1.0 — once a prompt has gone through 3+ real projects without major edits.
- The version is recorded in the prompt header (`**Prompt version:** v0.2`).

## Structure of each prompt

1. **Header** — which skill, version, which schemas are used.
2. **Calibration** — a YAML block of thresholds and flags at the top. Changed in a single edit.
3. **System instruction** — who the agent is, the hard rules.
4. **Input** — which files the agent reads.
5. **Algorithm** — step-by-step logic.
6. **Output** — artifact structure (Markdown templates + a link to the JSON schema).
7. **DoD** — definition of done.
8. **Failure modes** — common mistakes.
9. **Worker prompts** (if subagents are used) — what each worker and the judge does.
10. **Mode behavior** — assistive vs. autonomous.
