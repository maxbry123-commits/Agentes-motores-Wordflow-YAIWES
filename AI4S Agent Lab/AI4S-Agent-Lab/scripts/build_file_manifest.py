#!/usr/bin/env python3
"""Build the file-level provenance and checksum manifest for the public tree."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path


MANIFEST_PATH = Path("audit/FILE_MANIFEST.tsv")


def _candidate_paths(root: Path) -> list[Path]:
    completed = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "ls-files",
            "-z",
            "--cached",
            "--others",
            "--exclude-standard",
        ],
        check=True,
        capture_output=True,
    )
    names = completed.stdout.decode("utf-8").split("\0")
    return sorted(
        (Path(name) for name in names if name and Path(name) != MANIFEST_PATH),
        key=lambda path: path.as_posix(),
    )


def _classification(path: Path) -> tuple[str, str, str]:
    value = path.as_posix()
    if value == "LICENSE":
        return (
            "standard_license_text",
            "Apache-2.0 license text",
            "Apache-2.0",
        )
    if value.startswith("evidence/reconstructed_traces/"):
        return (
            "personal_reconstructed_evidence",
            "personal reconstruction from bounded historical observations; not an original log",
            "Apache-2.0",
        )
    if value.startswith(("src/", "tests/", "examples/", "scripts/", ".github/")) or value == "pyproject.toml":
        return (
            "personal_original_code",
            "created for Wanrun Cong's personal research project",
            "Apache-2.0",
        )
    return (
        "personal_project_documentation",
        "written for this personal public research project",
        "Apache-2.0",
    )


def build_manifest(root: Path) -> Path:
    root = root.resolve()
    rows = ["path\tsha256\tbytes\tclassification\tprovenance\tlicense"]
    for relative_path in _candidate_paths(root):
        payload = (root / relative_path).read_bytes()
        classification, provenance, license_name = _classification(relative_path)
        rows.append(
            "\t".join(
                (
                    relative_path.as_posix(),
                    hashlib.sha256(payload).hexdigest(),
                    str(len(payload)),
                    classification,
                    provenance,
                    license_name,
                )
            )
        )
    rows.append(
        "\t".join(
            (
                MANIFEST_PATH.as_posix(),
                "SELF",
                "SELF",
                "generated_file_manifest",
                "generated from the current public tree",
                "Apache-2.0",
            )
        )
    )
    destination = root / MANIFEST_PATH
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return destination


if __name__ == "__main__":
    repository_root = Path(__file__).resolve().parents[1]
    print(build_manifest(repository_root))
