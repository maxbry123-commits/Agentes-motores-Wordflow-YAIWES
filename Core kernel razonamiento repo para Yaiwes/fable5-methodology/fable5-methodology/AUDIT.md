# Enforcement Audit

The collection is a set of instructions. Instructions decay: context resets, the next model is
weaker, goodwill can't be assumed. This audit asks one question of every rule — **"which file
enforces this tomorrow?"** — and classifies each into the one mechanism that actually holds it
up when nobody is being careful.

> **Schema verification (self-applied research-and-verification rule).** Before writing any
> Claude Code config in this task, the hooks, subagent-frontmatter, and settings schemas were
> verified against the official docs at code.claude.com (redirected from docs.claude.com),
> fetched 2026-07-06 — not written from memory. Verified facts used below: hook events
> `PreToolUse/PostToolUse/Stop/PreCompact/SessionStart/SessionEnd` are current; `PreToolUse`
> denies via `hookSpecificOutput.permissionDecision:"deny"`+`permissionDecisionReason` or exit
> 2; `Stop` blocks via `decision:"block"`+`reason` or exit 2; `SessionStart` injects context
> via stdout; subagent frontmatter requires only `name`+`description`, `model` defaults to
> `inherit`, `tools` is comma-separated; `${CLAUDE_PROJECT_DIR}` is the project-root env var.

## The five classes

- **HOOK** — deterministically enforceable at a lifecycle event. A script decides; the model
  cannot forget it. Strongest.
- **AGENT** — delegated to a subagent with a strict contract, often gaining independence (a
  reviewer that never saw the reasoning).
- **CONTEXT** — must stay always-loaded in CLAUDE.md because it shapes every decision and no
  hook can capture judgement. Only as strong as the model's compliance — so reserved for what
  genuinely can't be mechanized.
- **EVAL** — a quality bar only checkable by testing outputs against a fixture; the regression
  net for behaviours that are judgement, not syntax.
- **WISHFUL** — not enforceable as written. Must be rewritten into one of the above or flagged
  honestly. **Goal of this audit: zero WISHFUL without an explicit reason.**

Most rules get a **primary** enforcer plus backups — defence in depth. The primary is what
holds when everything else fails.

---

## Prime Directives (PLAYBOOK §0 / CLAUDE.md block A)

| # | Rule | Primary | Backups | Enforcement file |
|---|------|---------|---------|------------------|
| 1 | No success claim without evidence | HOOK | EVAL, CONTEXT | hooks/delivery-gate.sh (Stop); evals/ ; CLAUDE.md A1 |
| 2 | Read before you write | CONTEXT | AGENT, EVAL | CLAUDE.md A2; qa-verifier re-reads; eval-05 |
| 3 | Re-read request before delivering | CONTEXT | EVAL, AGENT | CLAUDE.md A3; evals/ ; code-reviewer |
| 4 | Never silently drop a requirement | EVAL | AGENT, CONTEXT | evals/eval-03; code-reviewer.md; CLAUDE.md A4 |
| 5 | Reproduce before you fix | CONTEXT | EVAL | CLAUDE.md A5; evals/eval-04 |
| 6 | One hypothesis / one change at a time | CONTEXT | — | CLAUDE.md A6 (judgement; not mechanizable) |
| 7 | 3 failed attempts → stop & re-plan | CONTEXT | HOOK(partial) | CLAUDE.md A7; evidence.log makes loops visible |
| 8 | State assumptions; ask by reversibility | CONTEXT | EVAL | CLAUDE.md A8; evals/eval-01 |
| 9 | Smallest change; no gold-plating | AGENT | EVAL, CONTEXT | code-reviewer.md; evals/eval-05; CLAUDE.md A9 |
| 10 | Match the codebase | CONTEXT | AGENT, EVAL | CLAUDE.md A10; code-reviewer.md |
| 11 | Distinguish "I know" from "I infer" | CONTEXT | AGENT | CLAUDE.md A11; research-scout.md |
| 12 | Gate destructive / outward actions | **HOOK** | CONTEXT | **hooks/pre-tool-guard.py (PreToolUse)**; CLAUDE.md A12 |
| 13 | Validate at trust boundaries | EVAL | AGENT | evals/ ; code-reviewer safety pass |
| 14 | Verify each unit before the next | **HOOK** | CONTEXT | **hooks/post-edit-verify.sh (PostToolUse)**; CLAUDE.md A14 |
| 15 | Report failures plainly | CONTEXT | EVAL | CLAUDE.md A15; evals/ |

## Integrity Rules (INTEGRITY.md / CLAUDE.md block B)

| # | Rule | Primary | Backups | Enforcement file |
|---|------|---------|---------|------------------|
| I-1 | No "tests pass" without a run | **HOOK** | EVAL | **hooks/delivery-gate.sh** (blocks Stop if src changed but no test/build in evidence.log) |
| I-2 | No fabricated output/contents/API | EVAL | AGENT, CONTEXT | evals/eval-02; qa-verifier (evidence = real output); research-scout |
| I-3 | Never weaken/skip/delete a failing test | AGENT | HOOK(augmentable), EVAL | code-reviewer.md (hunts `.skip`/loosened asserts); post-edit-verify can be extended to flag test-file skips |
| I-4 | No silent requirement downgrade | EVAL | AGENT | evals/eval-03; code-reviewer.md |
| I-5 | Report failures & partials honestly | EVAL | CONTEXT | evals/ ; CLAUDE.md B5 |
| I-6 | Destructive cmds need confirmation | **HOOK** | CONTEXT | **hooks/pre-tool-guard.py** (deny-with-reason) |
| I-7 | No out-of-scope file edits | AGENT | HOOK(log), EVAL | code-reviewer.md; hooks/evidence-log.sh records every edit target; evals/eval-05 |
| I-8 | No secrets committed | **HOOK** | CONTEXT | **hooks/pre-tool-guard.py** (scans `git commit`/`git add` for secrets); settings deny Read(.env) already present |
| I-9 | Uncertain → stop and ask | CONTEXT | — | CLAUDE.md B9 (judgement) |
| I-10 | No fake progress (stubs as done) | EVAL | AGENT | evals/ ; code-reviewer.md (hunts stubs) |

## Playbook sections → skills (PLAYBOOK §1–§14)

| Section / skill | Primary | Enforcement file |
|---|---|---|
| §1 Task comprehension / task-planning | CONTEXT | skills/task-planning; CLAUDE.md D |
| §2 Planning & decomposition | CONTEXT | skills/task-planning |
| §3 Architecture / architecture-decisions | CONTEXT | skills/architecture-decisions |
| §4 Coding standards / implementation-standards | CONTEXT+EVAL | skills/implementation-standards; stacks/*; post-edit-verify (lint) |
| §5 Debugging / debugging-methodology, legacy-debugging | CONTEXT | skills/debugging-methodology, legacy-debugging |
| §6 Verification & self-review | **HOOK+AGENT+EVAL** | hooks/delivery-gate.sh; agents/qa-verifier.md; evals/ |
| §7 Course correction | CONTEXT | skills/course-correction (3-strike surfaced by evidence.log) |
| §8 Uncertainty | CONTEXT | skills/uncertainty-management |
| §9 Large deliverables / incremental-delivery | CONTEXT+HOOK | skills/incremental-delivery; pre-compact-handoff.sh |
| §10 Communication of results | CONTEXT | CLAUDE.md; skills/verification-and-review |
| §11 Anti-patterns | EVAL | evals/ (each anti-pattern → an eval) |
| §12 Non-transferable limits | CONTEXT | CLAUDE.md F |
| §13 Reasoning protocol / structured-reasoning | CONTEXT | skills/structured-reasoning, extended-problem-solving |
| §14 Knowledge currency / research-and-verification | **AGENT** | agents/research-scout.md; skills/research-and-verification |
| §15 Difference layer (hard kernel, negative space, name-the-problem, premise check, precision, knowing→generating) | CONTEXT | skills/problem-framing; PLAYBOOK §15; eval-01 (premise/ambiguity) as partial EVAL backup |
| §15.2/15.5/15.7 predict-then-compare, information-gain, blast radius | CONTEXT | skills/predictive-execution; PLAYBOOK §15; eval-04 (regression trap) exercises blast-radius failure as EVAL backup |
| §16.1 Context economy (altitude, delegation, externalize, degradation signals) | CONTEXT | skills/context-economy; PLAYBOOK §16.1; partially HOOK-backed (session-loader + pre-compact-handoff keep notes current) |
| §16.2 / I-11 Untrusted content is data, not instructions | CONTEXT | INTEGRITY.md I-11; CLAUDE.md B11; PLAYBOOK §16.2 — judgement rule; a future PostToolUse content-scan hook is the eventual HOOK upgrade |
| §17.1 Combination/retrieval (constraint interactions missed despite storage) | **AGENT+EVAL** | skills/self-consistency-check (pairwise sweep + fresh-context cold read + N-version divergence); PLAYBOOK §17.1 — the cold read delegates to a subagent, the structural fix |
| §17.2 Existence≠fidelity of judgment artifacts | CONTEXT+AGENT | PLAYBOOK §17.2 doctrine; fidelity routed to code-reviewer / self-consistency-check; hooks honestly labeled below (STATE vs FLOOR) |
| §17.3 Regressive token tax / right-sizing | CONTEXT | PLAYBOOK §17.3 effort tiers; CLAUDE.md E; load-on-demand skills are the structural mitigation |
| §17.4 Net-benefit-over-baseline (the meta-test) | **EVAL** | evals/ab-harness/ (score-ab.sh + protocol) — the only test that can falsify the whole collection; not yet run head-to-head |

### Gate fidelity — STATE vs FLOOR (answering §17.2 honestly)

A hook can enforce **verifiable state** or merely **existence**; conflating them is dishonest.
Labeled explicitly so a passed gate is never mistaken for a quality signal:

| Hook check | Kind | What a pass actually proves |
|---|---|---|
| pre-tool-guard (command patterns, staged-diff secret scan) | **STATE** | the command is/ isn't in the denied set — fully verifiable |
| delivery-gate: "a verify ran since the last code edit" | **STATE** | a test/build/lint command was actually logged after the last code edit |
| post-edit-verify: lint/parse of the touched file | **STATE** | the file passes the fast checker (or a test-file gained a skip marker) |
| delivery-gate: "WORKING_NOTES.md exists" | **FLOOR** | only that the file is present — NOT that its contents are faithful or useful |

The FLOOR check is deliberately not upgraded to fake a fidelity check (that would be theater).
Fidelity of judgment artifacts (notes, plans, assumption logs) is checked by an AGENT that never
saw the reasoning (code-reviewer, self-consistency-check), never by a hook.
| verification-loop skill | **HOOK** | hooks/post-edit-verify.sh |
| session-state-management skill | **HOOK** | hooks/pre-compact-handoff.sh + hooks/session-loader.sh |
| git-discipline skill | **HOOK** | hooks/pre-tool-guard.py |
| code-review skill | **AGENT** | agents/code-reviewer.md |
| security-review skill | AGENT+EVAL | agents/code-reviewer.md (safety pass); evals/ |
| safe-refactoring / dependency-changes / performance-optimization | CONTEXT | respective skills |
| Operational memory (this task) | **HOOK+CONTEXT** | MEMORY.md; hooks/session-loader.sh (injects last 3); CLAUDE.md E |

---

## Gaps found in the current `~/.claude/` setup

Inspected 2026-07-06. What exists, and what's missing against this collection:

1. **PreToolUse guard exists but is narrower than the collection requires.** `hooks/guard-bash.py`
   blocks only *catastrophic* commands (mkfs, dd-to-disk, fork bomb, rm of root/home). It
   deliberately does NOT block force-push, history rewrite, `DROP TABLE`, mass chmod, or
   `curl|sh` — which Prime Directive 12 / Integrity I-6 require gating. **Gap:** the softer-but-
   still-destructive tier is unenforced. → `hooks/pre-tool-guard.py` (this task) covers it.
2. **No secret-scan before commit.** Integrity I-8 relies on the model remembering. Read(.env)
   is denied in settings, but nothing stops `git add`/`git commit` of a secret in tracked code.
   **Gap.** → folded into `hooks/pre-tool-guard.py`.
3. **No post-edit verification.** `format-after-edit.sh` formats but does not lint/type-check
   or feed failures back. Prime Directive 14 / verification-loop are unenforced mechanically.
   **Gap.** → `hooks/post-edit-verify.sh`.
4. **No delivery gate.** Nothing blocks a "done" that never ran tests. Prime Directive 1 /
   Integrity I-1 are pure goodwill today. **Biggest gap.** → `hooks/delivery-gate.sh` (Stop).
5. **No evidence log.** There is no objective record of what ran, so neither a gate nor MEMORY
   can check anything. **Gap.** → `hooks/evidence-log.sh`.
6. **No pre-compact handoff.** Existing session hooks may run at session-end/stop, but nothing
   snapshots task/plan/next-step into WORKING_NOTES.md before compaction. session-state-management
   is unenforced. **Gap.** → `hooks/pre-compact-handoff.sh`.
7. **SessionStart shows the conversation-log reminder only.** It does not surface git status,
   WORKING_NOTES.md, or recent MEMORY.md entries, so sessions start under-oriented. **Gap.** →
   `hooks/session-loader.sh`.
8. **30 agents, none contracted for this loop.** The existing roster (code-reviewer,
   security-reviewer, tdd-guide, etc.) is broad and prose-heavy; none is the strict
   builder→qa-verifier→reviewer→scout contract this collection needs, and none *refuses* on
   missing acceptance criteria. **Gap.** → 4 contracted agents in agents/ (this task).
9. **No evals at all.** No regression net for judgement-level rules. Every EVAL row above is
   currently WISHFUL. **Gap.** → evals/ (this task).
10. **No operational memory.** Recurring failures aren't captured to a patch-tracking ledger.
    **Gap.** → MEMORY.md + the memory rule (this task).

---

## What this task creates (forward references for B–F)

Every HOOK, AGENT, and EVAL cell above resolves to a file created in this task:

- **HOOKs** → `hooks/pre-tool-guard.py`, `hooks/post-edit-verify.sh`, `hooks/evidence-log.sh`,
  `hooks/delivery-gate.sh`, `hooks/pre-compact-handoff.sh`, `hooks/session-loader.sh` +
  `settings-hooks.json` (registration).
- **AGENTs** → `agents/builder.md`, `agents/qa-verifier.md`, `agents/code-reviewer.md`,
  `agents/research-scout.md` + Orchestration section in CLAUDE.md.
- **EVALs** → `evals/README.md`, `evals/TEMPLATE/`, and `evals/eval-01`..`eval-05`.
- **MEMORY** → `MEMORY.md` + the memory rule in CLAUDE.md.

A post-implementation re-classification pass (Deliverable F) re-answers "which file enforces
this tomorrow?" and confirms no row remains WISHFUL without a stated reason. The two rows that
stay CONTEXT-only by nature (Directive 6 one-change-at-a-time, I-9 stop-and-ask) are judgement
calls no script can make; they are flagged as such, not left as accidental gaps.

---

## Post-implementation re-classification (completed this task)

Re-answering "which file enforces this tomorrow?" now that the files exist. Every HOOK, AGENT,
and EVAL cell above resolves to a real, tested file:

**HOOKs (all written + tested, exit codes verified against the schema):**
- `hooks/pre-tool-guard.py` — Directive 12, I-6, I-8. Tested: force-push/DROP/curl-sh/rm-outside
  → deny(exit 2); normal push/rm, force-with-lease, malformed JSON → allow(exit 0).
- `hooks/post-edit-verify.sh` — Directive 14, verification-loop, I-3. Tested: bad JSON → exit 2
  clean error; test-file skip marker → flagged.
- `hooks/evidence-log.sh` — the objective record. Tested: edit/verify lines classified + logged.
- `hooks/delivery-gate.sh` — Directive 1, I-1. Tested: edit-after-verify → block JSON;
  verify-after-edit + notes → allow; `stop_hook_active` → allow (loop guard).
- `hooks/pre-compact-handoff.sh` — session-state-management. Tested: writes handoff block.
- `hooks/session-loader.sh` — orientation + memory surfacing. Tested: emits git/notes/memory.
- `hooks/settings-hooks.json` — registration snippet (schema-verified 2026-07-06).

**AGENTs (contracts written, refuse-conditions explicit):** `agents/builder.md`,
`agents/qa-verifier.md`, `agents/code-reviewer.md`, `agents/research-scout.md`. Wired via
CLAUDE.md §D (builder → qa-verifier → code-reviewer chain; no acceptance without qa evidence).

**EVALs (written; mechanical checks validated):** `evals/eval-01`..`eval-05` + README + TEMPLATE.
eval-04 and eval-05 checks validated across correct/naive/cheat paths; eval-01/02/03 checks
grep + rubric to qa-verifier.

**MEMORY:** `MEMORY.md` (3 seed rows, each names a patched file) + rule in CLAUDE.md §G.

### Final WISHFUL count: 0 unexplained.

Two rules remain CONTEXT-only, by nature, with stated reason — not accidental gaps:
- **Directive 6** (one hypothesis/change at a time) — a judgement about reasoning cadence; no
  lifecycle event exposes it. Backed by evidence-log making rapid unverified edits visible.
- **Integrity I-9** (uncertain → stop and ask) — the trigger is internal hesitation; no script
  observes it. Backed by pre-tool-guard (the destructive subset of "unsafe" IS mechanized).

Everything else has a primary mechanical or agent enforcer. The collection now enforces itself
after a context reset, on a weaker model, with no goodwill assumed.
