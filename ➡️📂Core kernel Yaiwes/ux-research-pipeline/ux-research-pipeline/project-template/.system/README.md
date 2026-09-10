# .system/ — the agent's working folder

Don't touch by hand.

This is where the files live that the agent needs in order to remember what has been done:

- `agent-notes.md` — the agent's working notebook: handoff to next session (at the top), current state, decisions log, open methodological questions. The agent reads it first when starting a new chat session on the project (see `AGENT.md` §13–14). Feel free to peek if you're curious — there's nothing secret in there — but you don't need to change it.
- `coded/` — coded transcripts in JSON following the `coded-interview.v1` schema (one file per interview).
- `codebook/` — the project's code dictionary, updated as coding progresses.
- `axial/` — snapshots of themes and categories following the `theme.v1` / `category.v1` schemas (after `13-axial-coding`).
- `paradigm/` — nodes and edges of the paradigm model following the `paradigmatic-node.v1` schema (after `14-paradigmatic-model`).
- `typology/` — snapshots of behavioral types following the `typology-type.v1` schema (after `16-typology`).
- `findings/` — snapshots of key findings following the `finding.v1` schema (after `17-key-findings`).
- `prompts-versions/` — snapshots of prompts at the time of each run. If a prompt changes later, you can compare.
- `runs/` — logs of skill runs (what ran when, on what, how many tokens, what came out).

If you need quotes or specific codes, ask the agent and it will produce a readable artifact in `3-analysis/`. Don't open the JSON files by hand — they aren't readable without context.

System files stay in the project folder — they're the material for lessons extraction after the report is published (see `docs/feedback-loop.md`) and for the pipeline's quarterly retro.
