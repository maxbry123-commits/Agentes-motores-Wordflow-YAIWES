"""Redacted JSONL evidence logging for research-loop decisions."""

from __future__ import annotations

import dataclasses
import datetime as dt
import fcntl
import json
import math
import os
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any


_REDACTED = "[REDACTED]"
_SENSITIVE_KEY_PARTS = (
    "api_key",
    "apikey",
    "authorization",
    "bearer",
    "cookie",
    "credential",
    "email",
    "password",
    "prompt",
    "secret",
)
_TOKEN_PATTERN = re.compile(
    r"(?i)(?:bearer\s+|(?:sk|ghp|github_pat)[-_])[A-Za-z0-9_.-]{8,}"
)
_ABSOLUTE_PATH_PATTERN = re.compile(
    r"(?<![:/A-Za-z0-9])/(?:[^/\s\"'<>]+/)*[^/\s\"'<>,;:)\]}]+"
)
_SAFE_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SAFE_EVENT = re.compile(r"^[a-z][a-z0-9_]{0,63}$")


def redact(value: Any, *, key: str | None = None) -> Any:
    """Return a JSON-safe copy with credentials and local paths removed.

    Redaction happens before serialization, so a caller cannot accidentally
    recover the original sensitive value from the on-disk event.
    """

    normalized_key = (key or "").lower().replace("-", "_")
    token_key = normalized_key == "token" or normalized_key.endswith(
        ("_token", "_token_value")
    )
    if any(part in normalized_key for part in _SENSITIVE_KEY_PARTS) or token_key:
        return _REDACTED

    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        value = {
            item.name: getattr(value, item.name)
            for item in dataclasses.fields(value)
        }

    if isinstance(value, Mapping):
        redacted_items: dict[str, Any] = {}
        for item_key, item in value.items():
            original_key = str(item_key)
            safe_key = redact(original_key)
            if not isinstance(safe_key, str):
                safe_key = "<redacted-key>"
            redacted_items[safe_key] = redact(item, key=original_key)
        return redacted_items
    if isinstance(value, (list, tuple, set)):
        return [redact(item) for item in value]
    if isinstance(value, Path):
        return "<local-path-redacted>" if value.is_absolute() else value.as_posix()
    if isinstance(value, str):
        if os.path.isabs(os.path.expanduser(value)):
            return "<local-path-redacted>"
        redacted_value = _TOKEN_PATTERN.sub(_REDACTED, value)
        return _ABSOLUTE_PATH_PATTERN.sub("<local-path-redacted>", redacted_value)
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return f"<unsupported:{type(value).__name__}>"


class JsonlEvidenceLogger:
    """Append-only, fsync-backed event logger with monotonic sequence IDs."""

    schema_version = "1.0"

    def __init__(self, path: str | Path, run_id: str) -> None:
        if not isinstance(run_id, str) or not _SAFE_IDENTIFIER.fullmatch(run_id):
            raise ValueError("run_id must be a short, path-free identifier")
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id
        descriptor = os.open(self.path, os.O_APPEND | os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            self._sequence = self._inspect_existing(descriptor)
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
            os.close(descriptor)

    def _inspect_existing(self, descriptor: int) -> int:
        os.lseek(descriptor, 0, os.SEEK_SET)
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                break
            chunks.append(chunk)
        try:
            text = b"".join(chunks).decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError("existing evidence log is not UTF-8") from error
        if text and not text.endswith("\n"):
            raise ValueError("existing evidence log has an unterminated final line")

        expected_sequence = 0
        for line_number, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                raise ValueError(f"existing evidence log has a blank line at {line_number}")
            try:
                item = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"existing evidence log is malformed at line {line_number}"
                ) from error
            expected_sequence += 1
            if not isinstance(item, dict):
                raise ValueError(f"existing evidence event is not an object at line {line_number}")
            required_keys = {
                "schema_version",
                "timestamp",
                "run_id",
                "sequence",
                "event",
                "stage",
                "payload",
            }
            if set(item) != required_keys:
                raise ValueError(f"existing evidence event has an invalid schema at line {line_number}")
            if item.get("schema_version") != self.schema_version:
                raise ValueError(f"existing evidence event has an unsupported schema at line {line_number}")
            if item.get("run_id") != self.run_id:
                raise ValueError("existing evidence log belongs to a different run_id")
            if type(item.get("sequence")) is not int or item.get("sequence") != expected_sequence:
                raise ValueError("existing evidence log has a non-contiguous sequence")
            if not isinstance(item.get("event"), str) or not _SAFE_EVENT.fullmatch(item["event"]):
                raise ValueError(f"existing evidence event has an invalid event at line {line_number}")
            if not isinstance(item.get("stage"), str) or not _SAFE_EVENT.fullmatch(item["stage"]):
                raise ValueError(f"existing evidence event has an invalid stage at line {line_number}")
            timestamp = item.get("timestamp")
            if not isinstance(timestamp, str):
                raise ValueError(f"existing evidence event has an invalid timestamp at line {line_number}")
            try:
                parsed_timestamp = dt.datetime.fromisoformat(timestamp)
            except ValueError as error:
                raise ValueError(
                    f"existing evidence event has an invalid timestamp at line {line_number}"
                ) from error
            if parsed_timestamp.tzinfo is None:
                raise ValueError(f"existing evidence timestamp lacks a timezone at line {line_number}")
        return expected_sequence

    @property
    def event_count(self) -> int:
        """Return the number of validated events observed by this instance."""

        descriptor = os.open(self.path, os.O_APPEND | os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            self._sequence = self._inspect_existing(descriptor)
            return self._sequence
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
            os.close(descriptor)

    def begin_run(self, payload: Any) -> dict[str, Any]:
        """Atomically claim an empty log for one research-loop invocation."""

        descriptor = os.open(self.path, os.O_APPEND | os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            if self._inspect_existing(descriptor) != 0:
                raise RuntimeError("research loop requires an empty evidence log")
            self._sequence = 1
            item = self._event_item("run_started", "run", payload, self._sequence)
            self._write_all(descriptor, self._encode(item))
            os.fsync(descriptor)
            return item
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
            os.close(descriptor)

    def record(self, event: str, stage: str, payload: Any) -> dict[str, Any]:
        """Redact and durably append one evidence event."""

        if not isinstance(event, str) or not _SAFE_EVENT.fullmatch(event):
            raise ValueError("event must be a lowercase identifier")
        if not isinstance(stage, str) or not _SAFE_EVENT.fullmatch(stage):
            raise ValueError("stage must be a lowercase identifier")

        descriptor = os.open(self.path, os.O_APPEND | os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            self._sequence = self._inspect_existing(descriptor) + 1
            item = self._event_item(event, stage, payload, self._sequence)
            self._write_all(descriptor, self._encode(item))
            os.fsync(descriptor)
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
            os.close(descriptor)
        return item

    def _event_item(
        self,
        event: str,
        stage: str,
        payload: Any,
        sequence: int,
    ) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
            "run_id": self.run_id,
            "sequence": sequence,
            "event": event,
            "stage": stage,
            "payload": redact(payload),
        }

    @staticmethod
    def _encode(item: dict[str, Any]) -> bytes:
        return (json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")

    @staticmethod
    def _write_all(descriptor: int, payload: bytes) -> None:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("failed to append evidence event")
            view = view[written:]
