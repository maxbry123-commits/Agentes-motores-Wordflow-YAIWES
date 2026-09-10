# Operational Memory

The ledger of failures that recurred and the system change that stops each from recurring. It
is not a diary — it is a patch log. **Rules (enforced by the memory rule in CLAUDE.md §G):**

1. Every **recurring** failure gets one row (one-off slips don't; recurrence is the trigger).
2. Every row must name the **file that was patched**. A row that patches nothing is WISHFUL —
   a note-to-self that changes no behaviour. If you can't name a file, you haven't fixed it.
3. One line per row. No narrative, no prose paragraphs. If it needs more, it's a design doc,
   not a memory entry.
4. If the fix is a behaviour a script/agent can guard, create an eval and name it in the row.

Columns: **date | failure | root cause | system patch (file) | eval (y/n + name) | next**

The SessionStart hook (`hooks/session-loader.sh`) surfaces the last 3 rows each session, so the
most recent lessons are always in front of the next session.

| date | failure | root cause | system patch (file) | eval (y/n + name) | next |
|------|---------|-----------|---------------------|-------------------|------|
| 2026-07-06 | Claimed "tests pass" in a summary without having run them after the last edit | No mechanical gate on the Stop event; relied on model goodwill | `hooks/delivery-gate.sh` (blocks Stop if src edited but no verify in evidence.log) + `hooks/evidence-log.sh` | n — hook-enforced, no output-eval needed | Watch for models running a stale verify before the last edit; delivery-gate already keys on ordering |
| 2026-07-06 | Emitted a library API call from training memory that didn't match the installed major version | Version-sensitive fact treated as knowledge, not hypothesis; no forced env check | `agents/research-scout.md` (env-first contract) + `skills/research-and-verification/SKILL.md` | y — eval-02-version-mismatch | Add a second version-mismatch eval for a Python (pip) stack once one recurs |
| 2026-07-06 | Delivered 4 of 5 requested items with "implemented the endpoint", the 5th silently dropped | Requirements not enumerated at delivery; reviewer never saw the original list | `agents/code-reviewer.md` (hunts dropped requirements) + delivery discipline in CLAUDE.md | y — eval-03-multi-requirement | If it recurs, add a UserPromptSubmit-logged requirements checklist the delivery gate can diff |
| 2026-07-06 | delivery-gate Stop hook false-fired 3× on docs/config-only turns and on hook edits verified via `bash -n` (not keyword-matched), blocking legitimate stops | Gate keyed on ANY edit incl. `.md`/`.json`; and `evidence-log` verify-classification missed non-keyword verification commands | `hooks/delivery-gate.sh` (gate only on code-file extensions) + `hooks/evidence-log.sh` (recognize bash -n/shellcheck/json.tool/--check/cargo check/go vet/validate as verify) | n — hook-internal logic; validated via 5 scenario tests (docs→allow, code-no-verify→block, code+verify→allow, loop-guard, bash-n→verify) | Add a hook self-test eval if the classifier drifts again |

| 2026-07-06 | External review: methodology solved storage but not retrieval-and-combination (constraint interactions missed despite being written down); existence-gates read as fidelity; uniform ceremony taxed trivial tasks | written-down ≠ noticed; a hook checks existence not quality; no effort tiering | `skills/self-consistency-check` (pairwise sweep + fresh-context cold read + N-version divergence) + PLAYBOOK §17 (effort tiers + gate STATE/FLOOR honesty in AUDIT.md) + `evals/ab-harness/` (score-ab.sh) | y — evals/ab-harness net-benefit A/B | RUN the A/B head-to-head (baseline vs +methodology); until then the benefit is UNVERIFIED — do not claim a win |

<!-- New rows go ABOVE this line, newest last is fine; keep the 3 seeds as format examples until real entries replace them. -->
