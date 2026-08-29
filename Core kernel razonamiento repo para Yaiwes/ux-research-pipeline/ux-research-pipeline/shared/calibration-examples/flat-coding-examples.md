# Calibration examples for `09-flat-coding`

Domain reference examples from a real study (topic: searching for housing in a browser / real-estate apps). Used in `prompts/flat-coding.md` v0.3 as hard-coded examples. If they are recalibrated after a future pilot, update them here and bump the prompt version.

> **Source**: a housing-search study. PII has been replaced with aggregated demographics ("man, ~30, large city"). Verbatim text is preserved word-for-word; only the name in the first segment has been replaced with "<name>".

---

## Section A — content_type

### A.1 `fact` — a description of behavior, experience, or observation

Markers: subject "I / he / she," past- or present-tense verbs, concrete actions or recurring patterns.

**Example A.1.1** (background, demographics)
```
verbatim: "<name>, born in '90. I've lived in the city full-time since birth.
Right now I work as a logistics assistant at a transport company.
I do have a degree — as a doctor — but I'm not a doctor. It turned out not to be for me.
Single, no kids either."
content_type: fact
content_codes: ["lifelong city resident works as a remote logistics assistant", "career switch from doctor to logistics"]
notes: contains_pii (name — mask downstream)
```

**Example A.1.2** (a habit — looks like a hypothesis because of "maybe," but it describes reality)
```
verbatim: "On the laptop, for example, to get into a food-delivery service I open the browser first,
and only then go to the service itself. I go through the browser when it's the laptop.
It can be at any time of day: morning, afternoon, evening.
If I need to find something, I open the browser."
content_type: fact
content_codes: ["browser as the entry point to other services", "browser kept open all the time on the laptop"]
```

**Why fact**: "it can be at any time" describes a distribution over time, **not** a guess about the future. The tell: the surrounding context is concrete actions ("I open," "I go").

### A.2 `interpretation` — an explanation of "why," a causal link

Markers: "because," "I think," "it seems," "as if," "maybe it's down to…". The respondent explains an already-established fact.

**Example A.2.1**
```
verbatim: "I used the classifieds site, but not to search for housing. I'd just drop in,
scroll a bit, and leave. I didn't dig into the listings.
Probably because that site isn't specialized in housing. I know it's more about resale there."
content_type: interpretation
content_codes: ["classifieds site perceived as a resale marketplace, not housing"]
```

**Why interpretation, not hypothesis**: "probably because" — the respondent is **explaining their actual behavior** (they used the site and didn't dig in). It's an explanation of a fact, not a guess about the future.

**Example A.2.2**
```
verbatim: "It's been on the market a long time, there's trust in it. A large base of users
who post listings or search. I think that's it. Plus, maybe,
a convenient filter. These days everyone's filters are more or less the same."
content_type: interpretation
content_codes: ["chooses the incumbent listing site for its longevity and trust", "large user base as a trust factor"]
```

**Example A.2.3**
```
verbatim: "Overall it's clear there are listings. But it's all kind of on a white background,
the pictures don't stand out from each other. Like everything's gray-and-white in the background.
If I scroll fast, I can't tell what's where at all."
content_type: interpretation
content_codes: ["listings blur together on fast scroll due to gray-white scheme"]
```

**Why interpretation**: the respondent states the cause of their observation ("I can't tell what's where because it's all gray"). "Like" is a causal link.

### A.3 `hypothesis` — a guess about future behavior or about an uncertain cause

Markers: conditional mood, "if only," "it would be better if," "maybe add," "I'd guess." The respondent builds a construct whose reality they themselves are unsure of.

**Example A.3.1** (a proposed design fix)
```
verbatim: "For new services, add a thin little outline. A red badge —
something new has appeared in the browser."
content_type: hypothesis
content_codes: ["would like a color marker for novelty on the tile"]
```

**Example A.3.2** (a conditional promise)
```
verbatim: "If I saw a 'real estate' badge and a price comparison across different sources,
I'd go straight through the browser. The incumbent site is years of habit. As an aggregator —
if there's a price comparison, that would catch my attention."
content_type: hypothesis
content_codes: ["two switching conditions: 'real estate' naming and a visible price comparison"]
notes: a typical "polite" forecast about one's own future behavior — treat with caution
```

**Example A.3.3** (a prediction of how the service works)
```
verbatim: "I'd guess it's a service like the big listing sites.
Probably something similar, with filters you can configure.
Maybe even some minimal info before you click through: floor area, square meters, price."
content_type: hypothesis
content_codes: ["expects functionality similar to existing listing sites"]
```

---

## Section B — a common mistake: "maybe / perhaps" ≠ automatically a hypothesis

In R04 v1 the worker tagged `hypothesis` on every appearance of "maybe / perhaps / sometimes." That produced a 72/4/23 skew. The rule:

> Uncertainty markers (`maybe`, `perhaps`, `probably`, `sometimes`) are a **necessary but not sufficient** condition for `hypothesis`. A hypothesis is tagged **when the construct as a whole is built as a guess about future behavior** or **about an alternative reality** that the respondent themselves is unsure of.

| Phrase | content_type | Why |
|---|---|---|
| "It can be at any time of day: morning, afternoon, evening" | `fact` | describes the time distribution of a real pattern |
| "Probably because that site isn't specialized in housing" | `interpretation` | explains an already-established fact |
| "Maybe outline it somehow around the perimeter… draw a border" | `hypothesis` | proposes a non-existent design fix |
| "Sometimes it's something mundane or just for no reason" | `fact` | describes the distribution of a pattern |
| "If I'd seen a price comparison, I would have switched" | `hypothesis` | a conditional forecast |
| "I think that's it. Plus, maybe, a convenient filter" | `interpretation` | an explanation of a choice, not a guess |

---

## Section C — segmentation: minimum length and merging

### C.1 Minimum segment — 15 seconds / 80 characters of verbatim

Exception: single short respondent answers ("Yes," "No," "I don't know") if they answer a substantive interviewer question. In that case the verbatim is shorter, but the segment **must** be tied to the preceding interviewer segment.

**Anti-example** (R07 v1, which triggered the recalibration):

```
[seg-0245] 00:42:17-00:42:21 verbatim: "No."
[seg-0246] 00:42:21-00:42:25 verbatim: "I don't know, never used it."
[seg-0247] 00:42:25-00:42:30 verbatim: "Maybe."
```

This "one segment = one short reply" behavior produced 1,082 segments for 76 minutes. The correct approach is to merge these three replies into a single segment or, if they answer different questions, attach each to its interviewer segment as context in `notes`.

### C.2 Merging interviewer replies

3–5 short interviewer replies in a row within a single question block = **one** segment. Otherwise the count of interviewer segments balloons.

**Anti-example** (R03 v1):

```
[seg-0001] 00:00:00-00:00:01 "Recording's rolling."
[seg-0002] 00:00:02-00:00:04 "So, the first question will be an easy one."
[seg-0003] 00:00:04-00:00:06 "Let's get to know you a bit. Tell me a little about yourself."
[seg-0004] 00:00:06-00:00:07 "Where are you from? Which city?"
[seg-0005] 00:00:07-00:00:08 "How old are you?"
[seg-0006] 00:00:08-00:00:09 "What do you do in life, generally?"
```

The correct approach is one interviewer segment:

```
[seg-0001] 00:00:00-00:00:09 speaker: interviewer
verbatim: "Recording's rolling. So, the first question will be an easy one.
Let's get to know you a bit. Tell me a little about yourself.
Where are you from? Which city? How old are you? What do you do in life, generally?"
content_codes: ["interviewer-prompt"]
notes: intro / rapport block
```

---

## Section D — blacklist of codes

These phrasings are forbidden in `content_codes` — they are category codes that belong in `13-axial-coding`, **not here**:

- `experience-description`, `usability-rating`, `mentions-X`, `requirements-elicitation`
- `usability-problem`, `motivation`, `need`, `barrier`, `pain`
- `positive-experience`, `negative-experience`, `feedback`
- `functional-requirement`, `non-functional-requirement`

If a code drifts toward a category, replace it with a flat verb/noun phrase close to the respondent's words. Replacement examples:

| Bad (category) | Good (flat code) |
|---|---|
| `usability-problem` | `can't find the metro filter in the listing` |
| `experience-description` | `searched three months for an apartment on the listing site` |
| `motivation` | `chooses the incumbent site for its longevity` |
| `negative-experience` | `listings blur together on fast scroll` |
| `mentions-filter` | `uses the metro and price filter as primary` |

---

## Section E — verbatim check

The verbatim **must** exist in the source transcript character-for-character. Including punctuation, recognition typos, and filler words ("uh," "um").

If the meaning requires merging two consecutive replies by the same speaker, the verbatim includes both as they are, separated by `\n`. Do not shorten, normalize, or translate.

On a mismatch (found later, didn't fully match) — `confidence: low` + `notes: verbatim-near-match` + add `coding_meta.verbatim_check.failed_segment_ids`.

---

## Version history

- Assembled from the housing-search study after the calibration review. Recalibrated after the errors in R04 (72/4/23 skew), R07 (1,082 segments), and R03 (380 interviewer segments).
