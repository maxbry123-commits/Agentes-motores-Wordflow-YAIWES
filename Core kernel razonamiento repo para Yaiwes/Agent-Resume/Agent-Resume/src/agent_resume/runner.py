"""`resume_or_start()` facade.

This is the one function 95% of callers should ever import. Hands back a
`Resumable` that is either fresh or pre-loaded from the store, depending on
what is on disk.
"""

from __future__ import annotations

from typing import Any, Callable, Sequence

from .resumable import Resumable
from .store import Sink


def resume_or_start(
    *,
    store: Sink,
    initial_state: dict[str, Any] | None = None,
    work_items: Sequence[Any] = (),
    item_key: Callable[[Any], Any] | None = None,
) -> Resumable:
    """Open or resume a checkpointed run.

    Args:
        store: any object implementing the Sink protocol (JsonlStore,
            InMemoryStore, or your own).
        initial_state: the starting state dict if no checkpoint exists.
            Ignored when resuming; the stored state wins.
        work_items: ordered sequence of items to process. The Resumable
            yields each one that has not already been marked complete.
        item_key: optional function to extract a comparable id from each
            work item. Default uses the item itself.

    Returns:
        A `Resumable` ready to iterate. Check `.resumed` to know whether
        it picked up an existing run or started a new one.
    """
    if item_key is None:
        return Resumable(
            store=store,
            initial_state=initial_state,
            work_items=work_items,
        )
    return Resumable(
        store=store,
        initial_state=initial_state,
        work_items=work_items,
        item_key=item_key,
    )
