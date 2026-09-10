# Golden set (for prompt regression — v2)

This folder is the scaffold for future regression testing of skill prompts. The regression itself is not implemented in v1 (see `docs/feedback-loop.md`), but the folder exists so the habit of collecting cases forms from the very start.

## Structure of a single case

```
tests/golden/case-<name>/
├── README.md              ← what matters to check in this case
├── input/
│   ├── transcript.json    ← coded transcript from ux-transcribe
│   ├── brief.md
│   └── questions-and-hypotheses.md
├── expected/
│   ├── coded.json         ← reference coding by a human reviewer
│   ├── findings.md        ← reference key findings
│   └── (optional) report.md
└── meta.yaml              ← metadata: source project, who coded it, date, which features to check
```

## What to put in a case

- **A transcript without PII.** Run it through anonymization: names → R0X, cities → "a major city", workplaces → "a company in industry Y".
- **Reference coding.** This is the **most expensive part.** Done by a human (a team can do it in an hour or two) — pick 3–5 segments with especially precise coding.
- **Expected findings.** For checking `17-key-findings` — what should show up in the findings.

## How to add a case

```bash
mkdir tests/golden/case-onboarding-2026q1
cd tests/golden/case-onboarding-2026q1
mkdir input expected
# copy the anonymized transcripts into input/
# write the reference findings in expected/findings.md
# fill in meta.yaml
```

## When to run the regression

In v1 — a manual run, when you edit a critical prompt:

```bash
# v2 — not implemented yet
./scripts/run-regression.sh tests/golden/case-onboarding-2026q1
# Compares the skill's fresh output against expected/ and shows the diff.
```

Metrics worth computing (a guide for the future):

- **Coverage** — what share of segments received non-empty coding.
- **Mapping accuracy** — share of segments mapped to the correct research question.
- **Verbatim quote validity** — share of quotes that exist in the transcript word for word.
- **False-positive rate in interpretive_notes** — share of interpretive notes that are "embellished" and not backed by the text.

## What we do NOT put in

- Raw audio (NDA + size).
- Respondents who are clearly identifiable (even after anonymization — if the profile is too unique).
- Stakeholder data.

## Minimal goal by the end of 2026 Q3

3–5 coded cases from real projects. Enough for the first automated regression in v2.
