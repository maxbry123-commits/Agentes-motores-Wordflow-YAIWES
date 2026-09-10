#!/usr/bin/env python3
"""Fail closed when the public tree violates publication boundaries."""

from __future__ import annotations

import json
import hashlib
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote, urlsplit


MAX_FILE_BYTES = 1024 * 1024

EXCLUDED_DIRECTORY_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "artifacts",
    "build",
    "dist",
    "venv",
}

PROHIBITED_SUFFIXES = (
    ".7z",
    ".arrow",
    ".bin",
    ".bz2",
    ".checkpoint",
    ".cif",
    ".ckpt",
    ".db",
    ".dill",
    ".engine",
    ".feather",
    ".gz",
    ".h5",
    ".hdf5",
    ".joblib",
    ".jks",
    ".key",
    ".keystore",
    ".mol2",
    ".npy",
    ".npz",
    ".onnx",
    ".p12",
    ".pdb",
    ".pem",
    ".pb",
    ".parquet",
    ".pickle",
    ".pkl",
    ".pth",
    ".pt",
    ".rar",
    ".safetensors",
    ".sdf",
    ".sqlite",
    ".sqlite3",
    ".tar",
    ".tgz",
    ".tflite",
    ".weights",
    ".xz",
    ".zip",
)

PRIVATE_KEY_HEADER = re.compile(
    r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"
)
PROVIDER_TOKEN = re.compile(
    r"(?x)"
    r"(?:\b(?:sk|ghp)[-_][A-Za-z0-9_.-]{16,}\b)"
    r"|(?:\bgithub_pat_[A-Za-z0-9_]{20,}\b)"
    r"|(?:\bAKIA[0-9A-Z]{16}\b)"
    r"|(?:\beyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b)"
)
SECRET_ASSIGNMENT = re.compile(
    r"(?im)^\s*(?:export\s+)?"
    r"[A-Z][A-Z0-9_]*(?:API_KEY|TOKEN|SECRET|PASSWORD)\s*=\s*"
    r"[\"']?([^\s\"'#]{16,})"
)
URL_CREDENTIALS = re.compile(r"https?://[^\s/:]+:[^\s/@]+@")
PRIVATE_IPV4 = re.compile(
    r"(?<![0-9.])(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    r"|192\.168\.\d{1,3}\.\d{1,3}"
    r"|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})(?![0-9.])"
)
USER_SPECIFIC_PATH = re.compile(
    r"(?<![A-Za-z0-9:])/(?:Users|home)/[^\s\"'<>]+"
)
SERVER_IDENTIFIER = re.compile(r"\bSERVER_\d+\b")
IMAGE_DIGEST = re.compile(r"\bsha256:[0-9a-fA-F]{64}\b")
PEM_FILENAME = re.compile(r"(?i)(?<![A-Za-z0-9_.-])[A-Za-z0-9_.-]+\.pem\b")

INLINE_MARKDOWN_LINK = re.compile(
    r"!?\[[^\]]*\]\(\s*(<[^>]+>|[^)\s]+)"
    r"(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)"
)
REFERENCE_MARKDOWN_LINK = re.compile(
    r"(?m)^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)"
)


@dataclass
class VerificationResult:
    issues: list[str] = field(default_factory=list)
    candidate_count: int = 0
    markdown_count: int = 0
    trace_count: int = 0
    trace_event_count: int = 0

    @property
    def ok(self) -> bool:
        return not self.issues


def _relative_display(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _worktree_candidates(root: Path) -> list[Path]:
    """Return tracked, staged, and non-ignored untracked publication candidates."""

    command = [
        "git",
        "-C",
        str(root),
        "ls-files",
        "-z",
        "--cached",
        "--others",
        "--exclude-standard",
    ]
    completed = subprocess.run(command, capture_output=True, check=False)
    if completed.returncode == 0:
        decoded = completed.stdout.decode("utf-8", errors="surrogateescape")
        names = [name for name in decoded.split("\0") if name]
        return sorted((root / name for name in names), key=lambda item: item.as_posix())

    candidates: list[Path] = []
    for current, directories, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        retained_directories: list[str] = []
        for directory in directories:
            candidate = current_path / directory
            if candidate.is_symlink():
                candidates.append(candidate)
            elif directory not in EXCLUDED_DIRECTORY_NAMES:
                retained_directories.append(directory)
        directories[:] = retained_directories
        candidates.extend(current_path / filename for filename in filenames)
    return sorted(candidates, key=lambda item: item.as_posix())


def _read_text(path: Path) -> str | None:
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\0" in raw:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def _check_sensitive_text(path: Path, text: str, root: Path, result: VerificationResult) -> None:
    display = _relative_display(path, root)
    pattern_labels = (
        ("private-key material", PRIVATE_KEY_HEADER),
        ("provider credential", PROVIDER_TOKEN),
        ("credential assignment", SECRET_ASSIGNMENT),
        ("credentials embedded in URL", URL_CREDENTIALS),
        ("private IPv4 endpoint", PRIVATE_IPV4),
        ("user-specific absolute path", USER_SPECIFIC_PATH),
        ("server-style environment identifier", SERVER_IDENTIFIER),
        ("container image digest", IMAGE_DIGEST),
        ("private-key filename", PEM_FILENAME),
    )
    for label, pattern in pattern_labels:
        if pattern.search(text):
            result.issues.append(f"{display}: contains possible {label}")
def _markdown_targets(text: str) -> set[str]:
    targets = {match.group(1) for match in INLINE_MARKDOWN_LINK.finditer(text)}
    targets.update(match.group(1) for match in REFERENCE_MARKDOWN_LINK.finditer(text))
    return targets


def _check_markdown_links(path: Path, text: str, root: Path, result: VerificationResult) -> None:
    display = _relative_display(path, root)
    root_resolved = root.resolve()
    for raw_target in sorted(_markdown_targets(text)):
        target = raw_target.strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        target = unquote(target)

        split = urlsplit(target)
        if split.scheme or split.netloc or target.startswith(("#", "/")):
            continue
        relative_target = split.path
        if not relative_target:
            continue

        resolved = (path.parent / relative_target).resolve(strict=False)
        try:
            resolved.relative_to(root_resolved)
        except ValueError:
            result.issues.append(
                f"{display}: relative link escapes repository: {raw_target}"
            )
            continue
        if not resolved.exists():
            result.issues.append(f"{display}: broken relative link: {raw_target}")


def _check_reconstructed_traces(root: Path, result: VerificationResult) -> None:
    trace_directory = root / "evidence" / "reconstructed_traces"
    if not trace_directory.is_dir():
        result.issues.append("evidence/reconstructed_traces: required directory is missing")
        return

    trace_files = sorted(trace_directory.glob("*.jsonl"))
    if not trace_files:
        result.issues.append("evidence/reconstructed_traces: no JSONL traces found")
        return

    result.trace_count = len(trace_files)
    for trace_file in trace_files:
        display = _relative_display(trace_file, root)
        expected_sequence = 0
        expected_trace_id: str | None = None
        event_count = 0
        try:
            lines = trace_file.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as error:
            result.issues.append(f"{display}: cannot read UTF-8 JSONL ({error})")
            continue

        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                result.issues.append(f"{display}:{line_number}: blank JSONL line")
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as error:
                result.issues.append(
                    f"{display}:{line_number}: invalid JSON ({error.msg})"
                )
                continue
            if not isinstance(event, dict):
                result.issues.append(f"{display}:{line_number}: event is not an object")
                continue

            event_count += 1
            sequence = event.get("sequence")
            if type(sequence) is not int or sequence != expected_sequence:
                result.issues.append(
                    f"{display}:{line_number}: sequence must be {expected_sequence}, got {sequence!r}"
                )
            expected_sequence += 1

            trace_id = event.get("trace_id")
            if not isinstance(trace_id, str) or not trace_id.strip():
                result.issues.append(f"{display}:{line_number}: trace_id is missing")
            elif expected_trace_id is None:
                expected_trace_id = trace_id
            elif trace_id != expected_trace_id:
                result.issues.append(
                    f"{display}:{line_number}: trace_id changed within one file"
                )

            if event.get("reconstructed") is not True:
                result.issues.append(
                    f"{display}:{line_number}: reconstructed must be true"
                )
            if event.get("not_original_log") is not True:
                result.issues.append(
                    f"{display}:{line_number}: not_original_log must be true"
                )

        if event_count == 0:
            result.issues.append(f"{display}: trace contains no events")
        result.trace_event_count += event_count


def _check_file_manifest(
    root: Path,
    candidates: list[Path],
    result: VerificationResult,
) -> None:
    audit_directory = root / "audit"
    if not audit_directory.is_dir():
        return
    manifest = audit_directory / "FILE_MANIFEST.tsv"
    if not manifest.is_file():
        result.issues.append("audit/FILE_MANIFEST.tsv: required manifest is missing")
        return

    try:
        lines = manifest.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        result.issues.append(f"audit/FILE_MANIFEST.tsv: cannot read manifest ({error})")
        return
    expected_header = "path\tsha256\tbytes\tclassification\tprovenance\tlicense"
    if not lines or lines[0] != expected_header:
        result.issues.append("audit/FILE_MANIFEST.tsv: invalid header")
        return

    entries: dict[str, tuple[str, str, str, str, str]] = {}
    for line_number, line in enumerate(lines[1:], start=2):
        columns = line.split("\t")
        if len(columns) != 6:
            result.issues.append(
                f"audit/FILE_MANIFEST.tsv:{line_number}: expected 6 columns"
            )
            continue
        path_name, digest, byte_count, classification, provenance, license_name = columns
        if path_name in entries:
            result.issues.append(
                f"audit/FILE_MANIFEST.tsv:{line_number}: duplicate path {path_name}"
            )
            continue
        if not all((classification, provenance, license_name)):
            result.issues.append(
                f"audit/FILE_MANIFEST.tsv:{line_number}: classification fields are required"
            )
        entries[path_name] = (digest, byte_count, classification, provenance, license_name)

    manifest_name = "audit/FILE_MANIFEST.tsv"
    expected_paths = {
        _relative_display(path, root)
        for path in candidates
        if os.path.lexists(path)
    }
    if set(entries) != expected_paths:
        missing = sorted(expected_paths - set(entries))
        extra = sorted(set(entries) - expected_paths)
        if missing:
            result.issues.append(
                "audit/FILE_MANIFEST.tsv: missing paths: " + ", ".join(missing)
            )
        if extra:
            result.issues.append(
                "audit/FILE_MANIFEST.tsv: unexpected paths: " + ", ".join(extra)
            )

    for path_name, (digest, byte_count, _, _, _) in entries.items():
        if path_name == manifest_name:
            if (digest, byte_count) != ("SELF", "SELF"):
                result.issues.append(
                    "audit/FILE_MANIFEST.tsv: self row must use SELF placeholders"
                )
            continue
        path = root / path_name
        if not path.is_file() or path.is_symlink():
            continue
        payload = path.read_bytes()
        if digest != hashlib.sha256(payload).hexdigest():
            result.issues.append(f"audit/FILE_MANIFEST.tsv: stale hash for {path_name}")
        if byte_count != str(len(payload)):
            result.issues.append(f"audit/FILE_MANIFEST.tsv: stale size for {path_name}")


def verify_repository(root: Path) -> VerificationResult:
    root = root.resolve()
    result = VerificationResult()
    candidates = _worktree_candidates(root)
    result.candidate_count = len(candidates)

    for path in candidates:
        display = _relative_display(path, root)
        if not os.path.lexists(path):
            result.issues.append(f"{display}: tracked candidate is missing")
            continue
        if path.is_symlink():
            result.issues.append(f"{display}: symbolic links are not allowed")
            continue
        if not path.is_file():
            result.issues.append(f"{display}: candidate is not a regular file")
            continue

        try:
            size = path.stat().st_size
        except OSError as error:
            result.issues.append(f"{display}: cannot inspect file ({error})")
            continue
        too_large = size > MAX_FILE_BYTES
        if too_large:
            result.issues.append(
                f"{display}: file is {size} bytes (limit {MAX_FILE_BYTES})"
            )

        lower_name = path.name.lower()
        if lower_name.endswith(PROHIBITED_SUFFIXES):
            result.issues.append(f"{display}: prohibited model/data/key/archive suffix")

        if too_large:
            continue
        text = _read_text(path)
        if text is None:
            result.issues.append(
                f"{display}: non-UTF-8 or NUL-containing candidates are not allowed"
            )
            continue
        _check_sensitive_text(path, text, root, result)
        if path.suffix.lower() in {".md", ".markdown"}:
            result.markdown_count += 1
            _check_markdown_links(path, text, root, result)

    _check_reconstructed_traces(root, result)
    _check_file_manifest(root, candidates, result)
    return result


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    root = Path(arguments[0]) if arguments else Path(__file__).resolve().parents[1]
    result = verify_repository(root)

    if result.ok:
        print(
            "Publication audit PASSED: "
            f"{result.candidate_count} candidates, "
            f"{result.markdown_count} Markdown files, "
            f"{result.trace_count} reconstructed traces, "
            f"{result.trace_event_count} trace events."
        )
        return 0

    print(f"Publication audit FAILED with {len(result.issues)} issue(s):")
    for issue in result.issues:
        print(f"- {issue}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
