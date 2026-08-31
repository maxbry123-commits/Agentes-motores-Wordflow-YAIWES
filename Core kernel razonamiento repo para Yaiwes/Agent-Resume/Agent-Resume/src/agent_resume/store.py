"""Pluggable stores for checkpoints.

The contract is small on purpose. A store is anything with `append()` and
`load_latest()`. That lets callers swap in a Redis, SQLite, or S3 backed
store without changing the runner.

`JsonlStore` is the default. Append-only, one Checkpoint per line, fsync on
every write. This is the boring choice and it is the right one for most
single-process agent jobs.

`InMemoryStore` exists so tests do not need a temp dir, and so callers can
exercise the resume path in unit tests without touching disk.
"""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Iterator, Protocol, runtime_checkable

from .checkpoint import Checkpoint
from .exceptions import CheckpointCorrupt, NoCheckpoint


@runtime_checkable
class Sink(Protocol):
    """Minimal store contract. Implement these two methods and you're a store."""

    def append(self, checkpoint: Checkpoint) -> None: ...
    def load_latest(self) -> Checkpoint: ...


class InMemoryStore:
    """In-memory store. Not durable across processes; use for tests + demos."""

    def __init__(self) -> None:
        self._rows: list[Checkpoint] = []
        self._lock = threading.Lock()

    def append(self, checkpoint: Checkpoint) -> None:
        with self._lock:
            self._rows.append(checkpoint)

    def load_latest(self) -> Checkpoint:
        with self._lock:
            if not self._rows:
                raise NoCheckpoint("no checkpoints in memory")
            return self._rows[-1]

    def all(self) -> list[Checkpoint]:
        """Test helper. Snapshot of every checkpoint written so far."""
        with self._lock:
            return list(self._rows)

    def __len__(self) -> int:
        with self._lock:
            return len(self._rows)


class JsonlStore:
    """Append-only JSONL file. One Checkpoint per line.

    fsync-on-write is on by default because the whole point of a checkpoint
    is to survive a crash. Callers who care more about throughput than
    durability can pass `fsync=False`.
    """

    def __init__(self, path: str | os.PathLike[str], *, fsync: bool = True) -> None:
        self.path = Path(path)
        self._fsync = fsync
        # Process-local lock; if two processes write to the same file you
        # need a file lock or a different store. Documented in the README.
        self._lock = threading.Lock()
        # Touch parent dir so the first write doesn't trip on missing path.
        if self.path.parent and str(self.path.parent) not in {"", "."}:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, checkpoint: Checkpoint) -> None:
        line = checkpoint.to_json()
        if "\n" in line:
            # JSONL is line-delimited; an embedded newline corrupts the file.
            # `to_json` should already strip these but be paranoid.
            raise ValueError("checkpoint payload contains a newline")
        with self._lock:
            # Open per-write so a crash mid-run does not leave a stray fd.
            with open(self.path, "a", encoding="utf-8") as fh:
                fh.write(line)
                fh.write("\n")
                fh.flush()
                if self._fsync:
                    try:
                        os.fsync(fh.fileno())
                    except OSError:
                        # Some filesystems (tmpfs on certain CI images)
                        # reject fsync. Better to keep going than crash.
                        pass

    def iter_checkpoints(self) -> Iterator[Checkpoint]:
        """Stream all checkpoints in write order. Used by callers who want
        to audit the full run history rather than just the latest row."""
        if not self.path.exists():
            return
        with open(self.path, encoding="utf-8") as fh:
            for line_no, raw in enumerate(fh, start=1):
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    yield Checkpoint.from_json(raw)
                except (json.JSONDecodeError, KeyError, ValueError) as exc:
                    raise CheckpointCorrupt(
                        f"line {line_no} in {self.path}: {exc}",
                        line_number=line_no,
                    ) from exc

    def load_latest(self) -> Checkpoint:
        if not self.path.exists() or self.path.stat().st_size == 0:
            raise NoCheckpoint(f"{self.path} is empty or missing")
        latest: Checkpoint | None = None
        for ckpt in self.iter_checkpoints():
            latest = ckpt
        if latest is None:
            raise NoCheckpoint(f"{self.path} contains no checkpoints")
        return latest

    def __len__(self) -> int:
        if not self.path.exists():
            return 0
        return sum(1 for _ in self.iter_checkpoints())
