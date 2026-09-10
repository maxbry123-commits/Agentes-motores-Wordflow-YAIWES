# Interpretive frames for the `interpretive_notes` field

Version: 1.0

Three configurable presets of hermeneutic lenses used by the local-coding prompt to fill `interpretive_notes`. Select via `local_coding.interpretive_preset` in `config.yaml`.

**Contents:** [Purpose](#purpose) · [Common guidance](#common-guidance) · [Minimal preset](#minimal) · [Default preset](#default) · [Full preset](#full)

---

## Purpose

The `interpretive_notes` field is **not** a mirror of structured codes — that's what `subject_codes` and `content_type` are for. This field captures the "texture of meaning" around an utterance: what the respondent is *doing* with the reply beyond its propositional content, what they are not saying, how they frame the situation. These notes help the analyst at stage 8 spot patterns that don't surface from structured codes alone.

Choose a preset based on the interview type:
- **`minimal`** for fast runs on functional questions where hermeneutic layer is overhead
- **`default`** for typical interface/technology interviews (recommended)
- **`full`** for ethnographic or sense-making interviews where deep hermeneutic layer pays off
- **`custom:<path>`** to plug in a project-specific file

The preset text is inserted into the local-coding prompt as-is, so each preset includes self-contained operational guidance.

---

## Common guidance

Included by reference in every preset:

- Write in the respondent's language. Stay close to the respondent's wording.
- Be concrete: quote or paraphrase the exact cue that triggered a lens.
- Be conservative: if nothing notable, leave the field empty. Do not fabricate.
- One short paragraph or a bulleted list, 3–8 observations max.
- Do not restate what `subject_codes` already capture.

---

## Minimal

Use only the base layer: contrasts, omissions, emotional coloring. Suitable for fast runs and standard functional questions where the hermeneutic layer is overhead.

Observe:

1. **Contrasts** — what the respondent compares the current experience against ("it used to be…", "unlike…", "normal vs. weird"). Name the specific pair.
2. **Omissions** — what the respondent pointedly stays silent about, what they leave out when answering a direct question, what they collapse into vague generalities. Explicit cases only.
3. **Emotional coloring** — irritation, delight, resignation, hope. Only when strongly expressed.

If none of the three fires, leave `interpretive_notes: null`.

---

## Default

Preset for most interface/technology interviews. Six lenses tuned to work well on product-and-task conversations without drifting into sociology.

Apply each lens **only if there is an explicit cue in the reply**. If no lens fires, leave `interpretive_notes: null`.

### 1. Speech act (Austin / Searle)

What the respondent is *doing* with the reply, not what it says:
- Stating as fact / guess / hearsay
- Justifying (shifting responsibility for the outcome)
- Distancing ("I rarely ever", "it wasn't me")
- Complaining / criticizing / praising
- Promising / committing / refusing
- Evading (answering a different question than asked)

Cue example: "I rarely buy online anyway" in reply to a question about checkout → responsibility shift + distancing.

### 2. Modalities

Which modal verbs dominate:
- **Deontic** (obligation): must, must not, have to, supposed to
- **Epistemic** (knowledge): I know, I think, I guess, I'm not sure
- **Bouletic** (desire): I want, I'd like, I need
- **Alethic** (possibility): can, can't, it works out, it doesn't work

Modality *shifts* within a single reply are especially valuable ("I want to, but I can't").

### 3. Metaphors (Lakoff)

What images the respondent uses to describe the product or experience. Relationship metaphors are especially rich: war, friendship, master/servant, road, container, struggle.

Cue examples: "I'm at war with this app", "I made friends with the bot", "I feed the algorithm", "I fell into the settings".

### 4. Attribution of causes

Who/what the respondent blames for what happened:
- Self ("I didn't figure it out")
- The system ("the interface is confusing")
- Chance ("it just happened that way")
- Other people ("my wife set it up")

Shifts of attribution within a single reply are strong signals.

### 5. Type of knowledge (Shchedrovitsky)

Which type of knowledge the respondent is producing:
- **Situational** — what is happening right now, what I see
- **Causal** — why it works this way, the mechanism
- **Normative** — how it should / shouldn't work
- **Prescriptive** — what to do about it, an instruction

Useful when the respondent switches between types within one reply.

### 6. Critical incident

Moments where something clearly went wrong or unexpectedly worked. Markers: "got stuck", "got lost", "suddenly realized", "somehow it worked", "never did figure it out", "eventually gave up".

For each: what went wrong, what the respondent did in response, what explanation they offered.

---

## Full

Expanded preset for ethnographic or sense-making interviews where a deep hermeneutic layer pays off. Contains all six lenses of Default plus four more.

### All of Default (speech act, modalities, metaphors, attributions, knowledge type, critical incidents)

See above — contents unchanged.

### 7. Frame (Goffman)

What role the respondent is answering in at this moment: expert, layperson, user, critic, parent, colleague, client, victim, hero-of-the-story. **Frame shifts** within a single reply are especially valuable.

Cues: sudden shift of lexical register, switching from "I" to "everyone"/"we"/"they", moving from evaluation to description or vice versa.

### 8. Narrative structure (Labov)

If the respondent tells a story, its structure:
- Orientation (who / where / when)
- Complication (what went wrong)
- Evaluation (what it meant)
- Resolution (how it ended)
- Coda (return to the present, moral)

Note where the respondent dwells (most detail), where they rush (skipping), where they insert evaluation.

### 9. JTBD (Jobs To Be Done)

Which "job" the respondent hires the product to do:
- Functional (achieve a result)
- Emotional (feel a certain way)
- Social (be seen a certain way)

Especially valuable when the declared job (functional) diverges from the actual one (emotional / social).

### 10. Greimas semiotic square

Binary oppositions with intermediate states:
- good / bad / not-good / not-bad
- works / broken / not-working / not-not-working (flaky, livable)
- own / foreign / not-own / not-foreign

Respondents often live in "not-bad" and "not-foreign" rather than at the pure poles — nuance lost in binary codes.

### 11. Cultural scripts

Typical "how to / how not to" patterns in the culture that the respondent implicitly relies on: "I'm not an idiot, so I wouldn't…", "a normal person would…", "that's just not done where I'm from…". Especially valuable where the script conflicts with how the product is designed.
