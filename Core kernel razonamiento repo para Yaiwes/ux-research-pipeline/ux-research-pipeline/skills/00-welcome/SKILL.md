---
name: welcome
description: First-run onboarding for a new researcher opening ux-research-pipeline for the first time. Trigger — absence of the marker `.system/welcomed-at.txt` in the repo root AND no active research project. Does: a 3-screen intro to how the system works, sets up MISTRAL_API_KEY via setup-mistral.sh, optionally requests additional keys, writes the marker, and hands off to 01-brief-intake or offers a demo project.
stage: 0
status: core
---

# 00-welcome

## Why

This system is launched by different people: someone seeing Cowork for the first time, someone who has never worked with an agent, someone on a Claude Pro plan with usage limits. Without explicit onboarding they get lost in one of:
- not understanding what kind of methodology to expect (is this a parsable auto-pipeline or a conversational partner?);
- not knowing that MISTRAL_API_KEY is needed and where to get it;
- thinking they have to create folders and edit configs by hand;
- launching heavy skills without realizing there's a Claude Pro session limit.

This skill — short, **once per user** — closes these gaps and leaves a marker so it never shows again on subsequent launches.

## Trigger

Fires when **all of the following** hold:
1. The workspace has no active research project (no `project-config.yaml` in any `research-projects/<slug>/`).
2. The root of `ux-research-pipeline/` has no `.system/welcomed-at.txt` file.
3. The user's first chat is open (any first substantive message — "hi", "help", a task description).

If even one of these conditions is broken — **do not show yourself**. If there is an active project but no marker (for example, the researcher imported a project from another workspace) — quietly create the marker yourself and don't interrupt the work.

## Inputs

- No file inputs. The skill works purely from the environment.
- If the researcher already described a task in their first message — take it into account when choosing the final offer (create a project now vs. run the demo).

## Outputs

- `.system/welcomed-at.txt` in the root of `ux-research-pipeline/` — the "onboarding done" marker. Contains the date and version (see below).
- `~/.config/ux-transcribe/.env` with `MISTRAL_API_KEY=...` (via `shared/scripts/setup-mistral.sh`) — if the researcher provided a key.
- In chat — a short intro and an offer of "how we proceed".

## Behavior

### Step 0: check the marker

If `.system/welcomed-at.txt` already exists — **exit quietly**. Don't run again. If it exists but the contents are corrupt or older than 6 months (a new system version has shipped) — you may show a "short refresh" (1 paragraph on what's new), but that's a separate v0.6+ scenario.

### Step 1: introduction and three screens

In chat — three short blocks (one after another, like a conversation, not all at once as a list):

**Screen 1 — who I am and what this is:**

```
Hi. This is ux-research-pipeline — an assistant for in-depth interviews for
the UX research team. I'll guide you through the cycle from brief intake
with the stakeholder to the report and presentation.

I'm not a workflow-runner and I don't do everything at the push of a button.
I'm a conversational partner: you decide, I suggest and format. Under the
hood there are ~25 skills — but you don't see them in chat, I decide myself
which one is needed right now.
```

After that — a **short pause** (wait for any reply: "got it" / "ok" / even an emoji). Don't dump the second screen right after.

**Screen 2 — how the work goes:**

```
A few things about working with me:

- All research materials are under NDA. I won't suggest uploading them to
  public services (ChatGPT.com web, Claude.ai web, public GitHub).
- One project = many chat sessions. At stage boundaries (after coding,
  after analysis, after the stakeholder version of the report) I'll suggest
  opening a new chat — it's cleaner and cheaper than running everything in one.
- If you're on a Claude Pro plan or have other limits — you can set
  `session_budget: low` in `project-config.yaml`, and I'll pause more often
  (this is the default for new projects).
- If at some step I start doing the wrong thing — say "stop" directly.
  There will be no sycophancy, and I'll argue on the merits.
```

Another pause.

**Screen 3 — what I need from you:**

```
Before we start — two technical points:

1. MISTRAL_API_KEY — needed for transcribing interview audio (Voxtral STT).
   If you don't have one yet — get it at https://console.mistral.ai/ (Login →
   API Keys → Create new). Copy the key and send it to me here, I'll save it
   to `~/.config/ux-transcribe/.env`. It won't go anywhere external.

2. Documentation — `docs/getting-started.md` (how to work with the system) and
   `AGENT.md` (the full canon, if you're curious technically). You don't have
   to read it right now, I'll point things out along the way.

Ready to start? Say "have a key" and send it, or "no key" — you can work
without audio too, but `06-transcribe` will be unavailable.
```

### Step 2: setting up MISTRAL_API_KEY

Depending on the reply:

- **"here's the key: m_xxx..."** — run `MISTRAL_API_KEY="m_xxx..." bash shared/scripts/setup-mistral.sh`. Show the researcher the script's exit message (or its gist: "ok, valid" / "invalid, try another"). On success — move to Step 3.
- **"haven't gotten one yet"** — briefly remind: console.mistral.ai → Login → API Keys. Once they send it — run the script. Don't block, you can proceed to Step 3 without a key (but note in the future project's `agent-notes.md` that Mistral is not configured).
- **"I don't need audio, I only have transcripts"** — fine, skip the key. Record this in the marker.

Optionally (only if the researcher asked) — mention the other keys:
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GEMINI_API_KEY` — for `coding_mode: external` with large samples (≥10 interviews).
- A key for publishing to the team wiki.
- A key for linking issue-tracker tickets.

By default **you don't need to touch them** — the default `coding_mode: agent` requires no keys.

### Step 3: writing the marker

Create `.system/welcomed-at.txt` (if there's no `.system/` folder in the root of `ux-research-pipeline/` — first `mkdir -p`):

```
welcomed: YYYY-MM-DD HH:MM
system_version: v0.5
mistral_key_configured: true|false|skipped
notes: <one line of free context, e.g. "user is on Claude Pro">
```

This is **not PII**. Do not write the user's name here.

### Step 4: what's next

Ask one of:

```
What do we do next?

(a) A new project right away — I already have a task / meeting recording / guide.
(b) Show me a demo — I'll see the pipeline on a small example, then start my own.
(c) I'll just read the documentation, I'll start a project later.
```

Depending on the reply:
- **(a)** — hand off to `01-brief-intake` (the trigger "researcher describes a task / brings material, but there's no active project" from AGENT.md §5).
- **(b)** — demo mode. **Not yet implemented in v0.5** — say honestly "demo mode is in progress, for now I can show you the pipeline structure from `docs/pipeline-map.md`. Want to see it?" and on "yes" — open and walk through `docs/pipeline-map.md`.
- **(c)** — open `docs/getting-started.md` and answer questions. Don't try to "accidentally" pull them into work.

## DoD

- [ ] The three screens are shown **sequentially**, with pauses for reaction (not all at once as a list).
- [ ] `MISTRAL_API_KEY` is either configured via `setup-mistral.sh`, or "skipping" is explicitly recorded.
- [ ] `.system/welcomed-at.txt` is created.
- [ ] Control is handed off either to 01-brief-intake (a), or to `docs/pipeline-map.md` (b/c).

## Failure modes

- **The marker already exists, but the researcher still asked "how does it work".** Don't run 00-welcome again — open `docs/getting-started.md` and answer specifically.
- **The researcher gives the task + key + everything in their very first message.** Don't run the 3 screens sequentially — compress into one paragraph: "got the task, saving the key, starting". Create the marker anyway.
- **MISTRAL_API_KEY is invalid (`setup-mistral.sh` exit 1).** Say directly: "the key didn't pass validation against api.mistral.ai/v1/models. Possibly a typo or the key expired. Try again?" Don't write the marker `mistral_key_configured: true`, leave it `false` or `skipped`.
- **No network for validation.** `setup-mistral.sh` exit 3 — the key is written but not validated. Marker `mistral_key_configured: pending_validation`. On the first real `06-transcribe` call it will be validated in live conditions.

## Mode behavior

- **assistive** (default): three screens sequentially, pauses between them, wait for reaction.
- **autonomous**: running 00-welcome in autonomous mode makes no sense — it's about the human first contact. If someone really wants an autonomous welcome — run it in a single pass without pauses, and at the end say "onboarding technically done, but I recommend reading `docs/getting-started.md` yourself".

## What it does NOT do

- Doesn't create a research project. That's the job of `01-brief-intake` (via the AGENT.md §5 trigger).
- Doesn't teach in-depth interview methodology. That's the job of `docs/getting-started.md` and the team's educational resources.
- Doesn't request the user's PII (name, email, phone). The email is visible from the Cowork session, no need to duplicate it.
- Doesn't offer to choose a "work mode assistive/autonomous" — that's decided in `project-config.yaml` at the level of a specific project.

## After the pass — mandatory

No lessons-extraction. This is onboarding, not an analytical skill.

If during the welcome the researcher asked "how does this thing X work?" — don't dig into details in this skill, answer specifically and offer to open `getting-started.md` or the relevant SKILL.md. 00-welcome should be **short** — dragging it out kills its purpose.
