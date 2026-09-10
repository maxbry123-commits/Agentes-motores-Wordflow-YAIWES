---
name: desk-research
description: External desk research via web_search — what we know on the topic from public sources. Trigger — the researcher asks "what do we know about topic X", or the stage before starting a new study. Produces `1-methodology/desk-research.md` or `4-output/desk-research.md` (if standalone). In v1 WITHOUT access to the archive of internal studies (that's v2 — `desk-research-index`).
stage: 2.3
status: core
---

# 03-desk-research

## Why

Before interviews it helps to know what's already known on the topic. This lowers the risk of asking questions whose answers have long existed, and helps formulate hypotheses.

In v1 — only external public sources (web_search). An internal RAG over the research archive is `desk-research-index` v2.

## Inputs

- A topic in chat or a formulation in `0-input/<note>.md`.
- Subtopics for refinement (if the researcher provided them).
- (Optional) links to specific sources the researcher wants to include.
- If available — research questions from `project-config.yaml` or `1-methodology/questions-and-hypotheses.md`.

## Outputs

- `1-methodology/desk-research.md` (if part of a full cycle) or `4-output/desk-research.md` (if standalone via `desk-only.md`).

### Structure

```markdown
---
type: desk_research
date: TODO
sources_count: 0
---

# Desk research — {{topic}}

## What the researcher wants to understand
{{1 paragraph}}

## What we know confidently
- {{statement}} — {{source}} ({{year}}).

## What we know with caveats
- {{statement}} — {{source A}} says X, {{source B}} says Y.

## What we don't know
(gaps — candidates for RQs)

## Relevant to our product
(assessment of transferability into our context)

## Sources
1. {{Title}} — {{Author}} ({{Year}}). {{URL}}.
```

## Prompt skeleton

```
You are doing desk research for a UX study.

Topic: {{topic}}
Subtopics of interest: {{list}}
Research questions (if any): {{list}}

Task:
1. Find 8–15 relevant sources: NN/g, academic publications, industry reports, government studies (where applicable).
2. Structure the output across three levels: what we know confidently / with caveats / don't know.
3. For each statement — a source with a year.
4. Don't use marketing blog posts from SaaS companies as a primary source, except when the researcher explicitly asked about them.
5. In the "relevant to our product" section — honestly assess transferability. If a source is about the US/Europe and we work in a different context — note it.

What NOT to do:
- don't reproduce large chunks of text from sources (>15 words) — paraphrase.
- don't make recommendations (that's no longer desk research).
- don't confuse "don't know" with "didn't find in open sources".
```

## DoD

- [ ] At least 5 sources, ideally 8–15.
- [ ] Each statement is tied to a source.
- [ ] An explicit split "confidently / with caveats / don't know".
- [ ] The transferability section — filled in, not left empty.

## Failure modes

- **The topic is too vague.** Clarify before launching the search. "Something about onboarding" = useless.
- **Sources only from the US.** That doesn't make them wrong, but in our context they may not work (different platforms, habits, regulation). Note it.
- **Overrating academia.** "According to a 1987 study…" — sometimes good, sometimes incompatible with modern interfaces. Common sense beats reverence.
- **Claims without sources.** Don't write "it's known that…" without a reference. That's hallucination.

## Mode behavior

- **assistive**: after generation — pause, in chat 2–3 sentences "here's the main thing I see. Want to deepen some block?".
- **autonomous**: write the full document, in `concerns.md` indicate which sources are unreliable or dated.

## What remains for v2

- Search over the archive of internal studies (RAG).
- Re-creating a mini-report from old transcripts for the current request.
- Triangulation of "what external authors say" × "what we already know on the team".
