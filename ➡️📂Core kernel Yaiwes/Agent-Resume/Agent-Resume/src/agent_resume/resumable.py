"""The Resumable class.

This is what `resume_or_start()` returns. It is also fine to construct
directly when you want the full control surface (custom item key fn,
custom store, mid-iteration `checkpoint()` calls outside the loop, etc).

Mental model:

- You give it a store, an initial state, and a list of work_items.
- It restores the latest checkpoint from the store if one exists.
- Iterating yields only the items that have not been completed yet.
- After each item your code calls `.checkpoint(new_state)`, which appends
  a fresh Checkpoint to the store and advances the in-memory turn counter.
- If the process dies before that `.checkpoint()` call, you re-run the same
  code and the item that was in flight gets retried. That is the intended
  semantic: items are at-least-once, not exactly-once.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Iterator, Sequence

from .checkpoint import Checkpoint
from .exceptions import NoCheckpoint
from .store import Sink

# Default key function: rely on the item itself being hashable + comparable.
# Most callers pass ints, strings, or simple identifiers. For richer objects
# pass an explicit `item_key` to extract the id.
_DEFAULT_KEY: Callable[[Any], Any] = lambda item: item  # noqa: E731


class Resumable:
    def __init__(
        self,
        *,
        store: Sink,
        initial_state: dict[str, Any] | None = None,
        work_items: Sequence[Any] = (),
        item_key: Callable[[Any], Any] = _DEFAULT_KEY,
    ) -> None:
        self._store = store
        self._item_key = item_key
        self._work_items: list[Any] = list(work_items)
        self._initial_state: dict[str, Any] = dict(initial_state or {})

        # Restore from store if it has data; otherwise start fresh.
        try:
            latest = store.load_latest()
            self._restored = True
            self._turn = latest.turn
            self._state: dict[str, Any] = dict(latest.state)
            self._completed: list[Any] = list(latest.completed_items)
        except NoCheckpoint:
            self._restored = False
            self._turn = 0
            self._state = dict(self._initial_state)
            self._completed = []

        self._current_item: Any | None = None

    # Public state accessors ------------------------------------------------

    @property
    def state(self) -> dict[str, Any]:
        """The current rolling state. Mutate at your own risk; prefer to
        return a new dict from your worker and hand it to `checkpoint()`."""
        return self._state

    @property
    def turn(self) -> int:
        """How many checkpoints have been written for this run, including
        the restored one if any."""
        return self._turn

    @property
    def completed_items(self) -> list[Any]:
        return list(self._completed)

    @property
    def resumed(self) -> bool:
        """True if this run started from an existing checkpoint."""
        return self._restored

    def remaining_items(self) -> list[Any]:
        """The work items that still need to be processed."""
        done = set(self._item_key(c) for c in self._completed)
        return [item for item in self._work_items if self._item_key(item) not in done]

    # Iteration -------------------------------------------------------------

    def __iter__(self) -> Iterator[Any]:
        """Yield each remaining work item exactly once.

        The runner pattern is: yield an item, caller does work, caller calls
        `.checkpoint(new_state)`. If they forget to checkpoint, the item is
        still marked complete in memory but nothing is persisted, so a crash
        replays it. That matches the at-least-once semantic above.
        """
        done = set(self._item_key(c) for c in self._completed)
        for item in self._work_items:
            key = self._item_key(item)
            if key in done:
                continue
            self._current_item = item
            yield item
            # If `.checkpoint()` was called, _current_item is already cleared.
            # If not, we still mark it complete in memory so a subsequent
            # iter() in the same process does not re-yield it.
            if self._current_item is item:
                self._completed.append(key)
                self._current_item = None

    # Mutation --------------------------------------------------------------

    def checkpoint(self, new_state: dict[str, Any] | None = None) -> Checkpoint:
        """Persist a new checkpoint covering the in-flight item.

        Bumps the turn counter, replaces in-memory state with `new_state`
        (if provided), marks the current item complete, and appends to the
        store.

        Safe to call outside the iteration loop: if there is no in-flight
        item, the checkpoint just snapshots current state.
        """
        if new_state is not None:
            self._state = dict(new_state)

        if self._current_item is not None:
            key = self._item_key(self._current_item)
            # self._completed stores keys directly, so compare against them.
            if key not in self._completed:
                self._completed.append(key)
            self._current_item = None

        self._turn += 1
        ckpt = Checkpoint(
            turn=self._turn,
            state=self._state,
            completed_items=list(self._completed),
            timestamp=time.time(),
        )
        self._store.append(ckpt)
        return ckpt
