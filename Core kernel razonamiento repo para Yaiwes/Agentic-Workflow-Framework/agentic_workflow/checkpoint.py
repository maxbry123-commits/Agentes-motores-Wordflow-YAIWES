"""Durable checkpoint storage for clean stop/resume.

A :class:`CheckpointStore` persists the manager's serialized state to disk as
JSON. Writes are atomic (write-to-temp + ``os.replace``) so an interrupted save
can never leave a half-written, unloadable checkpoint behind.

The store is intentionally tiny and dependency-free: a checkpoint is just a
``dict`` that the :class:`~agentic_workflow.manager.Manager` knows how to
produce and consume. Keeping the format plain JSON means a human can open a
checkpoint and read exactly where a run stopped.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from .errors import CheckpointError


class CheckpointStore:
    """Persist and load manager checkpoints under a directory."""

    def __init__(self, directory: os.PathLike[str] | str) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _path(self, name: str) -> Path:
        safe = name.strip().replace(os.sep, "_")
        if not safe:
            raise CheckpointError("checkpoint name must be a non-empty string")
        return self.directory / f"{safe}.json"

    def exists(self, name: str) -> bool:
        return self._path(name).is_file()

    def save(self, name: str, payload: Dict[str, Any]) -> Path:
        """Atomically write ``payload`` as JSON under ``name``."""
        path = self._path(name)
        try:
            serialized = json.dumps(payload, indent=2, ensure_ascii=False, default=str)
        except (TypeError, ValueError) as exc:  # non-serializable state
            raise CheckpointError(f"checkpoint '{name}' is not serializable: {exc}") from exc

        fd, tmp_name = tempfile.mkstemp(dir=self.directory, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(serialized)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_name, path)  # atomic on POSIX and Windows
        except OSError as exc:
            # Best-effort cleanup of the temp file if the swap failed.
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
            raise CheckpointError(f"failed to write checkpoint '{name}': {exc}") from exc
        return path

    def load(self, name: str) -> Dict[str, Any]:
        path = self._path(name)
        if not path.is_file():
            raise CheckpointError(f"checkpoint '{name}' does not exist at {path}")
        try:
            with path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise CheckpointError(f"failed to read checkpoint '{name}': {exc}") from exc

    def list(self) -> List[str]:
        return sorted(p.stem for p in self.directory.glob("*.json"))

    def latest(self) -> Optional[str]:
        """Return the name of the most recently modified checkpoint, if any."""
        candidates = list(self.directory.glob("*.json"))
        if not candidates:
            return None
        newest = max(candidates, key=lambda p: p.stat().st_mtime)
        return newest.stem
