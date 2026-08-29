# example-case (placeholder)

This is an empty example case — a scaffold that shows what the structure should look like.

When creating a real case:
- Copy this folder to `tests/golden/case-<your-name>/`.
- Fill in `input/`, `expected/`, `meta.yaml`.
- Leave this example (example-case) as a skeleton.

## Case readiness checklist

- [ ] `input/transcript.json` — valid against the `ux-transcribe` schema.
- [ ] `input/brief.md` — filled in.
- [ ] `input/questions-and-hypotheses.md` — filled in.
- [ ] `expected/coded.json` — coded by a human.
- [ ] `expected/findings.md` — reference findings.
- [ ] `meta.yaml` — metadata filled in.
- [ ] Anonymization done: PII removed, names → R0X, cities → generalized, workplaces → industry.
