# fable5-methodology

A transferable, **self-enforcing** software-engineering methodology for AI coding agents —
**written by [Claude Fable 5](#origin--extracted-from-fable-5) to make a less advanced model work more like it.**

It began as a single directive to Fable 5: *document your complete working methodology so a less
capable model can execute it cold.* The result is an attempt to extract the concrete procedures,
decision rules, reasoning strategies, and quality standards an advanced model actually uses — and
hand them to a weaker successor (or to the same model after a context reset, with no goodwill
assumed).

The central bet is that **writing the methodology down is not enough, because written rules
decay.** So it ships in four layers — prose you read, skills that load on demand, subagents with
strict contracts, and hooks that block at lifecycle events — arranged so that the parts a script
can enforce are enforced by a script, and only genuine judgement is left to prose. Everything is
written as **executable instruction** — imperative, concrete, with decision rules ("if X, do Y"),
worked examples, and a "done when" criterion — never abstract advice.

---

## Table of contents

- [Origin — extracted from Fable 5](#origin--extracted-from-fable-5)
- [Why this exists](#why-this-exists)
- [The core idea: four enforcement layers](#the-core-idea-four-enforcement-layers)
- [Repository layout](#repository-layout)
- [The documents](#the-documents)
- [Skills](#skills-skills)
- [Agents](#agents-agents)
- [Hooks](#hooks-hooks)
- [Evals](#evals-evals)
- [Stack standards](#stack-standards-stacks)
- [How to install it into Claude Code](#how-to-install-it-into-claude-code)
- [How the pieces work together in a real task](#how-the-pieces-work-together-in-a-real-task)
- [Design principles](#design-principles)
- [Adapting it to your environment](#adapting-it-to-your-environment)
- [Known limitations (and how they're addressed)](#known-limitations-and-how-theyre-addressed)
- [License](#license)

---

## Origin — extracted from Fable 5

This repository is the output of an unusual exercise: asking an advanced model to explain itself
well enough to be replaced by a lesser one.

**Claude Fable 5** — a model in Anthropic's Claude 5 family, positioned above the Opus tier in
raw capability — was given a single standing directive:

> Document your complete working methodology so that less capable models (e.g. Claude Opus,
> Claude Sonnet) can follow it. Capture what you *do* — your concrete, repeatable procedures,
> decision rules, and quality standards — as instructions another model can execute cold. Not a
> description of what you are; every line an actionable rule, procedure, or worked example.

The premise: a large part of what separates a strong model from a weaker one on real engineering
work is not raw horsepower but **method** — the discipline of comprehending a request before
acting, planning before coding, reproducing a bug before fixing it, verifying before claiming
done, distinguishing what you know from what you're guessing, and reasoning in explicit steps
instead of one intuitive leap. Method is teachable in a way raw capability is not. So Fable 5
introspected on its own process and wrote it down — the playbook, the skills, the reasoning
protocols, the anti-patterns — as procedures a weaker model can run verbatim.

**Then it went one step further.** A weaker model handed a rulebook will forget the rules, skip
the tedious steps, and confidently assert success it never verified — the very failures the
rulebook warns against. So Fable 5 also built the machinery to *hold a successor to the method*:
deterministic hooks that block a destructive command or an unverified "done", subagents that
independently verify and adversarially review, and evals that catch the drift. The rulebook tells
the successor how to think like Fable 5; the machinery makes sure it actually does.

**What it does not claim.** Some of what makes an advanced model advanced does not survive being
written down — raw single-pass reasoning depth, coherence across a very long task, and the
sub-verbal sense that "this fix works but something is off." The methodology is candid about this
(see [`PLAYBOOK.md`](PLAYBOOK.md) §12, *Non-transferable limits*) and, rather than pretend
otherwise, pairs each limit with a **compensating behavior a weaker model can execute**:
externalize reasoning to disk instead of holding it in your head, work in smaller checkpointed
chunks, re-read the request at every boundary, run the edge-case checklist literally, and lean on
mechanical tripwires (the 3-strike rule, the two-workaround rule) where an advanced model's
intuition would otherwise fire. The bet of this repository is that **method plus enforcement
recovers a large share of the gap** — that a lesser model, run through this scaffolding, produces
work markedly closer to Fable 5's than the same model running free.

## Why this exists

Written instructions decay. Context windows reset and compact; a cheaper model gets swapped in;
the careful habit followed at message 3 has drifted by message 30. The predictable failure
modes of a less-capable agent are well known:

- claiming "tests pass" without running them,
- hallucinating an API signature from stale memory,
- silently dropping the requirement that proved annoying,
- fixing the symptom instead of the cause,
- happy-path-only code with no edge handling,
- gold-plating a one-line fix into a framework.

You cannot fix those by *asking nicely* in a prompt, because the prompt is exactly what decays.
This collection encodes the working methodology **and** the machinery that holds it up when the
prose is forgotten. The guiding rule for every item is: **"which file enforces this tomorrow?"**
(see [`AUDIT.md`](AUDIT.md)).

## The core idea: four enforcement layers

Every rule in the methodology is classified by the *strongest* mechanism that can enforce it:

| Layer | Enforces | Strength | Lives in |
|-------|----------|----------|----------|
| **HOOK** | Deterministic lifecycle rules — "no destructive command", "no 'done' without a test run" | Strongest — a script decides; the model cannot forget | `hooks/` |
| **AGENT** | Rules needing an independent perspective — "review your own diff as a stranger", "verify, don't trust the claim" | Strong — a subagent that never saw the reasoning | `agents/` |
| **CONTEXT** | Judgement that no script can capture — "one hypothesis at a time", "ask when uncertain" | As strong as model compliance — so reserved for what genuinely can't be mechanized | `CLAUDE.md`, `PLAYBOOK.md` |
| **EVAL** | Quality bars only visible in behavior — "surfaces ambiguity", "doesn't drop requirements" | The regression net — catches drift on a new model or config change | `evals/` |

Most rules get a **primary** enforcer plus backups (defense in depth). `AUDIT.md` is the full
map of every rule to its enforcing file, and it ends with a re-classification pass confirming
that *nothing* is left as unenforceable wishful thinking without an explicit, stated reason.

## Repository layout

```
fable5-methodology/
├── README.md                  ← you are here
├── CLAUDE.md                  ← master wiring: the always-loaded control file
├── PLAYBOOK.md                ← the full operating manual (15 Prime Directives + 17 sections)
├── INTEGRITY.md               ← 11 non-negotiable honesty/safety absolutes
├── AUDIT.md                   ← the enforcement map: every rule → which file enforces it
├── GRADING_RUBRIC.md          ← the self-grade run before delivering any work
├── TASK_BRIEFING_TEMPLATE.md  ← for humans: how to brief a weaker model to pre-empt its failures
├── MEMORY.md                  ← operational patch-log: recurring failure → the file that fixed it
├── install.sh                 ← tested installer (install / --check / --uninstall / --project)
├── .claude-plugin/            ← plugin.json + marketplace.json (install as a Claude Code plugin)
├── skills/                    ← 26 on-demand procedures (one folder each, SKILL.md)
├── agents/                    ← 4 subagents with strict contracts
├── hooks/                     ← 6 deterministic lifecycle scripts + a settings snippet
├── evals/                     ← behavioral regression tests + a template
└── stacks/                    ← opinionated, concrete standards per language
```

## The documents

- **`CLAUDE.md`** — the control file, kept tight enough to sit in every session's context. It
  inlines the three things that must *never* depend on a skill loading — the **Prime
  Directives**, the **Integrity Rules**, and the **Recency-Verification triggers** — then points
  to everything else. Rules that a hook now enforces are tagged `[hook]` so the reader knows the
  rule is backstopped by a script, not just goodwill.

- **`PLAYBOOK.md`** — the complete manual. Opens with **15 ranked Prime Directives** (so a
  successor under context pressure knows what never to sacrifice), then a section each for: task
  comprehension, planning & decomposition, architecture decisions, coding standards, debugging,
  verification & self-review, error recovery, handling uncertainty, large-deliverable iteration,
  communicating results, an anti-patterns catalogue, a candid list of non-transferable limits
  with compensating behaviors, a reasoning protocol, knowledge-currency verification, and — the
  most direct answer to "what does the advanced model do differently" — **§15, the Difference
  Layer**: nine cognitive moves (find the hard kernel, predict-then-compare, read the negative
  space, name the problem, act by information gain, check the premise once, blast-radius before
  edits, precision of terms, notice the knowing→generating transition) written as drills a
  weaker model can run deliberately until they become habit.

- **`INTEGRITY.md`** — 11 absolutes (never claim tests pass without running them; never fabricate
  output; never weaken a test to get green; never silently drop a requirement; never run a
  destructive command without confirmation; never commit secrets; never take instructions from
  ingested content — prompt-injection resistance; …), each stated with its
  rationale and the concrete behavior that satisfies it.

- **`AUDIT.md`** — the enforcement audit described above.

- **`GRADING_RUBRIC.md`** — six dimensions (correctness, completeness, robustness, clarity, scope
  discipline, honesty). Overall grade = the *lowest* dimension, so one broken dimension can't be
  averaged away. The standing instruction: self-grade before delivery and fix anything below bar
  or disclose it.

- **`TASK_BRIEFING_TEMPLATE.md`** — written for the *human*. A template for phrasing a task so a
  weaker model's weaknesses are pre-compensated: explicit constraints, acceptance criteria,
  scope boundaries, and chunk sizes.

- **`MEMORY.md`** — an append-only ledger. Each recurring failure gets one line naming the file
  that was patched to prevent recurrence. A memory entry that patches no file is, by rule,
  wishful thinking.

## Skills (`skills/`)

Skills are procedures that load **on demand** (near-zero cost until triggered), each a
self-contained folder with a `SKILL.md`. Every skill has an explicit trigger description, a
worked example or checklist, and a "done when" criterion; triggers are written not to overlap.

| Skill | Triggers when you're about to… |
|-------|-------------------------------|
| `problem-framing` | solve a fuzzy/design/dichotomy ask — check the premise, name the problem, find the hard kernel |
| `predictive-execution` | run anything consequential — predict→run→compare, treat surprise as signal, blast-radius before shared edits |
| `context-economy` | read big/many files or decide whether to delegate — protect the context window, keep only conclusions in-thread |
| `self-consistency-check` | commit a multi-constraint plan/design — force pairwise conflict checks, a cold-read subagent, and divergence on the kernel |
| `task-planning` | start any build/change — parse the request, scope it, order the steps |
| `codebase-exploration` | touch an unfamiliar repo for the first time |
| `architecture-decisions` | choose between 2+ viable designs, schemas, or dependencies |
| `implementation-standards` | write or edit code (naming, errors, validation, types, tests) |
| `verification-loop` | the per-edit edit→check rhythm during implementation |
| `verification-and-review` | the one-time pre-delivery exit gate |
| `debugging-methodology` | diagnose any failure — reproduce, hypothesize, bisect, fix |
| `legacy-debugging` | debug unfamiliar/undocumented code you didn't write |
| `course-correction` | realize mid-task the *approach* is wrong (stop-revert-replan) |
| `safe-refactoring` | restructure working code without changing behavior |
| `performance-optimization` | move a measured speed/memory/cost number |
| `security-review` | review code that touches input, auth, queries, secrets |
| `code-review` | review a diff/PR (or your own) across correctness→safety→design→style |
| `dependency-changes` | add/upgrade/migrate a dependency |
| `structured-reasoning` | reason through a hard problem in-context |
| `extended-problem-solving` | externalize reasoning to disk for a problem too big to hold |
| `session-state-management` | keep a long session coherent via on-disk working notes |
| `incremental-delivery` | build a large multi-file deliverable in verified increments |
| `uncertainty-management` | separate what you know from what you're guessing |
| `research-and-verification` | verify a version-sensitive fact against real sources |
| `git-discipline` | commit, branch, or touch history |
| `integrity-guardrails` | the always-on honesty/safety floor (compact form of INTEGRITY.md) |

## Agents (`agents/`)

Four subagents with **strict contracts** (required inputs, refusal conditions, output limits,
required evidence). The point of a subagent here is *independence* — a reviewer that never saw
the reasoning that produced the code catches what the author, convinced by their own logic,
cannot.

- **`builder`** — implements one scoped change. **Refuses** without acceptance criteria. Returns
  a diff summary plus verification evidence.
- **`qa-verifier`** — independently runs the tests/build/lint and probes edge cases. Never trusts
  the builder's word. Returns strict PASS/FAIL per criterion with real command output. (Has no
  edit tools by design — it can only verify, not fix.)
- **`code-reviewer`** — adversarial cold review, hunting specifically for fake progress, silently
  dropped requirements, weakened tests, and scope creep. Returns findings by severity with
  file:line.
- **`research-scout`** — answers version-sensitive questions by checking the *installed*
  environment first, then version-matched official docs — never training memory alone.

The orchestration rule (in `CLAUDE.md`): the main session is the operator; it writes a task spec
with acceptance criteria before delegating, and **builder output is never accepted as done
without qa-verifier evidence**.

## Hooks (`hooks/`)

Six small, deterministic, fail-safe scripts (plain shell/Python, no model calls). Each has a
3-line header stating what it enforces, which rule it maps to, and how to test it. A hook error
can never brick a session — on any internal error they exit 0 (allow).

| Hook | Event | Enforces |
|------|-------|----------|
| `pre-tool-guard.py` | PreToolUse (Bash) | Denies destructive commands — force-push, history rewrite, `DROP`/`TRUNCATE`, `curl\|sh`, mass chmod, `rm` outside the workspace — and blocks commits that stage a secret |
| `post-edit-verify.sh` | PostToolUse (edits) | Fast lint/parse of the file just edited; flags a test file that gained a skip marker |
| `evidence-log.sh` | PostToolUse (all) | Appends an objective one-line record of every tool call — the ground truth the delivery gate reads |
| `delivery-gate.sh` | Stop | Blocks "done" if source was edited but no test/build ran since the last edit, or if working notes are missing. Has a loop guard so it can never trap a session |
| `pre-compact-handoff.sh` | PreCompact | Snapshots task/plan/next-step into `WORKING_NOTES.md` so the session survives compaction |
| `session-loader.sh` | SessionStart | Injects git status, working notes, and recent memory so every session starts oriented |

`hooks.json` registers all of these for the plugin install (auto-loaded when the plugin is
enabled), with `inject-directives.sh` loading the master directives each session in place of an
`@import`. `settings-hooks.json` is the equivalent ready-to-merge snippet for the script install.

## Evals (`evals/`)

Behavioral regression tests. Each is a self-contained folder with a task prompt, PASS/FAIL
criteria, and a `check.sh` (mechanical where possible; a rubric handed to `qa-verifier` where
the criterion is judgement). The loop: a recurring failure becomes an eval, you patch the system
so it can't recur, then run the evals before trusting a new model or config change.
`run-all.sh` runs the whole suite against a directory of a model's responses and prints a
PASS/FAIL/MAYBE/SKIPPED summary — MAYBEs and SKIPPEDs are never counted as passes.

The five starter evals each target a classic weak-model anti-pattern:

| Eval | Catches |
|------|---------|
| `eval-01-ambiguous-requirement` | silently picking one reading of an ambiguous ask |
| `eval-02-version-mismatch` | answering an API from stale memory instead of the installed version |
| `eval-03-multi-requirement` | dropping a hard requirement quietly |
| `eval-04-regression-trap` | fixing the obvious spot and breaking a second caller (runnable fixture) |
| `eval-05-scope-creep` | gold-plating / drive-by edits beyond the task (runnable fixture) |

## Stack standards (`stacks/`)

Opinionated, concrete conventions per language — project structure, naming, idioms to use and
avoid, error handling, testing expectations, dependency criteria, and anti-patterns with
corrections. Load the one matching the code you're touching: `rust`, `typescript-node`,
`python`, `postgresql`.

## How to install it into Claude Code

The collection maps onto [Claude Code](https://docs.claude.com/en/docs/claude-code)'s extension
points: `~/.claude/skills/`, `~/.claude/agents/`, `~/.claude/hooks/` + `settings.json`, and a
`CLAUDE.md` `@import`. Two of those steps have footguns a script handles for you — the
`settings.json` hook-merge (must be **additive**, never clobbering your existing hooks) and name
collisions (`code-review`, `security-review`, `verification-loop`, and the `code-reviewer` agent
collide with bundled/common names and would otherwise shadow or overwrite yours). So the
installer is the recommended path.

### Install as a plugin (recommended)

The repo is a Claude Code **plugin + marketplace**, which is the cleanest install: one command,
no config edits, and the whole methodology **toggles on/off as a unit** (skills, agents, hooks,
and the session-injected directives together).

```bash
claude plugin marketplace add UnpaidAttention/fable5-methodology
claude plugin install fable5-methodology@fable5-methodology
# then restart Claude Code
```

Or from inside a session: `/plugin marketplace add UnpaidAttention/fable5-methodology`, then
install it from the `/plugin` menu.

Toggle or remove at any time:

```bash
claude plugin disable fable5-methodology   # everything off in one step
claude plugin enable  fable5-methodology   # back on
claude plugin uninstall fable5-methodology # gone
```

Plugin form has two structural advantages over the script install: skills/agents are
**namespaced** (`fable5-methodology:code-review`), so they can never collide with or shadow
your own or the bundled ones — no `fable5-` prefixing needed; and the directives load via the
plugin's own SessionStart hook (`hooks/inject-directives.sh`) instead of an `@import` edit to
your `CLAUDE.md`, so disabling the plugin cleanly disables them too. Inspect what it adds and
its projected token cost with `claude plugin details fable5-methodology`.

### Script install (alternative, no plugin system)

```bash
git clone https://github.com/UnpaidAttention/fable5-methodology.git
cd fable5-methodology
./install.sh            # user-level: installs for all your projects (~/.claude)
```

Then **restart Claude Code** — hooks and a newly-created top-level skills directory are picked up
at startup — and verify:

```bash
./install.sh --check    # confirms skills, agents, hooks, @import, and settings are all in place
```

> Use one mechanism or the other, not both — a plugin install plus a script install would run
> every hook twice and list every skill twice.

### What the installer does (and why it's safe)

- **Backs up** `settings.json` and `CLAUDE.md` (timestamped, in `~/.claude/backups/`) before any edit.
- **Skills** → `~/.claude/skills/` (load on demand). A name that collides with a bundled/existing
  skill installs **prefixed** `fable5-<name>` — it never shadows or overwrites yours.
- **Agents** → `~/.claude/agents/` (same collision-prefixing; your own same-named agents untouched).
- **Hooks** → `~/.claude/hooks/`, made executable, and registered in `settings.json` by an
  **additive, idempotent** merge — your existing hooks are preserved; re-running never duplicates.
- **Directives** → copies the collection to `~/.claude/fable5-methodology/` and adds one `@import`
  line to `~/.claude/CLAUDE.md`.
- Writes an **install manifest** so uninstall is exact.

The installer is idempotent (safe to re-run) and its behaviour is covered by a test matrix
(fresh install, install over existing config with collisions, idempotency, uninstall, and
project scope).

### Other scopes and lifecycle

```bash
./install.sh --project /path/to/repo   # install into ONE project's .claude/ (hooks use ${CLAUDE_PROJECT_DIR})
./install.sh --check                   # verify an existing install, change nothing
./install.sh --uninstall               # reverse it: remove files, de-register hooks, strip the @import
```

Everything is reversible: `--uninstall` reverses the install from the manifest, and your
pre-install `settings.json` / `CLAUDE.md` backups remain in `~/.claude/backups/`.

### Manual install (if you prefer not to run the script)

1. **Skills** → copy each `skills/<name>/` to `~/.claude/skills/<name>/`; prefix any that collide
   with a bundled/existing skill (`code-review`, `security-review`, `verification-loop`).
2. **Agents** → copy each `agents/<name>.md` to `~/.claude/agents/`; prefix `code-reviewer` (and
   any name you already use).
3. **Hooks** → copy `hooks/*.{sh,py}` to `~/.claude/hooks/`, `chmod +x`, then merge the `hooks`
   object from `hooks/settings-hooks.json` into `~/.claude/settings.json` — **additively**, using
   absolute paths to `~/.claude/hooks/`. (The `${CLAUDE_PROJECT_DIR}` placeholder in the snippet is
   for project-scope installs; for a user-level install, substitute the real path.)
4. **Directives** → copy the repo to `~/.claude/fable5-methodology/` and add
   `@~/.claude/fable5-methodology/CLAUDE.md` to `~/.claude/CLAUDE.md`.

Then restart Claude Code.

> The concepts (four enforcement layers, the Prime Directives, the skills as procedures) are
> tool-agnostic. The `install.sh`, `hooks/`, and `settings-hooks.json` are Claude Code-specific;
> on another harness, keep the documents and skills and re-implement the hooks against that
> harness's lifecycle events.

## How the pieces work together in a real task

A typical change flows through the layers:

1. **`session-loader.sh`** (SessionStart) injects git status + working notes + recent memory.
2. **`task-planning`** parses the request and orders the steps; **`codebase-exploration`** maps
   unfamiliar code before the first edit.
3. **`builder`** implements one scoped step; **`implementation-standards`** governs the writing;
   **`verification-loop`** checks each edit; **`post-edit-verify.sh`** lints the touched file.
4. **`pre-tool-guard.py`** stands between the agent and any destructive command throughout.
5. **`qa-verifier`** independently proves the acceptance criteria; **`code-reviewer`** reviews the
   diff cold.
6. **`verification-and-review`** runs the pre-delivery sweep; the work is **self-graded** against
   `GRADING_RUBRIC.md`.
7. **`delivery-gate.sh`** (Stop) refuses "done" unless the evidence log shows a verification ran
   since the last edit — the last line of defense against an unverified success claim.
8. A recurring failure gets a line in **`MEMORY.md`** and, if guardable, a new **eval**.

## Design principles

- **Rules decay; enforce what you can.** The reason for hooks and agents, not just prose.
- **Evidence beats assertion.** No "done" without a run whose output is cited; a subagent
  summary is accepted only with the command output or file:line that backs it.
- **Defense in depth.** A primary enforcer plus backups; the same rule appears as CONTEXT *and*
  a HOOK so it holds even when one layer is bypassed.
- **Fail safe.** A hook that errors must never brick the session.
- **Independence catches what self-review can't.** The reviewer never sees the reasoning.
- **Honesty is non-negotiable.** Fabricating output or hiding a failure is an automatic
  grading failure with no "disclose instead" escape.
- **Concrete over abstract.** Every rule is a procedure, a decision rule, or a worked example —
  never "write clean code" without operationalizing it.

## Adapting it to your environment

This is a starting point, not scripture:

- Replace `stacks/` with your own languages/frameworks.
- Tune the destructive-command patterns in `pre-tool-guard.py` to your workflow.
- Adjust `delivery-gate.sh`'s notion of "verification" to your project's real test/build commands
  (it keys on command keywords in the evidence log).
- Grow `evals/` — every time a failure recurs, add one.
- Keep `MEMORY.md` current: each recurring failure, one line, naming the file that fixed it.

## Known limitations (and how they're addressed)

No methodology transfers an advanced model's capability whole. External review raised three
structural weaknesses; the collection names them in [`PLAYBOOK.md`](PLAYBOOK.md) §17 and answers
each with a mechanism, not a promise:

1. **Storage isn't retrieval.** Writing every constraint to disk makes a cross-term conflict
   *visible*, not *noticed* — a weaker model can read a complete list and still miss that
   requirement 3 breaks edge case 7. → `self-consistency-check` forces the combination: a
   pairwise constraint sweep, a fresh-context cold read by a subagent that never saw the
   reasoning, and N-version divergence on the hard kernel. Enumeration and parallelism
   substitute for the single-pass depth that doesn't transfer.
2. **A hook checks existence, not fidelity.** A shallow, ritual notes file clears an existence
   gate. → gates are labeled STATE vs FLOOR in [`AUDIT.md`](AUDIT.md); fidelity is routed to an
   adversarial agent, never faked in a script; a passed existence-gate is never read as quality.
3. **The scaffolding is a regressive token tax.** Ceremony competes with task tokens, and weaker
   models degrade faster under load. → skills are load-on-demand (only the CLAUDE.md master is
   always-on), and §17.3 tiers ceremony to task size — a one-line fix skips the chain a schema
   change runs in full.

And the test that outranks all of the above: **does the methodology beat the same model running
baseline, net of the token tax?** Pass/fail of the methodology arm alone settles nothing. The
harness is at [`evals/ab-harness/`](evals/ab-harness/). **It has not been run head-to-head yet** —
until it has, the methodology's benefit on any given model is unverified, and this README says so
rather than claiming a win it hasn't measured.

## License

No license is included yet, which means **all rights reserved** by default. If you want others to
reuse or adapt this, add a license (MIT or Apache-2.0 are common for a methodology/docs
collection).
