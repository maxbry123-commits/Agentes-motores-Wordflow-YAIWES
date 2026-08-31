"""The Checkpoint dataclass.

A Checkpoint is one row in a store. The shape is intentionally small:

- `turn`: monotonically increasing index, used for ordering and debugging.
- `state`: an arbitrary JSON-serializable dict the caller owns.
- `completed_items`: list of work-item ids already finished. Driven by the
  runner so resume knows what to skip.
- `timestamp`: unix seconds when the checkpoint was written. Useful for
  forensic "how far did we get before the box died" questions.

The dataclass is intentionally not frozen because callers occasionally want
to amend `completed_items` before passing it back to the store, but it is
treated as a value object everywhere in the library.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Checkpoint:
    turn: int
    state: dict[str, Any]
    completed_items: list[Any] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_json(self) -> str:
        """Serialize to a single JSONL line (no embedded newlines).

        `default=str` is a soft escape hatch so things like Decimal or Path
        do not crash the write path; the caller is still on the hook for
        keeping state JSON-safe if they want clean round-trips.
        """
        return json.dumps(asdict(self), default=str, separators=(",", ":"))

    @classmethod
    def from_json(cls, raw: str) -> Checkpoint:
        """Parse a single JSONL line back into a Checkpoint.

        Raises whatever `json.loads` raises on a malformed line; the store
        layer is responsible for translating those into `CheckpointCorrupt`.
        """
        data = json.loads(raw)
        return cls(
            turn=int(data["turn"]),
            state=data.get("state") or {},
            completed_items=list(data.get("completed_items") or []),
            timestamp=float(data.get("timestamp", 0.0)),
        )
