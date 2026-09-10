"""Basic agent-resume usage: process a list of GitHub issue ids with
checkpointing after each one.

Run it twice in a row to see resume in action:

    python examples/process_issues_with_resume.py
    python examples/process_issues_with_resume.py

(The second run finds the existing checkpoint and starts from where the
first one left off.)
"""

from pathlib import Path

from agent_resume import JsonlStore, resume_or_start


def process_issue(issue_id: int, state: dict) -> dict:
    """Pretend this calls an LLM, posts a comment, updates Notion, etc.

    Note the stringified key: JSON only allows string dict keys, and the
    store round-trips through JSON, so we use str(issue_id) here.
    """
    results = dict(state.get("results") or {})
    results[str(issue_id)] = f"summary for #{issue_id}"
    return {**state, "results": results, "last_processed": issue_id}


def main() -> None:
    path = Path("issues.ckpt")
    store = JsonlStore(path)

    issues = list(range(1, 11))
    run = resume_or_start(
        store=store,
        initial_state={"results": {}, "last_processed": None},
        work_items=issues,
    )

    if run.resumed:
        print(f"Resuming from turn {run.turn}. {len(run.completed_items)} of {len(issues)} done.")
    else:
        print(f"Starting fresh. {len(issues)} issues to process.")

    for issue_id in run:
        print(f"  processing #{issue_id} ...")
        new_state = process_issue(issue_id, run.state)
        run.checkpoint(new_state)

    print(f"\nDone. Total turns: {run.turn}")
    print(f"Final state: {run.state}")
    print(f"Checkpoint file: {path.absolute()}")


if __name__ == "__main__":
    main()
