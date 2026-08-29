# Obsidian conventions

How the `3-analysis/` vault of each project is organized, how the agent writes into it, and which templates it uses.

## What's inside the vault

```
3-analysis/
├── _index.md               ← the project dashboard (the agent keeps it updated)
├── findings.md             ← a summary of the key findings
├── typology.md             ← a summary of the typology
├── model.canvas            ← the paradigm model (Obsidian canvas)
├── matrix.xlsx             ← respondent × theme, saturation, hypotheses
├── respondents/            ← one card per interview
│   ├── _template-respondent.md
│   ├── R01.md
│   └── ...
├── themes/                 ← one card per theme
│   ├── _template-topic.md
│   └── ...
├── findings/               ← one file per finding
│   ├── _template-finding.md
│   └── ...
└── types/                  ← one file per type in the typology
    ├── _template-type.md
    └── ...
```

## Formatting rules

### Frontmatter properties

Every card starts with YAML frontmatter. This gives you:
- sorting and filtering in Obsidian (Settings → Files & links → Properties),
- queries via Dataview (if the plugin is installed),
- stable, machine-readable metadata for the agent.

Field templates live in the `_template-*.md` files in each subfolder.

### Wikilinks

All links between entities go through `[[wikilinks]]`, not Markdown links. Example:

```markdown
- [[respondents/R03]] aligns on the theme [[themes/onboarding]] with [[respondents/R07]].
```

This gives you the graph view out of the box.

### Quotes

A verbatim quote always looks like:

```markdown
> "{{verbatim}}" — [[respondents/R01]] `[mm:ss]`
>
> Context: what was being discussed.
```

Never:
- without quotation marks (if it's a paraphrase — no `>` block).
- without a timecode.
- without a link to the respondent.
- spliced together from different moments of the same interview.

### Tags

Use sparingly. Good candidates:
- `#draft` — the artifact isn't finished yet.
- `#disconfirm` — a strong counter-example to the main emerging story.
- `#followup` — needs more digging.
- `#kept-for-archive` — kept only for the record, not used in the current findings.

Don't use:
- `#important`, `#interesting` — useless as a filter.
- `#respondent_03` — that already exists as `[[R03]]`.

## What goes where

| Artifact | Where |
|---|---|
| Quote + context | the respondent card + duplicated into the theme card |
| A hypothesis that emerged from an interview | the respondent card (as an observation) + `findings.md` (once it takes shape) |
| A link between two interviews | both respondent cards, via a wikilink |
| A behavioral marker of a type | the type card in `types/` |
| A fragment of the model "condition → action → consequence" | as a node in `model.canvas`, linked to the quotes |

## What NOT to write into the vault

- Raw JSON — it lives in `.system/coded/`. If you need quotes, make a human-readable summary.
- Prompt logs — in `.system/runs/`.
- The final report — in `4-output/report.md`. That's a separate document, not part of the Obsidian vault (even though it's also `.md`).

## The "incremental update" principle

After each newly coded interview, the agent:

1. Creates `respondents/R0X.md`.
2. Updates `themes/<theme>.md`: adds the new quotes from this respondent, recomputes saturation in the frontmatter.
3. Regenerates `matrix.xlsx`.
4. Updates `_index.md`: the new respondent appears in the list, the saturation summary is refreshed.
5. If the interview count crossed the `draft_findings_after_n_interviews` threshold (see `project-config.yaml`) — creates draft `findings/F0X.md`.

## Obsidian plugins

The vault works in vanilla Obsidian with no community plugins. If you want more:

- **Dataview** — queries over frontmatter properties: `LIST FROM "respondents" WHERE saturation > 0.5`. Useful for free-form navigation.
- **Excalidraw** — draw diagrams directly in Obsidian (CJM, strategy maps). Not needed for the basic flow.
- **Templater** — advanced templates with scripted inserts. The agent does fine without it.

Install via Settings → Community plugins. This is local to you, not to the whole team.

## What to check before the final

Before assembling the report (`4-output/`):

1. Every finding has at least N respondents in its evidence (see `skills/17-key-findings/SKILL.md`).
2. Every quote has a timecode.
3. The paradigm model (`model.canvas`) is built and every node is linked to themes or quotes.
4. The typology (if appropriate for the project) passes the anti-pattern check (see the `_template-type.md` template).
5. `_index.md` is up to date.
