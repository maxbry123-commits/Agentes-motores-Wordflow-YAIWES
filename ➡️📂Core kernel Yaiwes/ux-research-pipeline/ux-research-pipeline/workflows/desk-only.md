# Workflow: desk-only

Desk research only. No interviews.

## Trigger

- The researcher said something like "what do we know about topic X" / "a day of desk research" / "before we take this on — look into it."
- There are no interviews in `2-interviews/` (yet, or at all).

## Preconditions

- The topic, stated in chat or in `0-input/<note>.md`.
- (Optional) links the researcher provides to specific sources.
- In v1 there is **no** access to an archive of past internal transcripts and reports (that's `desk-research-index`, planned for v2). We work from external sources and from whatever the researcher supplies directly.

## What the agent does

1. **Clarify the task.**
   - What business question sits behind this request?
   - Which sub-topics are of most interest?
   - Are there specific sources the researcher wants you to look at?
   - Depth: a one-hour overview or a serious day-long report?

2. **Gather sources.** In `03-desk-research`:
   - Web search across the clarified sub-topics.
   - Read reputable sources: Nielsen Norman Group, UX Design, academic JSTOR snippets, industry reports.
   - If present — link to materials the researcher placed in `0-input/`.

3. **Structure the output.** In `4-output/desk-research.md`:

```markdown
# Desk research — {{topic}}

> External sources, not cross-checked against an archive of internal studies (that's v2 of the pipeline).
> {{date}}.

## What the researcher wants to understand

{{1 paragraph}}

## What we know with confidence

(points with sources; explicit flag "industry / academia / our team")

- {{claim}} — {{source}} ({{year}}).

## What we know with caveats

(contested claims, differing positions in the literature)

- {{claim}} — {{source A}} says X, {{source B}} says Y.

## What we don't know

(gaps — candidate research questions for a future study)

- {{what isn't covered}}

## Relevance to our product

(transferability assessment — not everything found applies in our context)

## Sources

(full list with links)
```

4. **No interviews** in this workflow. If the researcher says mid-stream "okay, now let's recruit 5 people" — switch to `full-assistive.md`.

## Failure modes

- **The topic is vague** ("something about onboarding"). Clarify it **before** launching the search. Otherwise the result will be useless.
- **Only marketing sources** (promotional blog posts from SaaS companies). Flag them as low-trust. Good sources: NN/g, academia, government research (where applicable), respected industry reports.
- **Too academic.** Desk research is a working artifact, not a literature review. If the output has no applicability to the product — redo it.
- **Competitors named explicitly.** Keep the reverse-NDA in mind: you don't actually know what's inside their products. Only what's public.

## What the agent does NOT do

- Does not try to simulate an archive of past internal studies (RAG over the team wiki). That's `desk-research-index`, planned for v2 — not yet available. If the researcher wants internal data, they supply it manually in `0-input/`.
- Does not make recommendations. Desk research is "what we know," not "what to do."
