---
name: narrative-adapt
description: Rewrites the academically dry `4-output/report.md` (after `18-report-draft`) into language the stakeholder can understand. Removes anglicisms, percentages and "X out of 14," academic type labels, "priority 1/2/3" ranks, poetic tone. Renders respondent names via relevant context. Restructures: the report opens with answers to the brief's hypotheses; the sample's dichotomy becomes a separate axis of analysis in every section. In parallel, adapts the stakeholder-facing version of the paradigm model and the typology. Does not touch the chapter structure from 18 and does not alter verbatim quotes.
stage: 9.5
status: core
---

# 18.5-narrative-adapt

## Why

This is the methodological bridge between "a report a researcher understands" (the output of `18-report-draft`) and "a report a stakeholder understands" (the input of `19-format`).

Without this stage:
- The report fills up with anglicisms ("usability," "verbatim," "funnel," "value proposition," "word-of-mouth," "N=1").
- On a qualitative sample of 14 interviews you get percentages and "X out of 14" — methodologically incorrect for in-depth studies.
- Ranking recommendations as "Priority 1, 2, 3" — an in-depth study has no mandate to prioritize product tasks.
- Respondent names in the "Paul / Paul 2" style — not humane.
- Types from the typology live as "T1 Active comparer" — the stakeholder doesn't follow.
- The paradigm model is shown to the stakeholder in Strauss/Corbin terms — "causal / contextual / strategy" — that is academic apparatus, rewritten for the report.
- A poetic, narrative tone — "the voices of people front and center," "the powerful quotes that stayed with us" — feels false and saccharine. What's needed is a descriptive-factual tone, like in side-by-side comparative reports.
- Structure: 18 lays out executive → about the project → methodology → key findings. The stakeholder needs: answers to the brief's hypotheses right after a short note on method. Methodology goes down, into a collapsed block.
- The sample's dichotomy (e.g. "familiar with the product" vs "newcomers") sits as a note in the methodology. If the sample was deliberately split — it is a **separate axis of analysis** in every section.

## Trigger

After `18-report-draft`. Runs **automatically** in any mode (assistive and autonomous) — this is not optional editing, it is a methodologically mandatory stage.

The researcher can invoke it by hand: "adapt the report for the stakeholder" / "rewrite the report in client-facing language" / "18.5."

## Pre-flight: hard gate `outline_approved`

Before any edits, you **must** check the frontmatter of `4-output/report.md`:

- If `outline_approved: true` is missing — **stop and refuse to work**. In chat, one line to the researcher: "I can't run 18.5 — `report.md` has no `outline_approved: true` in the frontmatter. That means Step 2 in `18-report-draft` (agreeing the plan) was skipped. Go back to 18 and confirm the outline." Then wait.
- If `outline_approved: true` is present but `autonomous_approved: true` is also set — that means the outline was auto-approved in autonomous mode, without a human. Continue, but record in `concerns.md` "the outline did not go through the researcher" — they will see it when reviewing the client version.
- If there's a normal `outline_approved: true` with `outline_approved_at: <date>` — continue as usual.

This is a gate. Don't bypass it "because the report is already there" — without an agreed plan, 18.5 risks restructuring something the researcher never approved.

## Inputs

- `4-output/report.md` — the output of `18-report-draft` (a draft in academic language, but with verbatim already checked).
- `3-analysis/findings/F0X.md` — in case you need the full picture for a reformulation.
- `3-analysis/typology.md` + `3-analysis/types/*.md` — for adapting the type labels.
- `3-analysis/model.md` (or `.canvas`) — for building the client version of the paradigm model.
- `1-methodology/brief.md` — to know **which hypotheses** the report should open with.
- `1-methodology/questions-and-hypotheses.md` — the hypothesis wording to move to the front.
- `project-config.yaml.segments` — the sample dichotomy description (if any).
- `thoughts.md` — the researcher's notes; may contain "this is important for the stakeholder."
- `RESEARCH_PROJECTS_ROOT/_knowledge/lessons.md` — the list of style violations already recorded in past projects. Apply it.

## Outputs

- `4-output/report.md` — **rewritten** in adapted language. The old version is saved as `4-output/.report-pre-adapt.md` (hidden, for diff comparison and lessons-extraction).
- In the frontmatter: `narrative_adapted: true`, `narrative_adapt_run_at: YYYY-MM-DD`.
- `3-analysis/model-client.md` — a textual "story" of the paradigm model in 10–12 nodes with human labels. The `model.md` / `model.canvas` itself stays in Strauss/Corbin notation for the academic appendix.
- `3-analysis/typology-client.md` — types with descriptive labels, no "T1/T2."
- `.system/runs/narrative-adapt-<timestamp>.log` — a log: what was replaced, what was rewritten, what couldn't be done (with a rationale).

## Closed list of rules

**These are not recommendations, they are a gate.** We don't pass downstream until every rule has been applied.

### 1. Stop words (anglicisms and jargon)

**Two-layer check:**

1. **The closed stop-list below** — for a quick check of the most common violations.
2. **A full scan via the script** `shared/scripts/detect-english-words.py` — for completeness. The script extracts **all** Latin tokens from the main text, classifies them (`brand` / `abbrev` / `term` / `stoplist` / `generic`), gives context (the sentence the word appeared in), and returns exit code `2` if there are candidates to decide on. See the "§13. English-words pass via the script" section below — it is a **mandatory** step of the 18.5 algorithm.

Closed list (for reference):

| Forbidden | Replace with (one of) |
|---|---|
| usability | ease of use / ergonomics |
| verbatim | direct quote / a person's exact words |
| value proposition | value proposition / what sets it apart from competitors |
| paradigm (in the client version) | in the adapted model — rewrite as "how it works"; stays in the academic notation |
| funnel | path / funnel (only if the reader definitely understands it; otherwise "sequence of steps") |
| word-of-mouth | word of mouth / advice from people they know |
| pain point | problem / difficulty |
| user journey | user path |
| insight (as a noun) | observation / finding |
| persona | portrait / type |
| flow / user flow | sequence of steps |
| N=1 / n= | in a qualitative report — describe in words, no formula |
| onboarding | first encounter / initial experience |
| churn | drop-off / leaving |
| retention | retention |
| engagement | engagement / interest |
| conversion (if not a comparative-test metric) | transition / decision |
| feature | capability / function |
| baseline | starting level / point of departure |
| A/B test in a qualitative report | (mention with the note "a quantitative measurement") |

The list grows project over project — see `_knowledge/lessons.md`. Before running, read the latest lessons.md and add to this list everything flagged with the `[style]` category.

### 2. No percentages and exact fractions on a qualitative sample

On samples of 8–15 respondents, **in the main text of the report** — none of:
- "80% of respondents";
- "11 out of 14 mentioned";
- "4 out of 6 in group A";
- "a third of respondents."

Acceptable phrasings:

| Pattern strength | Phrasing |
|---|---|
| ≥80% of the sample | "most of them" / "almost everyone" |
| ~50% or more than half | "more than half" / "a noticeable share" |
| 3–5 respondents | "a few of them" |
| 1–2 respondents | "one or two" / "an isolated case" |
| Group dichotomy (important) | "everyone in group A — no one in group B" (an exact "X out of Y" is acceptable here as evidence of the dichotomy) |

**The exception** — only dichotomies and extreme cases (see the table). And only because they are fundamental to the argument.

### 3. No ranking of recommendations

- NO: "Priority 1 / 2 / 3," "high/medium/low," "top-7 recommendations."
- YES: "short steps you can take right away" vs "long-term directions."

A qualitative in-depth study gives no basis for prioritization — we have neither data on business impact nor context on cost. The product manager decides that after a discussion.

In the client version, recommendations stay as **observations that need discussion with the product manager and the designer**. The `[draft]` tag is preserved.

### 4. Respondent names via relevant context

- NO: "Paul," "Paul 2," "R03," "R07."
- YES: "Paul from Chusovoy," "Paul from Krasnodar," "Anna, 34, Moscow, experienced."

Relevant context is whatever is **significant for the specific finding**:
- If it's about geo-tied services — the city.
- If it's about a skill — the experience level.
- If it's about demographics — age and gender (but carefully — this must not replace the behavioral typology).

The `R0X` identifiers are kept in the appendix and in the system files; **in the main report text — only human descriptions**.

### 5. Descriptive type labels

- NO: "T1 Active comparer," "T3 Loyal generalist."
- YES: "Those who figure it out by comparing data," "Those for whom the marketplace is the starting point," "Those who trust the word of people they know."

Rule: a type label is a phrase of 4–9 words that describes **behavior**, not an attribute. It reads on its own, without a key.

### 6. Hypothesis-status colors

Hypothesis status drives color semantics, applied generically by `19-format` when it renders the report:

| Hypothesis status | Color |
|---|---|
| Confirmed | green / blue |
| Partial / ambiguous | orange |
| Not confirmed | red |

"Brand red = confirmed" is **forbidden**. In the context of hypothesis testing, red reads as "problem / needs attention," and that semantics must not be broken for the sake of brand style.

### 7. Poetry and pathos

Forbidden constructions:
- "the voices of people front and center";
- "the powerful quotes that stayed with us";
- "the study revealed…," "it was discovered…," "we managed to discern";
- "we heard," "we tell the story";
- "the story of one user" (only if it really is one story and the context calls for it).

The tone standard is **descriptive-factual**, like in the team's side-by-side comparative reports. Interpretation goes in a separate callout ("Interpretation: …"), not dissolved into the narrative.

### 8. Structure: start with answers to the hypotheses

The target order of sections **after** `18.5`:

1. The main conclusion (1 paragraph) or executive summary (2–3 paragraphs).
2. **Answers to the hypotheses from the brief** — a table or short bullets (H1: confirmed / not confirmed / partial + one phrase on why).
3. About the project — a short block (method, period, sample). No "72-minute median" — those are technical metrics.
4. Key findings.
5. (optional) Adapted paradigm model — the client version.
6. (optional) Typology — client labels.
7. What we did not find (though we looked).
8. Observations for discussion with the product manager and the designer (the former "recommendations `[draft]`").
9. New directions for the next study.
10. Methodological caveats.
11. Appendices (including the academic paradigm model in Strauss/Corbin notation).

If `18-report-draft` had a different order — rearrange it.

### 9. The sample dichotomy as an axis

If `project-config.yaml.segments` describes two groups (e.g. "familiar with the product" vs "newcomers," "bought" vs "declined"), then **in every substantive section** there is an **explicit cut by group**. Not as "we had two groups in the sample," but as "for group A it worked like this, for group B differently."

Cut format: at the end of each finding — a `**By group.**` subheading with one or two phrases on the difference (or an explicit "no difference recorded").

### 10. Technical metrics — out

Removed from the main report text:
- "N segments coded";
- "N hours of audio";
- "72-minute median";
- "MEDIAN_DURATION," "P50," "P95."

If the researcher wants them — keep them in a collapsed "Corpus volume" block in the methodological appendix.

### 11. Adapting the paradigm model

`3-analysis/model.md` (or `.canvas`) is written in Strauss/Corbin terms — that is correct for the academic part. For the report, a separate client version is written:

- 10–12 nodes maximum.
- Story format, not a tangled diagram: "it happens → it gets cut off → in a rare case it works out" (but **only as a structure of exposition**, not as a replacement of the terms).
- Nodes renamed from causal/contextual/strategy/consequence/intervening to human descriptions. For example: "causal condition: needs an apartment by the end of the rental contract" → "**Housing deadline**: the rental contract ends in X months."
- Arrows — simple phrasings: "leads to," "gets worse when," "sometimes ends with."

Written to `3-analysis/model-client.md` (Markdown + optionally mermaid with short nodes). The academic `model.md` / `.canvas` stays untouched.

### 12. Adapting the typology

Same approach: `3-analysis/typology-client.md` with a list of types, each with a descriptive label (see §5), 2–3 sentences of characterization, and one verbatim quote each (with the verbatim already checked, copied from 17/18 as is — no repeat verbatim check).

## Algorithm

1. **Read** all inputs. Pay special attention to `thoughts.md` and `_knowledge/lessons.md` for fresh `[style]` categories.
2. **Build the stop-list** — the standard one (§1) + everything added from lessons.
3. **Do the structural edit** — rearrange sections per §8, add the "By group" axis to every finding (§9).
4. **Walk the text** and apply rules §1–7, §10. This is mostly replacements and rewrites.
5. **Adapt the paradigm model** — create `3-analysis/model-client.md` (§11).
6. **Adapt the typology** — create `3-analysis/typology-client.md` (§12).
7. **Reread the whole report** — a sanity check for "false saccharine tone," "poetry" (§7). If anything still reads like a PR release — rewrite it.
8. **Write** the new version of `report.md` over the old one, saving the old one as `.report-pre-adapt.md`.
9. **Log** to `.system/runs/narrative-adapt-<timestamp>.log`: what was replaced (top-20 edits), what couldn't be done and why.
10. In chat to the researcher, briefly: "adapted the report. Main edits: <top-3>. The old version — `.report-pre-adapt.md`. Ready to run `19-format`?".

## DoD

- [ ] `4-output/report.md` contains not a single word from the §1 stop-list.
- [ ] The main text has no percentages or "X out of Y" constructions — except explicit group dichotomies.
- [ ] No "Priority 1/2/3," no "high/medium/low" on recommendations.
- [ ] Respondent names — via relevant context; the R0X identifiers appear only in the appendix.
- [ ] Types from the typology are described as 4–9 word behavior phrases; no "T1/T2."
- [ ] Hypothesis-status colors — blue/green for confirmed, red for not confirmed.
- [ ] The report opens with the executive + answers to the hypotheses; methodology is below.
- [ ] If the sample is dichotomous — every key finding has a "By group" subsection.
- [ ] No technical metrics "N segments," "72 minutes" in the main text.
- [ ] `3-analysis/model-client.md` created, 10–12 nodes, no causal/contextual/strategy in the client phrasings.
- [ ] `3-analysis/typology-client.md` created.
- [ ] Verbatims are NOT changed (verbatim_check already passed in 17/18 — here, only the framing text).
- [ ] Frontmatter `narrative_adapted: true` set.
- [ ] **The `detect-english-words.py` script was run on the final version.** For every word in the `stoplist` and `generic` categories, an explicit decision was made (replaced / kept with a rationale in `agent-notes.md`).
- [ ] **The query list** (words the LLM is unsure about) is either approved by the researcher or recorded in `concerns.md` with a proposed resolution.

## Failure modes

- **A verbatim quote was changed** — a critical error. Compare the old and new versions: `diff .report-pre-adapt.md report.md`; the quotes in quotation marks must be identical. If anything changed — roll it back, rewrite only the framing.
- **Can't find a plain-language equivalent** — you hit a piece of jargon or an untranslated buzzword with no established plain-language equivalent. Give 1–2 options in chat and ask the researcher. Not "I'll leave it as is."
- **The structure doesn't fit §8** — e.g. the RQ are so narrow that "answers to the hypotheses" duplicate the executive. Then collapse the executive to 1 paragraph and make answers to the hypotheses the main first section.
- **The pilot sample isn't dichotomous** — skip §9 (instead of "By group," normal findings), but record in the log "no dichotomy, no cut made."
- **The paradigm model in the source was already rewritten for the stakeholder** (e.g. the researcher did it by hand) — don't recreate it, just copy it with minimal edits. Record it in the log.

## Mode behavior

- **assistive**: after the pass — a short message with the top-3 edits and an offer to "read it and fix anything that's off. Good? On to the Markdown formatting step?". Pause until confirmation.
- **autonomous**: recorded; in `concerns.md` — the spots where you're unsure of a translation or had to make a structural choice without explicit grounds.

## After the pass — mandatory

1. Compare `.report-pre-adapt.md` and `report.md`. The top-5 substantive edits (not cosmetics) are candidates for `_knowledge/lessons.md` in the `[style]` category.
2. Record the candidates in chat to the researcher with an offer to confirm.
3. On "yes" — add them to `lessons.md`.
4. This is the same trigger as in `18-report-draft` (lessons-extraction), but the focus is on style and adaptation. If 18 already proposed a lesson and it concerned content — add this one on top, don't duplicate.

## Contract with 19-format

`19-format` refuses to work with a report that lacks `narrative_adapted: true` in the frontmatter. This is a hard boundary: without `18.5`, a draft ends up in the team wiki.

If the researcher wants to skip `18.5` (e.g. the report is already in good language) — they explicitly say "skip 18.5," and then `19-format` runs with a warning "language adaptation skipped at the researcher's request." In autonomous mode the agent does not make this decision on its own.

---

## §13. English-words pass via the script (mandatory stage)

**Don't strip out all anglicisms automatically. Decide on each one in context.**

This rule matters: the stop-list is closed and deliberately incomplete. And "strip out everything Latin" is methodologically wrong, because brand names (`YouTube`, `iPhone`, a marketplace name), team abbreviations (`UX`, `MR`, `JTBD`, `NPS`) and technical terms should stay. The decision on each word is made by the **LLM**, based on the sentence context and the document type.

### Algorithm

1. **Run the script** on the version being adapted:

   ```bash
   python3 shared/scripts/detect-english-words.py 4-output/report.md
   ```

   The script ignores frontmatter, code fences, URLs, and file paths. It returns a structured list of Latin tokens with category and context. Exit code:
   - `0` — no `generic` / `stoplist` at all. You can move on.
   - `2` — there are `generic` / `stoplist`. An LLM decision is needed on each.

2. **If exit code = 2** — go through every unique word in the `stoplist` and `generic` categories and make a **separate decision**:

   - **Category `stoplist`** (`onboarding`, `retention`, `usability`, `funnel`, `pain`, `flow`, `wow`, `interviews`, `experience`, ...) — these are **strong candidates** for replacement. By default, replace. But if in a specific context the word conveys a meaning its native equivalent doesn't (a rare case) — keep it, but add a `concerns.md` entry with a rationale.
   - **Category `generic`** (a new Latin word that landed in no list) — an **open question**. Read the sentence the word appeared in. Decide: does a native equivalent fit? If yes — replace. If no — keep it and add to `concerns.md`. If unsure — put it on the query list (see below).
   - **Category `brand`** (a marketplace name, `YouTube`, `iPhone`, `Google`, `Cowork`, ...) — **keep it**. These are proper names. But if a brand is used in a **generic** sense ("googled it" as a verb → "searched online") — reword it.
   - **Category `abbrev`** (`UX`, `MR`, `JTBD`, `RQ`, `H1`, `F1`, ...) — **keep it**. These are part of the team's professional vocabulary. Exception: if the report has abbreviations **without expansion** that the stakeholder may not know (`NPS`, `CSAT`, `JTBD`) — add the expansion at first use: "JTBD (Jobs To Be Done) — the task the user is solving with the product."
   - **Category `term`** (`Mermaid`, `Pydantic`, ...) — **keep it** if it's in a technical section. If it's in the main report text for the stakeholder — reword it.

3. **Query list.** If you can't make a confident decision on a word (typical case: a brand neologism, a coinage, or a term that **might** be an abbreviation but it's unclear) — collect such words separately and at the end of the pass present them to the researcher:

   > Unsure about the words: `<word1>`, `<word2>`, `<word3>`. Context:
   > - `<word1>` — "{{sentence}}"
   > - `<word2>` — "{{sentence}}"
   >
   > Replace / keep / expand?

   In assistive — wait for an answer. In autonomous — write to `concerns.md` with a proposed resolution for each; a reviewing agent or the researcher will double-check them.

4. **Apply the decisions.** Write to `4-output/report.md`. Log every replacement to `.system/runs/narrative-adapt-<timestamp>.log` as `word → replacement (category: <cat>, reason: <reason>)`.

5. **Rerun the script** on the final version. All remaining words should be in the `brand`, `abbrev`, `term` categories. If anything is left in `stoplist` or `generic`, it means you consciously decided to "keep" it. Record the reason for each in `agent-notes.md`.

### What the script does NOT do

- It doesn't make decisions. It's a completeness tool, not a rule.
- It doesn't edit the file. It only shows.
- It doesn't account for the inflection of native words. If in the LLM pass you translated `onboarding` as a native phrase, a rerun won't show "onboarding" — but if you missed one instance, it will.
- It doesn't distinguish "in code / in the main text" context. It ignores code fences and inline code, but if you accidentally quote a technical term without backticks — the script will show it; the "keep" decision is yours.

### Updating the lists

If the researcher says "this `dashboard` — keep it, that's how we talk on the team" — add it to `TEAM_ABBREVS` or `TECH_TERMS` in the script (the category grows). This improves the script from project to project.

If, conversely, the researcher says "this word definitely needs changing" — add it to `HARD_STOPLIST`. Do it **right after the pass**, so you don't miss it in the next project.

Updates to `_knowledge/lessons.md` in the `[style]` category (see the "After the pass — mandatory" section) are the material for expanding these lists.

## STOP — handoff after this skill

`18.5-narrative-adapt` is the last "heavy" boundary before `19-format` (see AGENT.md §14.1). After 18.5 the report moves from the academic to the client version — a serious methodological decision the researcher must read. Hard rule §14.0: **never run `19-format` automatically.**

By `session_budget`:

- `low` — handoff is **required**. The researcher reads the client version of the report between sessions, without rushing.
- `normal` — handoff is **required**. Same.
- `high` — handoff is desirable; at minimum, a mandatory pause for review.

When 18.5 is done:

1. Append a **"Handoff to next session"** section to the top of `.system/agent-notes.md`. Inside: what was reformulated (a brief summary of replacement categories), which words on the query list were left undecided, and what to read in the new session (at minimum — `4-output/report.md` with `narrative_adapted: true` in the frontmatter, `model-client.md`, `typology-client.md`).
2. Print the STOP-handoff block per the AGENT.md §14.2 template, with separators. **Additionally** include a link to the report and an offer to read it and record edits in `feedback.md` before `19-format`.
3. **Do not run** `19-format`. Never automatically — not even in autonomous; see the "Mode behavior" section of this skill.

Lessons-extraction (see the "After the pass — mandatory" section above) is done BEFORE the handoff, in the current session. Don't push it to a new session — do it while the context is fresh.
