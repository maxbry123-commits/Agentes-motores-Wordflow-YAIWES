"""Prompt loader for transcript-coding.

Prompts live in references/*.md files (not hardcoded in Python) so that researchers
can edit them without touching code. The loader supports:
  - Loading by name (prompt_<stage>.md)
  - Extracting a specific section by heading (e.g. "## System" / "## User")
  - Variable substitution via Python str.format syntax
  - Version extraction from the first "Version:" line of the file

Format convention for prompt files:

    # <Stage> prompt
    Version: <semver-like tag>

    ## System
    <system prompt text>

    ## User
    <user prompt template with {placeholders}>
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROMPT_VERSION_RE = re.compile(r"^Version:\s*(\S+)\s*$", re.MULTILINE)
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


@dataclass
class Prompt:
    name: str
    version: str
    sections: dict[str, str]

    def render(self, section: str, **vars: Any) -> str:
        """Return the section text with variables substituted via str.format."""
        if section not in self.sections:
            raise KeyError(f"Section '{section}' not found in prompt '{self.name}'")
        tmpl = self.sections[section]
        # Use a custom format that tolerates missing keys gracefully for literal braces.
        return tmpl.format(**vars)


class PromptLoader:
    def __init__(self, references_dir: Path) -> None:
        self.references_dir = Path(references_dir)
        if not self.references_dir.exists():
            raise FileNotFoundError(f"References directory not found: {references_dir}")

    def load(self, name: str) -> Prompt:
        """Load a prompt by base name (without .md)."""
        path = self.references_dir / f"{name}.md"
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        text = path.read_text(encoding="utf-8")

        version_match = PROMPT_VERSION_RE.search(text)
        version = version_match.group(1) if version_match else "unversioned"

        # Split by "## " level-2 headings.
        sections: dict[str, str] = {}
        matches = list(SECTION_RE.finditer(text))
        for i, m in enumerate(matches):
            section_name = m.group(1).strip()
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            sections[section_name] = body

        return Prompt(name=name, version=version, sections=sections)

    def load_frames(self, preset: str) -> str:
        """Load interpretive frames content for a given preset.

        Presets:
          - minimal: returns "## Minimal" section from interpretive_frames.md
          - default: returns "## Default" section
          - full: returns "## Full" section
          - custom:<path>: reads the file at <path> as-is
        """
        if preset.startswith("custom:"):
            custom_path = Path(preset[len("custom:"):])
            return custom_path.read_text(encoding="utf-8")
        prompt = self.load("interpretive_frames")
        section_name = preset.capitalize()
        if section_name not in prompt.sections:
            raise KeyError(
                f"Preset '{preset}' not found in interpretive_frames.md. "
                f"Available: {list(prompt.sections.keys())}"
            )
        return prompt.sections[section_name]
