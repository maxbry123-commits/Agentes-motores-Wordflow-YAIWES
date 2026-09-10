# shared/

Shared resources used across all skills and projects.

| File / folder | Purpose |
|---|---|
| `glossary.md` | Single glossary of terms: qualitative methodology, our team's vocabulary, technical terms. |
| `coding-vocabulary.md` | The team's canonical codebook — a living document. Used as a reference in `09-flat-coding` and `13-axial-coding` to unify synonyms. |
| `prompts/` | Shared prompt fragments reused across skills (for example, the instruction about verbatim quotes, or the shared NDA header). |
| `schemas/` | JSON Schema contracts for the key artifacts (`coded-segment`, `theme`, `category`, `paradigmatic-node`, `typology-type`, `finding`). Versioned, used for validation and to generate Pydantic classes. See `schemas/README.md`. |

Unlike `templates/` (which land in the project as files), `shared/` is a **reference** that skills point to.

**Production skill prompts** (what the agent applies to the data) live NOT here, but in the root `prompts/<skill-name>.md` folder. They are versioned separately from `SKILL.md` and calibrated against the results of pilot runs.
