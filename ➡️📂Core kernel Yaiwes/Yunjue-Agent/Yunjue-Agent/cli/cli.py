from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import textwrap
import tomllib
import locale
import shutil
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, AsyncIterator, Tuple

import yaml
from langchain_core.messages import HumanMessage, SystemMessage

from src.schema.types import LLMType
from src.services.llms.llm import create_llm
from src.config.config import load_yaml_config
from src.utils.event_parser import EventParser
from src.core import build_graph
GraphEvent = Tuple[str, Dict[str, Any]]

graph = build_graph().compile()

async def graph_event_stream(user_query: str, task_id, run_dir) -> AsyncIterator[GraphEvent]:
    initial_state = {"user_query": user_query}
    config = {
        "configurable": {
            "thread_id": task_id,
            "dynamic_tools_dir": f"{run_dir}/private_dynamic_tools/dynamic_tools_{task_id}",
            "dynamic_tools_public_dir": f"{run_dir}/dynamic_tools_public",
        }
    }
    async for msg_type, event in graph.astream(
        initial_state,
        config=config,
        stream_mode=["custom", "updates"],
    ):
        yield msg_type, event

FRONT_MATTER_DELIM = "---"
DEFAULT_CONFIG_PATH = Path("conf.yaml").resolve()
DEFAULT_PYPROJECT_PATH = Path("pyproject.toml").resolve()
DEFAULT_SKILLS_DIR = Path("example/cli/skills")
DEFAULT_TOKEN_LIMIT = 200000
DEFAULT_MODE = "auto"
DEFAULT_MODEL_TEMPS = {
    "BASIC_MODEL": 0.7,
    "EVAL_MODEL": 0.0,
    "VISION_MODEL": 0.7,
    "SUMMARIZE_MODEL": 0.2,
    "CLUSTER_MODEL": 0.2,
    "TOOL_ANALYZE_MODEL": 0.2,
}


class _Ansi:
    RESET = "\033[0m"
    DIM = "\033[2m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"


def _supports_color() -> bool:
    # CLI_COLOR can be: auto (default), always, never
    mode = (os.environ.get("CLI_COLOR") or "auto").strip().lower()
    if mode in ("never", "no", "false", "0", "off"):
        return False
    if mode in ("always", "yes", "true", "1", "on", "force"):
        return True

    # auto mode
    if "NO_COLOR" in os.environ:
        return False
    if not sys.stdout.isatty():
        return False
    term = (os.environ.get("TERM") or "").strip().lower()
    if term in ("", "dumb"):
        return False
    return True


def _color(text: str, code: str) -> str:
    if not _supports_color():
        return text
    return f"{code}{text}{_Ansi.RESET}"


def _indent_block(text: str, prefix: str = "  ") -> str:
    if not text:
        return ""
    return textwrap.indent(text, prefix)


def _format_tool_calls(tool_calls: Iterable[Dict[str, Any]]) -> str:
    lines: List[str] = []
    for tool_call in tool_calls:
        name = tool_call.get("name") or "unknown"
        args = tool_call.get("arguments", {})
        if isinstance(args, dict):
            args_text = json.dumps(args, ensure_ascii=True)
        else:
            args_text = json.dumps({"_raw": str(args)}, ensure_ascii=True)
        lines.append(f"- {name} {args_text}")
    return "\n".join(lines)


@dataclass
class _FormattedPayload:
    text: str
    spinner_message: Optional[str] = None


class _Spinner:
    def __init__(self, interval: float = 0.1) -> None:
        self._interval = interval
        self._task: Optional[asyncio.Task] = None
        self._stop_event: Optional[asyncio.Event] = None
        self._message = ""
        self._enabled = sys.stdout.isatty()

    def is_running(self) -> bool:
        return self._task is not None and not self._task.done()

    async def start(self, message: str) -> None:
        if not self._enabled:
            return
        await self.stop()
        self._message = self._truncate_message(message)
        self._stop_event = asyncio.Event()
        self._task = asyncio.create_task(self._spin())

    async def stop(self) -> None:
        if self._task and self._stop_event:
            self._stop_event.set()
            await self._task
        self._task = None
        self._stop_event = None

    async def _spin(self) -> None:
        frames = ["|", "/", "-", "\\"]
        idx = 0
        message = self._message
        stop_event = self._stop_event
        if not stop_event:
            return
        while not stop_event.is_set():
            sys.stdout.write(f"\r{message} {frames[idx % len(frames)]}")
            sys.stdout.flush()
            idx += 1
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=self._interval)
            except asyncio.TimeoutError:
                pass
        clear_len = max(self._terminal_width(), len(message) + 2)
        sys.stdout.write("\r" + (" " * clear_len) + "\r")
        sys.stdout.flush()

    @staticmethod
    def _terminal_width() -> int:
        try:
            return max(10, shutil.get_terminal_size((80, 20)).columns)
        except Exception:
            return 80

    def _truncate_message(self, message: str) -> str:
        width = self._terminal_width()
        max_len = max(10, width - 2)
        if len(message) <= max_len:
            return message
        return message[: max_len - 1] + "…"


def _summarize_pending_tools(pending: Iterable[Dict[str, Any]]) -> List[str]:
    names: List[str] = []
    for req in pending:
        name = req.get("name")
        if name:
            names.append(str(name))
    return names


def _format_payload(payload: Dict[str, Any]) -> _FormattedPayload:
    role = payload.get("role")
    message_type = payload.get("message_type")
    content = payload.get("content", "")

    if role == "executor" and message_type == "human":
        user_task = None
        if isinstance(content, str):
            marker = "User task:"
            if marker in content:
                after = content.split(marker, 1)[1]
                user_task = after.strip().splitlines()[0] if after.strip() else None
        header = _color("User", _Ansi.GREEN)
        body = _indent_block(user_task or str(content))
        return _FormattedPayload(f"{header}:\n{body}\n\n")

    if role == "executor" and message_type == "ai":
        header = _color("Assistant", _Ansi.CYAN)
        lines = [f"{header}:"]
        if content:
            lines.append(_indent_block(str(content)))
        tool_calls = payload.get("tool_calls") or []
        if tool_calls:
            lines.append(_indent_block("Tool calls:"))
            lines.append(_indent_block(_format_tool_calls(tool_calls), "    "))
        return _FormattedPayload("\n".join(lines) + "\n\n")

    if role == "executor" and message_type == "tool":
        header = _color("Tool response", _Ansi.YELLOW)
        tool_call_id = payload.get("tool_call_id")
        tool_msg_id = payload.get("tool_message_id")
        meta_bits = []
        if tool_call_id:
            meta_bits.append(f"call_id={tool_call_id}")
        if tool_msg_id:
            meta_bits.append(f"msg_id={tool_msg_id}")
        meta = f" ({', '.join(meta_bits)})" if meta_bits else ""
        body = _indent_block(str(content))
        return _FormattedPayload(f"{header}{meta}:\n{body}\n\n")

    if role == "executor" and message_type == "context_summary":
        header = _color("Context summary", _Ansi.DIM)
        body = _indent_block(str(content))
        return _FormattedPayload(f"{header}:\n{body}\n\n")

    if role == "manager" and message_type == "state_update":
        header = _color("Manager update", _Ansi.DIM)
        lines = [f"{header}:"]
        required = payload.get("required_tool_names") or []
        if required:
            lines.append(_indent_block(f"Required tools: {', '.join(required)}"))
        pending = payload.get("pending_tool_requests") or []
        spinner_message = None
        if pending:
            names = _summarize_pending_tools(pending)
            if names:
                spinner_message = f"Tool Developer is building {', '.join(names)}"
        usage = payload.get("tool_usage_guidance") or ""
        if usage:
            lines.append(_indent_block("Tool usage guidance:"))
            lines.append(_indent_block(usage, "    "))
        summary = payload.get("context_summary") or ""
        if summary:
            lines.append(_indent_block("Context summary:"))
            lines.append(_indent_block(summary, "    "))
        return _FormattedPayload("\n".join(lines) + "\n\n", spinner_message=spinner_message)

    if role == "tool_developer" and message_type == "state_update":
        header = _color("Tool developer update", _Ansi.DIM)
        lines = [f"{header}:"]
        created = payload.get("created_tools") or []
        if created:
            lines.append(_indent_block("Created tools:"))
            lines.append(_indent_block(json.dumps(created, ensure_ascii=True, indent=2), "    "))
        pending = payload.get("pending_tool_requests")
        spinner_message = None
        if pending:
            names = _summarize_pending_tools(pending)
            if names:
                spinner_message = f"Tool Developer is building {', '.join(names)}"
        return _FormattedPayload("\n".join(lines) + "\n\n", spinner_message=spinner_message)

    if role == "integrator" and message_type == "final_answer":
        header = _color("Final answer", _Ansi.GREEN)
        lines = [f"{header}:"]
        if content:
            lines.append(_indent_block(str(content)))
        reasoning = payload.get("reasoning_summary") or ""
        if reasoning:
            lines.append(_indent_block(_color("Reasoning summary:", _Ansi.DIM)))
            lines.append(_indent_block(reasoning, "    "))
        return _FormattedPayload("\n".join(lines) + "\n\n")

    header = _color(f"{role or 'event'}:{message_type or 'unknown'}", _Ansi.DIM)
    body = _indent_block(str(content))
    return _FormattedPayload(f"{header}\n{body}\n\n")


def _init_input_support() -> None:
    if not sys.stdin.isatty():
        return
    try:
        locale.setlocale(locale.LC_ALL, "")
    except locale.Error:
        pass
    try:
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _suppress_console_logging() -> None:
    logging.disable(logging.NOTSET)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    for handler in list(root_logger.handlers):
        if isinstance(handler, logging.StreamHandler):
            root_logger.removeHandler(handler)
    try:
        import readline  # pylint: disable=import-outside-toplevel

        readline.parse_and_bind("tab: complete")
        readline.parse_and_bind("set enable-keypad on")
        readline.clear_history()
    except Exception:
        pass


@dataclass(frozen=True)
class Skill:
    name: str
    path: Path
    metadata: Dict[str, Any]
    content: str


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _parse_front_matter(lines: List[str]) -> tuple[Dict[str, Any], List[str]]:
    if not lines or lines[0].strip() != FRONT_MATTER_DELIM:
        return {}, lines

    metadata_lines: List[str] = []
    body_start = 1
    for idx in range(1, len(lines)):
        if lines[idx].strip() == FRONT_MATTER_DELIM:
            body_start = idx + 1
            break
        metadata_lines.append(lines[idx])
    metadata = _parse_simple_yaml(metadata_lines)
    return metadata, lines[body_start:]


def _parse_simple_yaml(lines: Iterable[str]) -> Dict[str, Any]:
    metadata: Dict[str, Any] = {}
    current_key: Optional[str] = None
    for raw_line in lines:
        line = raw_line.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        stripped = line.lstrip()
        if stripped.startswith("- ") and current_key:
            metadata.setdefault(current_key, [])
            if not isinstance(metadata[current_key], list):
                metadata[current_key] = [metadata[current_key]]
            metadata[current_key].append(stripped[2:].strip())
            continue

        if ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            current_key = key
            if value == "":
                metadata[key] = []
            else:
                metadata[key] = _strip_quotes(value)
            continue

    return metadata


def _strip_quotes(value: str) -> str:
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def _get_cli_version() -> str:
    if not DEFAULT_PYPROJECT_PATH.exists():
        return "unknown"
    try:
        data = tomllib.loads(_read_text(DEFAULT_PYPROJECT_PATH))
    except (OSError, tomllib.TOMLDecodeError):
        return "unknown"
    project = data.get("project", {})
    version = project.get("version")
    return str(version) if version else "unknown"


def _skill_name_from_metadata(metadata: Dict[str, Any], path: Path) -> str:
    for key in ("name", "title", "skill", "id"):
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return path.parent.name or path.stem


def load_skills(skills_dir: Path) -> List[Skill]:
    if not skills_dir.exists():
        raise FileNotFoundError(f"Skills directory not found: {skills_dir}")

    skill_files = sorted(skills_dir.rglob("SKILL.md"))
    skills: List[Skill] = []
    used_names: Dict[str, int] = {}
    for skill_path in skill_files:
        content = _read_text(skill_path)
        lines = content.splitlines()
        metadata, body_lines = _parse_front_matter(lines)
        name = _skill_name_from_metadata(metadata, skill_path)
        normalized = name.strip().lower()
        if normalized in used_names:
            used_names[normalized] += 1
            name = f"{name}-{used_names[normalized]}"
        else:
            used_names[normalized] = 1
        skills.append(
            Skill(
                name=name,
                path=skill_path,
                metadata=metadata,
                content="\n".join(body_lines).strip() or content.strip(),
            )
        )
    return skills


def build_selection_prompt(skills: List[Skill], user_task: str) -> str:
    metadata_payload = [
        {
            "name": skill.name,
            "metadata": skill.metadata,
        }
        for skill in skills
    ]
    metadata_json = json.dumps(metadata_payload, ensure_ascii=True, indent=2)
    return (
        "You are a skill router. Given a list of skill metadata and a user task, "
        "select the skills that are strictly necessary to complete the task. "
        "If none are needed, return an empty list.\n\n"
        "Return ONLY a JSON array of skill names, with no extra text.\n\n"
        f"Skill metadata list (JSON):\n{metadata_json}\n\n"
        f"User task:\n{user_task}\n"
    )


def _parse_skill_names(response_text: str) -> List[str]:
    text = response_text.strip()
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return [
                item.get("name", "")
                if isinstance(item, dict)
                else str(item)
                for item in data
            ]
    except json.JSONDecodeError:
        pass

    cleaned = text.strip("[]")
    candidates = [part.strip() for part in cleaned.replace("\n", ",").split(",")]
    return [c for c in candidates if c]

def select_skills_auto(skills: List[Skill], user_task: str) -> List[Skill]:
    if not skills:
        return []
    prompt = build_selection_prompt(skills, user_task)
    llm = create_llm(LLMType.BASIC)
    response = llm.invoke(
        [
            SystemMessage(
                content="You are a precise selector. Follow the output format."
            ),
            HumanMessage(content=prompt),
        ]
    )
    response_text = response.content if hasattr(response, "content") else str(response)
    names = _parse_skill_names(response_text)
    name_map = {skill.name.lower(): skill for skill in skills}
    selected = []
    for name in names:
        normalized = name.strip().lower()
        if normalized in name_map:
            selected.append(name_map[normalized])
    return selected


def select_skills_manual(skills: List[Skill]) -> List[Skill]:
    if not skills:
        return []
    return _select_skills_interactive(skills)


def build_final_prompt(selected_skills: List[Skill], user_task: str) -> str:
    sections = [
        "Instruction:",
        "You should make your best effort to complete the user's task.",
        "Follow the provided skills. If a required tool is missing to implement a skill, create the tool yourself.",
        "When creating new tools, prefer the approaches and implementation patterns described in the SKILL(s).",
        "If your solution depends on command-line tools, include bootstrap/install logic because the tool may not be available on the machine.",
        "If a skill requires local machine capabilities, prefer AppleScript or Bash.",
        "",
        "User task:",
        user_task,
        "",
        "Selected skills (full content):",
    ]
    for skill in selected_skills:
        sections.append(f"=== Skill: {skill.name} ({skill.path}) ===")
        sections.append(skill.content)
        sections.append("")
    return "\n".join(sections).strip() + "\n"


def _print_skill_list(skills: List[Skill]) -> None:
    if not skills:
        print("No skills found.")
        return
    for skill in skills:
        summary = (
            skill.metadata.get("description") or skill.metadata.get("summary") or ""
        )
        print(f"- {skill.name} ({skill.path}){(' - ' + summary) if summary else ''}")


def _resolve_task() -> str:
    if sys.stdin.isatty():
        content = input("Enter user task: ").strip()
    else:
        print("Enter user task, finish with EOF (Ctrl+D):")
        content = sys.stdin.read().strip()
    if not content:
        raise ValueError("User task cannot be empty.")
    return content


def _select_mode_interactive(default: str = DEFAULT_MODE) -> str:
    options = ["auto", "manual"]
    default = default if default in options else DEFAULT_MODE
    prompt = (
        "Select skill mode:\n"
        "  1) auto\n"
        "  2) manual\n"
        f"Enter choice [default: {default}]: "
    )
    while True:
        choice = input(prompt).strip().lower()
        if not choice:
            return default
        if choice in ("1", "auto", "a"):
            return "auto"
        if choice in ("2", "manual", "m"):
            return "manual"
        print("Invalid choice. Please enter 1 or 2.")


def _select_mode(default: str = DEFAULT_MODE) -> str:
    if not sys.stdin.isatty():
        return default
    return _select_mode_interactive(default)

def _compose_banner_box(config: Dict[str, Any], skills_dir: Optional[Path] = None, mode: Optional[str] = None, allowed_skills: Optional[List[Skill]] = None, colorize: bool = True) -> List[str]:
    version = _get_cli_version()
    model = _get_primary_model_name(config)
    lines = ["Yunjue Tech", f"model: {model}"]
    if skills_dir is not None:
        lines.append(f"skills: {skills_dir}")
    if mode is not None:
        lines.append(f"mode: {mode}")
    if allowed_skills is not None:
        lines.append(f"allowed skills: {len(allowed_skills)}")
    width = max(len(line) for line in lines)
    box = [f"+{'-' * (width + 2)}+"]
    for line in lines:
        padding = " " * (width - len(line))
        box.append(f"| {line}{padding} |")
    box.append(f"+{'-' * (width + 2)}+")
    header = _color(f"Yunjue CLI v{version}", _Ansi.CYAN) if colorize else f"Yunjue CLI v{version}"
    return [header] + box + [""]

def _menu_select_list(title: str, options: List[str], banner_box_lines: Optional[List[str]] = None) -> int:
    import curses
    ansi_re = re.compile(r"\x1b\[[0-9;]*m")
    def run(stdscr):
        curses.curs_set(0)
        color_attr = 0
        if _supports_color():
            try:
                if curses.has_colors():
                    curses.start_color()
                    try:
                        curses.use_default_colors()
                    except Exception:
                        pass
                    curses.init_pair(1, curses.COLOR_CYAN, -1)
                    color_attr = curses.color_pair(1) | curses.A_BOLD
            except Exception:
                color_attr = 0
        idx = 0
        while True:
            stdscr.clear()
            start_row = 0
            if banner_box_lines:
                for i, line in enumerate(banner_box_lines):
                    clean = ansi_re.sub("", str(line))
                    max_width = max(1, (curses.COLS or 80) - 1)
                    clean = clean[:max_width]
                    try:
                        if i == 0 and color_attr:
                            stdscr.addstr(start_row + i, 0, clean, color_attr)
                        else:
                            stdscr.addstr(start_row + i, 0, clean)
                    except curses.error:
                        pass
                start_row += len(banner_box_lines)
            try:
                stdscr.addstr(start_row, 0, title[: max(1, (curses.COLS or 80) - 1)])
            except curses.error:
                pass
            for i, opt in enumerate(options):
                marker = "> " if i == idx else "  "
                line = f"{marker}{opt}"
                try:
                    stdscr.addstr(start_row + 2 + i, 0, line[: max(1, (curses.COLS or 80) - 1)])
                except curses.error:
                    pass
            stdscr.refresh()
            ch = stdscr.getch()
            if ch in (curses.KEY_UP, ord("k")):
                idx = (idx - 1) % len(options)
            elif ch in (curses.KEY_DOWN, ord("j")):
                idx = (idx + 1) % len(options)
            elif ch in (curses.KEY_ENTER, 10, 13):
                return idx
    return curses.wrapper(run)

def _multi_select_list(title: str, items: List[str], banner_box_lines: Optional[List[str]] = None) -> Optional[List[int]]:
    import curses
    ansi_re = re.compile(r"\x1b\[[0-9;]*m")
    def run(stdscr):
        curses.curs_set(0)
        color_attr = 0
        if _supports_color():
            try:
                if curses.has_colors():
                    curses.start_color()
                    try:
                        curses.use_default_colors()
                    except Exception:
                        pass
                    curses.init_pair(1, curses.COLOR_CYAN, -1)
                    color_attr = curses.color_pair(1) | curses.A_BOLD
            except Exception:
                color_attr = 0
        idx = 0
        selected: set[int] = set()
        back_idx = len(items)  # last is Back
        options = items + ["Back"]
        while True:
            stdscr.clear()
            start_row = 0
            if banner_box_lines:
                for i, line in enumerate(banner_box_lines):
                    clean = ansi_re.sub("", str(line))
                    max_width = max(1, (curses.COLS or 80) - 1)
                    clean = clean[:max_width]
                    try:
                        if i == 0 and color_attr:
                            stdscr.addstr(start_row + i, 0, clean, color_attr)
                        else:
                            stdscr.addstr(start_row + i, 0, clean)
                    except curses.error:
                        pass
                start_row += len(banner_box_lines)
            try:
                stdscr.addstr(start_row, 0, title[: max(1, (curses.COLS or 80) - 1)])
            except curses.error:
                pass
            for i, opt in enumerate(options):
                prefix = "[x] " if i in selected else "[ ] "
                if i == back_idx:
                    prefix = "    "
                marker = "> " if i == idx else "  "
                line = f"{marker}{prefix}{opt}"
                try:
                    stdscr.addstr(start_row + 2 + i, 0, line[: max(1, (curses.COLS or 80) - 1)])
                except curses.error:
                    pass
            try:
                stdscr.addstr(start_row + 3 + len(options), 0, "Space=toggle, Enter=confirm"[: max(1, (curses.COLS or 80) - 1)])
            except curses.error:
                pass
            stdscr.refresh()
            ch = stdscr.getch()
            if ch in (curses.KEY_UP, ord("k")):
                idx = (idx - 1) % len(options)
            elif ch in (curses.KEY_DOWN, ord("j")):
                idx = (idx + 1) % len(options)
            elif ch == ord(" "):
                if idx != back_idx:
                    if idx in selected:
                        selected.remove(idx)
                    else:
                        selected.add(idx)
            elif ch in (curses.KEY_ENTER, 10, 13):
                if idx == back_idx:
                    return None
                return sorted(i for i in selected if i != back_idx)
    return curses.wrapper(run)

def _select_skills_dir_interactive(default: Path = DEFAULT_SKILLS_DIR) -> Path:
    prompt = (
        "Select skills directory:\n"
        f"  1) default: {str(default)}\n"
        "  2) custom\n"
        "Enter choice [default: 1]: "
    )
    while True:
        choice = input(prompt).strip().lower()
        if not choice:
            return default.expanduser().resolve()
        if choice in ("1", "default", "d"):
            return default.expanduser().resolve()
        if choice in ("2", "custom", "c"):
            entered = _prompt_required("Skills directory", default=str(default))
            return Path(entered).expanduser().resolve()
        print("Invalid choice. Please enter 1 or 2.")

def _select_skills_dir(default: Path = DEFAULT_SKILLS_DIR) -> Path:
    if not sys.stdin.isatty():
        return default.expanduser().resolve()
    return _select_skills_dir_interactive(default)

def _select_skills_dir_interactive_list(default: Path = DEFAULT_SKILLS_DIR, banner_box_lines: Optional[List[str]] = None) -> Optional[Path]:
    options = [f"default: {str(default)}", "custom", "Back"]
    idx = _menu_select_list("Select skills directory:", options, banner_box_lines)
    if idx == 0:
        return default.expanduser().resolve()
    if idx == 1:
        entered = _prompt_required("Skills directory", default=str(default))
        return Path(entered).expanduser().resolve()
    return None

def _select_mode_interactive_list(default: str = DEFAULT_MODE, banner_box_lines: Optional[List[str]] = None) -> Optional[str]:
    options = ["auto", "manual", "Back"]
    idx = _menu_select_list("Select skill mode:", options, banner_box_lines)
    if idx == 2:
        return None
    return options[idx]


def _prompt_required(label: str, default: Optional[str] = None, secret: bool = False) -> str:
    while True:
        suffix = f" [{default}]" if default else ""
        prompt = f"{label}{suffix}: "
        try:
            value = input(prompt)
        except EOFError:
            value = ""
        value = value.strip()
        if value:
            return value
        if default:
            return default
        print(f"{label} cannot be empty.")


def _build_config_payload(base_url: str, api_key: str, model: str) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    for key, temp in DEFAULT_MODEL_TEMPS.items():
        payload[key] = {
            "base_url": base_url,
            "model": model,
            "api_key": api_key,
            "temperature": temp,
            "token_limit": DEFAULT_TOKEN_LIMIT,
        }
    return payload


def _get_primary_model_name(config: Dict[str, Any]) -> str:
    model = ""
    if isinstance(config.get("BASIC_MODEL"), dict):
        model = str(config.get("BASIC_MODEL", {}).get("model") or "")
    return model or "not configured"


def _print_banner(config: Dict[str, Any]) -> None:
    version = _get_cli_version()
    model = _get_primary_model_name(config)
    lines = [
        "Yunjue Tech",
        f"model: {model}",
    ]
    width = max(len(line) for line in lines)
    print(_color(f"Yunjue CLI v{version}", _Ansi.CYAN))
    print(f"+{'-' * (width + 2)}+")
    for line in lines:
        padding = " " * (width - len(line))
        print(f"| {line}{padding} |")
    print(f"+{'-' * (width + 2)}+")
    print()


def _write_yaml_config(config_path: Path, payload: Dict[str, Any]) -> None:
    config_path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=False),
        encoding="utf-8",
    )


def _has_valid_model_config(config: Dict[str, Any]) -> bool:
    required = ("base_url", "api_key", "model")
    for key in DEFAULT_MODEL_TEMPS.keys():
        model_block = config.get(key)
        if not isinstance(model_block, dict):
            return False
        if not all(bool(model_block.get(item)) for item in required):
            return False
    return True


def _load_existing_config() -> Dict[str, Any]:
    if not DEFAULT_CONFIG_PATH.exists():
        return {}
    config = load_yaml_config(str(DEFAULT_CONFIG_PATH))
    if _has_valid_model_config(config):
        print(f"Loaded config from {DEFAULT_CONFIG_PATH}")
    else:
        print(f"Config found at {DEFAULT_CONFIG_PATH} but missing required fields.")
    return config


def _read_cli_mode(config: Dict[str, Any]) -> Optional[str]:
    mode = config.get("CLI_MODE")
    if isinstance(mode, str) and mode in ("auto", "manual"):
        return mode
    return None


def _persist_cli_mode(mode: str) -> None:
    payload: Dict[str, Any] = {}
    if DEFAULT_CONFIG_PATH.exists():
        payload = load_yaml_config(str(DEFAULT_CONFIG_PATH)) or {}
    payload["CLI_MODE"] = mode
    _write_yaml_config(DEFAULT_CONFIG_PATH, payload)

def _persist_skills_dir(skills_dir: Path) -> None:
    payload: Dict[str, Any] = {}
    if DEFAULT_CONFIG_PATH.exists():
        payload = load_yaml_config(str(DEFAULT_CONFIG_PATH)) or {}
    payload["SKILLS_DIR"] = str(skills_dir)
    _write_yaml_config(DEFAULT_CONFIG_PATH, payload)


def _ensure_skills_dir_exists(skills_dir: Path) -> None:
    """Create skills_dir if it doesn't exist (mkdir -p).

    If the path exists but is not a directory, raise.
    """
    skills_dir = skills_dir.expanduser()
    if skills_dir.exists() and not skills_dir.is_dir():
        raise NotADirectoryError(f"SKILLS_DIR is not a directory: {skills_dir}")
    if not skills_dir.exists():
        skills_dir.mkdir(parents=True, exist_ok=True)


def _configure_model_interactive(mode: str) -> None:
    if not sys.stdin.isatty():
        raise RuntimeError("Missing conf.yaml and cannot prompt in non-interactive mode.")
    print("Model config not found. Let's set it up.")
    print(f"Selected skill mode: {mode}")
    base_url = _prompt_required("Base URL (e.g., https://api.openai.com/v1)")
    api_key = _prompt_required("API key")
    model = _prompt_required("Model name (e.g., gpt-5)")
    payload = _build_config_payload(base_url, api_key, model)
    payload["CLI_MODE"] = mode
    _write_yaml_config(DEFAULT_CONFIG_PATH, payload)
    print(f"Saved config to {DEFAULT_CONFIG_PATH}")


def _print_repl_help() -> None:
    print("Commands:")
    print(_color("  /help   Show this help", _Ansi.DIM))
    print(_color("  /skills List available skills", _Ansi.DIM))
    print(_color("  /mode   Switch skill selection mode", _Ansi.DIM))
    print(_color("  /model  Switch model name", _Ansi.DIM))
    print(_color("  /exit   Quit", _Ansi.DIM))
    print()


def _print_selected_skills(selected_skills: List[Skill]) -> None:
    if not selected_skills:
        print(_color("Selected skills: none", _Ansi.DIM))
        return
    print(_color("Selected skills:", _Ansi.DIM))
    for skill in selected_skills:
        summary = (
            skill.metadata.get("description")
            or skill.metadata.get("summary")
            or ""
        )
        summary = summary.replace("\n", " ").strip()
        if summary:
            print(f"- {skill.name}: {summary}")
        else:
            print(f"- {skill.name}")
    print()


async def _run_task_with_live_output(
    user_input: str, run_dir: Path, task_id: str = "default"
) -> str:
    log_file = run_dir / "logs" / f"task_{task_id}.log"
    if log_file.exists():
        try:
            log_file.unlink()
        except OSError:
            pass
    try:
        parser = EventParser()
        spinner = _Spinner()
        async for msg_type, event in graph_event_stream(user_input, task_id, run_dir):
            payloads = parser.parse(msg_type, event)
            for payload in payloads:
                formatted = _format_payload(payload)
                if spinner.is_running():
                    await spinner.stop()
                if formatted.text:
                    print(formatted.text, end="", flush=True)
                if formatted.spinner_message:
                    await spinner.start(formatted.spinner_message)
    finally:
        if "spinner" in locals():
            await spinner.stop()


def _list_available_models(config: Dict[str, Any]) -> List[str]:
    models: set[str] = set()
    for key in DEFAULT_MODEL_TEMPS.keys():
        block = config.get(key)
        if isinstance(block, dict):
            name = block.get("model")
            if isinstance(name, str) and name.strip():
                models.add(name.strip())
    return sorted(models)


def _select_model_interactive(config: Dict[str, Any]) -> str:
    current = _get_primary_model_name(config)
    models = _list_available_models(config)
    print(_color(f"Current model: {current}", _Ansi.DIM))
    if models:
        print("Available models:")
        for idx, name in enumerate(models, start=1):
            print(f"  {idx}) {name}")
        print("  c) custom")
        choice = input("Choose a model [enter to keep current]: ").strip().lower()
        if not choice:
            return current
        if choice in ("c", "custom"):
            return _prompt_required("Model name")
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(models):
                return models[idx - 1]
        print("Invalid choice. Using current model.")
        return current
    default_value = current if current != "not configured" else None
    return _prompt_required("Model name", default=default_value)


def _update_model_in_config(config: Dict[str, Any], model: str) -> Dict[str, Any]:
    for key in DEFAULT_MODEL_TEMPS.keys():
        block = config.get(key)
        if not isinstance(block, dict):
            block = {}
        block["model"] = model
        config[key] = block
    return config


def _run_task_with_mode(skills: List[Skill], mode: str, user_task: str, allowed_skills: Optional[List[Skill]] = None) -> None:
    pool = allowed_skills if allowed_skills is not None else skills
    if mode == "manual":
        selected_skills = select_skills_auto(pool, user_task)
    else:
        selected_skills = select_skills_auto(pool, user_task)
    _print_selected_skills(selected_skills)
    final_prompt = build_final_prompt(selected_skills, user_task)
    run_dir = Path("output/cli").expanduser().resolve()
    if not os.path.exists(run_dir):
        os.makedirs(run_dir, exist_ok=True)
    final_answer = asyncio.run(
        _run_task_with_live_output(final_prompt, run_dir, task_id="default")
    )
    answer_text = final_answer
    if isinstance(final_answer, str):
        try:
            parsed = json.loads(final_answer)
            if isinstance(parsed, dict) and "final_answer" in parsed:
                answer_text = parsed["final_answer"]
        except json.JSONDecodeError:
            pass
    print(_color("Final answer:", _Ansi.DIM))
    print(_color(str(answer_text), _Ansi.GREEN))


def _interactive_loop(skills: List[Skill], mode: str, allowed_skills: Optional[List[Skill]] = None) -> None:
    print(_color("Ready. Type your task in natural language.", _Ansi.DIM))
    _print_repl_help()
    print(_color("Describe a task or type /help.", _Ansi.DIM))
    while True:
        try:
            user_input = input(_color(">>> ", _Ansi.GREEN)).strip()
        except EOFError:
            print("\nBye.")
            return

        if not user_input:
            continue
        if user_input in ("/exit", "/quit"):
            print("Bye.")
            return
        if user_input == "/help":
            _print_repl_help()
            continue
        if user_input == "/skills":
            _print_skill_list(allowed_skills if allowed_skills is not None else skills)
            continue
        if user_input == "/mode":
            mode = _select_mode(mode)
            _persist_cli_mode(mode)
            print(_color(f"Switched to {mode} mode.", _Ansi.YELLOW))
            continue
        if user_input == "/model":
            config = _load_existing_config()
            new_model = _select_model_interactive(config)
            updated = _update_model_in_config(config, new_model)
            _write_yaml_config(DEFAULT_CONFIG_PATH, updated)
            print(_color(f"Switched model to {new_model}", _Ansi.YELLOW))
            continue
        resolved_task = user_input
        if not resolved_task:
            print(_color("Cancelled.", _Ansi.DIM))
            continue
        _run_task_with_mode(skills, mode, resolved_task, allowed_skills=allowed_skills)
        print(_color("Done. You can enter another task.", _Ansi.DIM))


def _select_skills_interactive(skills: List[Skill]) -> List[Skill]:
    if not skills:
        return []

    print("Select skills for this task.")
    for idx, skill in enumerate(skills, start=1):
        summary = (
            skill.metadata.get("description")
            or skill.metadata.get("summary")
            or ""
        )
        summary = summary.replace("\n", " ")
        summary = textwrap.shorten(summary, width=60, placeholder="...")
        line = f"{idx}) {skill.name}"
        if summary:
            line = f"{line} - {summary}"
        print(line)

    print("Enter numbers separated by comma/space, or 'all', 'none'.")
    while True:
        raw = input("Your choice: ").strip().lower()
        if not raw or raw in ("none", "n"):
            return []
        if raw in ("all", "a"):
            return skills
        parts = [p for p in raw.replace(",", " ").split(" ") if p]
        indices: List[int] = []
        for part in parts:
            if part.isdigit():
                indices.append(int(part))
        if not indices:
            print("Invalid input. Example: 1 3 5")
            continue
        selected = []
        for idx in indices:
            if 1 <= idx <= len(skills):
                selected.append(skills[idx - 1])
        if not selected:
            print("No valid selections. Try again.")
            continue
        return selected


def main() -> None:
    _init_input_support()
    _suppress_console_logging()
    config = _load_existing_config()
    _print_banner(config)
    if sys.stdin.isatty():
        while True:
            raw_skills_dir = config.get("SKILLS_DIR")
            if not isinstance(raw_skills_dir, str) or not raw_skills_dir.strip():
                banner_lines = _compose_banner_box(config, colorize=False)
                chosen = _select_skills_dir_interactive_list(DEFAULT_SKILLS_DIR, banner_box_lines=banner_lines)
                if chosen is None:
                    # User chose "Back" on the first screen; exit gracefully.
                    print("Bye.")
                    return
                else:
                    skills_dir = chosen
                    _ensure_skills_dir_exists(skills_dir)
                    _persist_skills_dir(skills_dir)
                    config = _load_existing_config()
            else:
                skills_dir = Path(str(raw_skills_dir)).expanduser().resolve()
            try:
                _ensure_skills_dir_exists(skills_dir)
            except NotADirectoryError as e:
                print(str(e))
                banner_lines = _compose_banner_box(config, colorize=False)
                chosen = _select_skills_dir_interactive_list(DEFAULT_SKILLS_DIR, banner_box_lines=banner_lines)
                if chosen is None:
                    continue
                skills_dir = chosen
                _ensure_skills_dir_exists(skills_dir)
                _persist_skills_dir(skills_dir)
                config = _load_existing_config()
            skills = load_skills(skills_dir)
            if not skills:
                _print_skill_list(skills)
                return
            mode = _read_cli_mode(config)
            if not mode:
                banner_lines = _compose_banner_box(config, skills_dir=skills_dir, colorize=False)
                m = _select_mode_interactive_list(DEFAULT_MODE, banner_box_lines=banner_lines)
                if m is None:
                    continue
                mode = m
                _persist_cli_mode(mode)
                config = _load_existing_config()
            allowed_skills: Optional[List[Skill]] = None
            if mode == "manual":
                names = [s.name for s in skills]
                banner_lines = _compose_banner_box(config, skills_dir=skills_dir, mode=mode, colorize=False)
                sel = _multi_select_list("Select allowed skills:", names, banner_box_lines=banner_lines)
                if sel is None:
                    banner_lines = _compose_banner_box(config, skills_dir=skills_dir, colorize=False)
                    m = _select_mode_interactive_list(DEFAULT_MODE, banner_box_lines=banner_lines)
                    if m is None:
                        continue
                    mode = m
                    _persist_cli_mode(mode)
                else:
                    allowed_skills = [skills[i] for i in sel]
            if _has_valid_model_config(config):
                pass
            else:
                _configure_model_interactive(mode)
            if sys.stdin.isatty():
                _interactive_loop(skills, mode, allowed_skills=allowed_skills)
                return
            user_task = _resolve_task()
            _run_task_with_mode(skills, mode, user_task, allowed_skills=allowed_skills)
            return
    raw_skills_dir = config.get("SKILLS_DIR")
    if not isinstance(raw_skills_dir, str) or not raw_skills_dir.strip():
        skills_dir = _select_skills_dir(DEFAULT_SKILLS_DIR)
        _ensure_skills_dir_exists(skills_dir)
        _persist_skills_dir(skills_dir)
    else:
        skills_dir = Path(str(raw_skills_dir)).expanduser().resolve()
    try:
        _ensure_skills_dir_exists(skills_dir)
    except NotADirectoryError as e:
        print(str(e))
        if sys.stdin.isatty():
            skills_dir = _select_skills_dir(DEFAULT_SKILLS_DIR)
            _ensure_skills_dir_exists(skills_dir)
            _persist_skills_dir(skills_dir)
        else:
            raise
    skills = load_skills(skills_dir)

    if not skills:
        _print_skill_list(skills)
        return

    mode = _read_cli_mode(config)
    if not mode:
        mode = _select_mode(DEFAULT_MODE)
        _persist_cli_mode(mode)
    allowed_skills: Optional[List[Skill]] = None
    if mode == "manual" and sys.stdin.isatty():
        allowed_skills = _select_skills_interactive(skills)

    if _has_valid_model_config(config):
        pass
    else:
        _configure_model_interactive(mode)

    if sys.stdin.isatty():
        _interactive_loop(skills, mode, allowed_skills=allowed_skills)
        return

    user_task = _resolve_task()
    _run_task_with_mode(skills, mode, user_task, allowed_skills=allowed_skills)


if __name__ == "__main__":
    main()
