# A/B Harness — does the methodology actually beat baseline, net of tokens?

This is the only test that settles whether the methodology is worth anything (PLAYBOOK §17.4).
Everything else in this repo is sound-on-paper until this runs. It measures **the same model,
with the methodology vs. without it**, on the same tasks, and reports the quality delta *net of
the token tax* — because a step can look principled and still lose once its tokens are counted.

**Honest status: this A/B has not been run head-to-head yet.** The harness exists so it can be.
Do not claim the methodology helps a given model until you've run this for that model.

## What it compares

Two arms of the SAME model (e.g. Opus baseline vs Opus + fable5-methodology):

- **baseline** — a clean Claude Code environment: no `@import` of the collection, no fable5
  skills/agents/hooks installed. The model runs free.
- **methodology** — the collection fully installed (`../../install.sh`), so directives load,
  skills/agents are available, and hooks enforce.

Anything else held constant: same model, same tasks, same harness version.

## The task set

Start with the five evals (`../eval-01..05`) — each targets a known weak-model failure. Then add
**real tasks from your own work**, because the eval set is small and synthetic; the token tax
only shows its true cost on realistic tasks. Aim for ≥10 tasks spanning the effort tiers
(§17.3): some Trivial (where the methodology's ceremony should *lose* — that's the point of
measuring), some Complex (where it should win).

## Procedure

1. **Run each task on the baseline arm.** Clean environment. Save the model's full response to
   `runs/<label>/baseline/eval-0N.txt` (prompt-based evals) or the model-edited fixture dir to
   `runs/<label>/baseline/eval-0N/` (fixture evals 04/05). Record output-token count per task.
2. **Run each task on the methodology arm.** Full install. Save to `runs/<label>/methodology/…`
   the same way. Record output-token count (this is higher — that's the tax you're testing).
3. **Record tokens** in `runs/<label>/tokens.tsv` — one row per eval:
   `eval-id <TAB> baseline_tokens <TAB> methodology_tokens`
4. **Score:** `bash score-ab.sh runs/<label>` — runs each eval's own `check.sh` against both
   arms and prints the verdict table + net summary.
5. **Judge the net.** The script reports quality wins/losses and total token overhead; the
   worth-it call is yours (see below).

## Reading the verdict

`score-ab.sh` prints, per eval: baseline PASS/FAIL, methodology PASS/FAIL, tokens each, and a
per-eval outcome:

- **WIN** — methodology PASS where baseline FAIL. The scaffolding earned its tokens here.
- **LOSS** — methodology FAIL where baseline PASS. The scaffolding *hurt* (rare, but if it
  happens, that step is suspect — investigate).
- **TIE** — same verdict both arms. Then the token overhead was pure tax with no quality
  return on that task.

Net summary: `WINS − LOSSES` and total token overhead. The methodology is justified only if:

1. `WINS > LOSSES` (net quality gain), **and**
2. the per-task token overhead on the *Trivial/Small* tasks is acceptable to you — because
   that's the regressive tax, paid on the tasks that needed help least.

If the methodology only wins on Complex tasks and taxes Trivial ones, the correct fix is not to
abandon it but to **tier it** (§17.3): the WIN/TIE split by tier tells you exactly where the
ceremony pays and where to skip it. Prune any step that produces only TIEs at high token cost.

## MAYBE / SKIPPED

Judgement-based evals (01/02/03) may score MAYBE from the mechanical check — those go to
qa-verifier or a human, and are never counted as a WIN without that adjudication. Missing arm
outputs score SKIPPED, never a pass. The net summary reports both counts; a run with many
MAYBEs/SKIPPEDs is not a completed A/B.
