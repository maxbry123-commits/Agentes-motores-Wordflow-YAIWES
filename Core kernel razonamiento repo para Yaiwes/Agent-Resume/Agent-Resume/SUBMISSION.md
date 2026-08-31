# Submissions

## Hermes Agent Challenge (dev.to write track)

Paste-ready post draft below. Word count ~1000.

---

### Title: My agent processed 47 of 100 GitHub issues, then crashed. Here is the library I wish I had had.

A few weeks back I wrote a small agent to triage GitHub issues across a handful of repos. The plan was simple. Pull every open issue, ask an LLM to classify it, post a one line comment, move on. About 700 issues across six repos.

It died on issue 312 because my laptop went to sleep and the long lived shell session died with it. The agent had no memory of the 311 it had already processed. Start over and pay for 311 LLM calls again, or write some hacky file based "what was I doing" logic.

I wrote the hacky logic. Did it again two days later for a different agent. Then a third time. At that point I made the library.

It is called `agent-resume`. It checkpoints an agent run after every item and resumes from the last checkpoint when the process comes back. Pip install, Python 3.10 plus, zero runtime dependencies, MIT.

#### What the API looks like

The whole library is one function and one iterator. Here is the minimal use case.

```python
from agent_resume import JsonlStore, resume_or_start

store = JsonlStore("issues.ckpt")

def process_issue(issue_id, state):
    results = dict(state.get("results") or {})
    results[str(issue_id)] = call_llm_and_post_comment(issue_id)
    return {**state, "results": results}

run = resume_or_start(
    store=store,
    initial_state={"results": {}},
    work_items=list(range(1, 101)),
)

for issue_id in run:
    new_state = process_issue(issue_id, run.state)
    run.checkpoint(new_state)
```

Run that once. It processes the 100 items, writes 100 lines to `issues.ckpt`, and exits. Run it a second time and it sees the file has all 100 items completed, so the loop body never runs.

Now picture a crash on item 47. The file has 47 rows. You re-run the exact same script. `resume_or_start` reads the last row, restores `run.state` to whatever was in `state` on row 47, marks items 1 through 47 as done, and the loop yields items 48 through 100.

That is the entire library.

#### Why I made the store pluggable

The default is `JsonlStore`. Append only, one Checkpoint per line, fsync on every write. Boring, durable, greppable.

But I have one project where the right answer is Redis (multi worker), and another where the right answer is "throw it in memory because this is a unit test". So the contract is a Protocol called `Sink` with two methods: `append(checkpoint)` and `load_latest()`. Implement those two and you are a store. The runner does not care.

Three lines to write an `InMemoryStore`:

```python
class InMemoryStore:
    def __init__(self):
        self._rows = []
    def append(self, ck):
        self._rows.append(ck)
    def load_latest(self):
        if not self._rows:
            raise NoCheckpoint()
        return self._rows[-1]
```

The library ships this one too because tests need it.

#### The semantic I picked: at least once, not exactly once

This is the most important design choice and I want to call it out loudly. If your worker crashes in the middle of processing item 47 (after the LLM call, before `checkpoint`), the next run will retry item 47. The library does not try to detect "you were halfway through this one when you died" because there is no portable way to do that.

So your workers should be idempotent. Posting the same comment to a GitHub issue twice is bad. Posting once and then checking "did I already comment on this issue" before posting is fine. Most agent workloads are already either idempotent or close to it. If yours is not, wrap it.

The alternative is exactly once semantics, which needs two phase commits and a write ahead log. That is a real database. I did not want to ship a database. I wanted one file and 200 lines of Python.

#### Why JSONL and not pickle or sqlite

I went around on this for an afternoon. Three reasons JSONL won.

One, you can `cat` it. When something goes wrong in production you want to read the file. JSONL is line per row JSON. You open it, you see what was checkpointed, you understand the run.

Two, no schema migration. Add a field to your state dict, the next row has it. Old rows do not. Reading still works because state is just a dict.

Three, fsync per write actually means something for durability. SQLite fsyncs too but you are carrying a binary format and a query language for a use case that needs neither. Pickle is a security hazard if you ever load a checkpoint someone else wrote.

The one downside is that JSON is not great for arbitrary Python objects. The library uses `default=str` as a soft escape hatch so things like `Path` or `Decimal` do not crash the write path, but if your state has live socket handles or LLM clients in it you are going to have a bad time. Keep state JSON safe. It is good discipline for an agent anyway.

#### What it does not do

A few things I left out on purpose.

It does not auto detect schema drift. Restart with a different `work_items` list, the resume skips by id and yields whatever is new. Feature (add three issues mid run, resume picks them up) or bug (you renamed every id and nothing matches). Your call.

It does not lock the file across processes. Process local lock only. Four workers on the same file will corrupt the JSONL. Fix is one worker per file, or a real store like Redis. Documented in the README.

It does not retry items. If the worker raises, that bubbles out. Wrap with `llm-retry` or your own try/except. Checkpointing and nothing else.

#### Try it

It is on GitHub at `MukundaKatta/agent-resume`. There are two examples in the repo. `process_issues_with_resume.py` is the basic loop. `crash_recovery_demo.py` is the one that runs end to end in a single Python process: pass one processes five of ten items and raises, pass two reads the checkpoint and finishes the remaining five. Self contained, no external state, no API keys needed.

Thirty plus tests, all passing. Concurrent writes work. Corrupt JSONL lines raise a useful error. Empty store raises `NoCheckpoint`. Crash mid run, restart, finish. The whole library is small enough that you can read the source in fifteen minutes and decide if you trust it.

If you are running any agent that does more than five things in a row, you want this. Or you want to write it yourself, but I already did.

---

## Future submissions

Open AI infra slot if one shows up. Reuse the post above with a one paragraph "fault tolerance for agent infra" framing on top.
