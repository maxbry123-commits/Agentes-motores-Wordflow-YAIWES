# Pipeline retro — {{quarter/period}}

> A regular review: what needs improvement in the system itself. Not a retro on a specific project, but on the agent and skills on average.

## Period

{{from YYYY-MM-DD to YYYY-MM-DD}}.

## How many projects went through the system

| Project | Mode | Skills that "hurt" | Status |
|---|---|---|---|
| ... | assistive/autonomous | list of skill numbers with issues | done / in progress |

## Top 5 problems from `feedback.md`

> Collected from `feedback.md` across all projects in the period.

| Category | Times mentioned | In which skills | Fix priority |
|---|---|---|---|
| `hallucination` | {{N}} | 09-flat-coding, 17-key-findings | high |
| `inaccuracy` | {{M}} | 13-axial-coding | medium |
| ... | | | |

## Specific prompt edits

### Skill `<name>`
- **Symptom**: {{what was observed}}.
- **Hypothesized cause**: {{what in the prompt produces this behavior}}.
- **Edit**: {{new wording}}.
- **Expected effect**: {{what will change}}.
- **Regression check**: run on golden case {{ID}} — improvement / regression / no change.
- **PR**: {{link}}.

(several such blocks)

## Structural pipeline changes

> If the quarter showed that not just prompt edits are needed, but changes to the skill architecture, workflows, or the project file structure.

- {{proposal}}: {{rationale}}.
- {{proposal}}: {{rationale}}.

## What we are NOT doing (although it was proposed)

- {{idea}} — {{why we're deferring it}}.

## Pipeline metrics

- Average time from project kickoff to the first report draft: {{N days}}.
- Share of quotes that required manual correction: {{%}}.
- Share of recommendations the researcher rewrote entirely: {{%}}.
- Cost per project: {{$}}, LLM tokens + Voxtral.

## Actions

- [ ] {{action}} — who — by when.
- [ ] {{action}} — who — by when.

## Deferred to v2

(copied from `plugin.json.v2_roadmap` + anything new that came up)
