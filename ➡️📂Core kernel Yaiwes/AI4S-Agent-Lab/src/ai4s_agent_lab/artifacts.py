"""Atomic artifact delivery helpers."""

from __future__ import annotations

import json
import hashlib
import os
import tempfile
from pathlib import Path
from typing import Any

from .contracts import to_plain_data


class AtomicArtifactWriter:
    """Write complete artifacts through a same-directory atomic replace."""

    def write_json(self, path: str | Path, value: Any) -> Path:
        destination = Path(path)
        payload = self._json_bytes(value)
        self._write_bytes(destination, payload)
        return destination

    @staticmethod
    def _json_bytes(value: Any) -> bytes:
        return (
            json.dumps(
                to_plain_data(value),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")

    @staticmethod
    def verify_json(path: str | Path, expected: Any) -> str:
        """Read an artifact back, compare it exactly, and return its SHA-256."""

        artifact_path = Path(path)
        payload = artifact_path.read_bytes()
        try:
            observed = json.loads(payload)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise RuntimeError("delivered artifact is not valid JSON") from error
        if payload != AtomicArtifactWriter._json_bytes(expected):
            raise RuntimeError("delivered artifact does not match the verified summary")
        return hashlib.sha256(payload).hexdigest()

    @staticmethod
    def _write_bytes(destination: Path, payload: bytes) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
        )
        temporary_path = Path(temporary_name)
        try:
            os.fchmod(descriptor, 0o600)
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, destination)
            directory_descriptor = os.open(destination.parent, os.O_RDONLY)
            try:
                os.fsync(directory_descriptor)
            finally:
                os.close(directory_descriptor)
        except BaseException:
            try:
                os.close(descriptor)
            except OSError:
                pass
            temporary_path.unlink(missing_ok=True)
            raise
