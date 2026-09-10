"""Run MatTools real-world tasks with Claude Code in method1 read-only mode.

This runner intentionally writes the same evaluator-facing JSONL contract as
pure_agent_test/build_agent.py:

  {"question_file_path": "...", "function": "...", "function_name": "..."}

Claude Code may inspect the MatTools method1/code corpus with read-only tools.
Additional raw Claude outputs are saved beside the evaluator file for debugging.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from tqdm import tqdm
except Exception:  # pragma: no cover - tqdm is optional for harness use.
    def tqdm(iterable, **_: Any):  # type: ignore
        return iterable


SRC_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SRC_ROOT.parents[3]
BASE_QUESTIONS_DIR = SRC_ROOT / "question_segments" / "pymatgen_analysis_defects"
DEFAULT_OUTPUT_ROOT = SRC_ROOT / "claude_cli_test"
DEFAULT_CLAUDE_BIN = REPO_ROOT / "scripts" / "claude-code.sh"
CLAUDE_CONDITION = "method1_read_only"
METHOD1_CORPUS_DIR = SRC_ROOT / "tool_source_code" / "pymatgen" / "src" / "pymatgen"
METHOD1_CORPUS_RELATIVE = "tool_source_code/pymatgen/src/pymatgen"
ALLOWED_TOOLS = ["Read", "Grep", "Glob"]
DEFAULT_CLAUDE_ARGS = [
    "--no-session-persistence",
    "--setting-sources",
    "",
    "--output-format",
    "stream-json",
    "--verbose",
    "--disable-slash-commands",
    "--tools",
    ",".join(ALLOWED_TOOLS),
    "--permission-mode",
    "dontAsk",
]
BLOCKED_ACCESS_DESCRIPTIONS = [
    "code_segments",
    "tool_source_code/pymatgen-analysis-defects/tests/**/*.py",
]

ANSWER_FORMAT = """**Answer format**:
Please make sure the response is enclosed within `<answer>`, `<code>` and `<name>` tags. Follow this example format:

<answer>
<code>
```python
# The generated function code
def example_function():
    pass
```
</code>
<name>name_of_generated_function</name>
</answer>"""

MATTOOLS_CLAUDE_INSTRUCTIONS = """Additional requirements for MatTools evaluation:
1. Generate exactly one zero-argument Python function.
2. The function must return a non-empty Python dict.
3. Do not call the function, do not print anything, and do not include tests.
4. Put only the generated function code inside the `<code>` block.
5. Put the exact generated function name inside the `<name>` tag."""

METHOD1_READ_ONLY_INSTRUCTIONS = """Claude Code read-only source access:
1. This run is the MatTools method1/code-corpus condition.
2. You have read-only Claude Code tools available: Read, Grep, and Glob.
3. The local pymatgen source corpus has been added to this session. Use it as
   reference material when API details matter:
   `{corpus_dir}`.
4. Before writing the final function, inspect the relevant local source files
   for the classes, functions, properties, or return types needed by the task.
5. Use Glob for file discovery and Grep for text search; do not assume an LS
   tool is available.
6. Do not run shell commands, Python code, tests, or executable probes.
7. Do not edit, create, delete, or overwrite files.
8. Do not inspect answer-leaking test/code-generation sources, including:
   `code_segments/`, `tool_source_code/pymatgen-analysis-defects/tests/*.py`,
   and `tool_source_code/pymatgen-analysis-defects/tests/plotting/*.py`.
9. You may still use file paths mentioned in the question as paths inside the
   generated function; just do not inspect test assertion files while solving."""


def load_questions_path_from_directories(base_dir: Path) -> list[Path]:
    """Mirror the original MatTools os.walk task ordering."""
    return [
        Path(root) / "question.txt"
        for root, _, files in os.walk(base_dir)
        if "question.txt" in files
    ]


def build_prompt(question: str) -> str:
    return "\n\n".join(
        [
            question.strip(),
            METHOD1_READ_ONLY_INSTRUCTIONS.format(corpus_dir=METHOD1_CORPUS_RELATIVE),
            ANSWER_FORMAT,
            MATTOOLS_CLAUDE_INSTRUCTIONS,
        ]
    ).strip() + "\n"


def extract_stream_json_text(stdout: str) -> str:
    """Extract assistant text from Claude Code --output-format stream-json output."""
    if not stdout or not stdout.lstrip().startswith("{"):
        return stdout or ""

    text_chunks: list[str] = []
    assistant_texts: list[str] = []
    result_texts: list[str] = []
    saw_json = False
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            return stdout
        if not isinstance(obj, dict):
            return stdout
        saw_json = True

        event = obj.get("event")
        if isinstance(event, dict):
            delta = event.get("delta")
            if isinstance(delta, dict) and delta.get("type") == "text_delta":
                text_chunks.append(str(delta.get("text") or ""))

        message = obj.get("message")
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        assistant_texts.append(str(block.get("text") or ""))

        if obj.get("type") == "result" and obj.get("result"):
            result_texts.append(str(obj.get("result") or ""))

    if text_chunks:
        return "".join(text_chunks)
    if assistant_texts:
        return "\n".join(dedupe_preserve_order(text for text in assistant_texts if text))
    if result_texts:
        return "\n".join(dedupe_preserve_order(text for text in result_texts if text))
    return "" if saw_json else stdout


def dedupe_preserve_order(values: Any) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


def extract_response(response: str) -> tuple[str, str]:
    """Extract generated function code and function name from Claude text."""
    if not response:
        return "", ""

    code_match = re.search(
        r"<code>\s*```(?:python)?\s*(.*?)```\s*</code>",
        response,
        re.DOTALL | re.IGNORECASE,
    )
    if not code_match:
        code_match = re.search(r"<code>\s*(.*?)\s*</code>", response, re.DOTALL | re.IGNORECASE)
    name_match = re.search(r"<name>\s*(.*?)\s*</name>", response, re.DOTALL | re.IGNORECASE)
    if not code_match or not name_match:
        return "", ""
    return code_match.group(1).strip(), name_match.group(1).strip()


def coerce_output_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def parse_stream_json_events(stdout: str) -> list[dict[str, Any]]:
    if not stdout or not stdout.lstrip().startswith("{"):
        return []

    events: list[dict[str, Any]] = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            return []
        if not isinstance(obj, dict):
            return []
        events.append(obj)
    return events


def compact_text(text: Any, limit: int = 240) -> str:
    value = coerce_output_text(text).replace("\n", "\\n")
    if len(value) <= limit:
        return value
    return value[: limit - 3] + "..."


def stringify_tool_input(value: Any) -> str:
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    except Exception:
        return str(value)


def is_blocked_access(value: Any) -> str | None:
    input_text = stringify_tool_input(value).replace("\\", "/").lower()
    if "code_segments" in input_text:
        return "code_segments"
    tests_marker = "tool_source_code/pymatgen-analysis-defects/tests/"
    if tests_marker in input_text and ".py" in input_text:
        return "tool_source_code/pymatgen-analysis-defects/tests/**/*.py"
    if "pymatgen-analysis-defects/tests/plotting/" in input_text and ".py" in input_text:
        return "tool_source_code/pymatgen-analysis-defects/tests/**/*.py"
    return None


def build_tool_usage_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    system_event = next((event for event in events if event.get("type") == "system"), {})
    tool_uses: list[dict[str, Any]] = []
    tool_results = 0
    tool_results_by_id: dict[str, dict[str, Any]] = {}

    for event_index, event in enumerate(events):
        message = event.get("message")
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for block_index, block in enumerate(content):
            if not isinstance(block, dict):
                continue
            block_type = block.get("type")
            if block_type == "tool_use":
                tool_uses.append(
                    {
                        "event_index": event_index,
                        "block_index": block_index,
                        "id": block.get("id"),
                        "name": block.get("name"),
                        "input": block.get("input"),
                    }
                )
            elif block_type == "tool_result":
                tool_results += 1
                tool_use_id = block.get("tool_use_id")
                if isinstance(tool_use_id, str):
                    tool_results_by_id[tool_use_id] = block

    violations: list[dict[str, Any]] = []
    disallowed_tool_uses: list[dict[str, Any]] = []
    successful_read_files: list[str] = []
    for tool_use in tool_uses:
        tool_name = str(tool_use.get("name") or "")
        if tool_name not in ALLOWED_TOOLS:
            disallowed_tool_uses.append(
                {
                    "tool_use_id": tool_use.get("id"),
                    "tool": tool_name,
                    "input_preview": compact_text(stringify_tool_input(tool_use.get("input"))),
                }
            )

        blocked_pattern = is_blocked_access(tool_use.get("input"))
        if blocked_pattern:
            violations.append(
                {
                    "tool_use_id": tool_use.get("id"),
                    "tool": tool_name,
                    "pattern": blocked_pattern,
                    "input_preview": compact_text(stringify_tool_input(tool_use.get("input"))),
                }
            )

        result = tool_results_by_id.get(str(tool_use.get("id") or ""))
        if tool_name == "Read" and result and not result.get("is_error"):
            tool_input = tool_use.get("input")
            if isinstance(tool_input, dict):
                file_path = tool_input.get("file_path")
                if isinstance(file_path, str):
                    successful_read_files.append(file_path)

    successful_code_files = sorted(
        {
            file_path
            for file_path in successful_read_files
            if file_path.endswith(".py") and METHOD1_CORPUS_RELATIVE in file_path.replace("\\", "/")
        }
    )

    return {
        "system_tools": system_event.get("tools", []),
        "system_mcp_servers": system_event.get("mcp_servers", []),
        "allowed_tools_policy": ALLOWED_TOOLS,
        "tool_use_count": len(tool_uses),
        "tool_result_count": tool_results,
        "tool_uses": tool_uses,
        "successful_read_files": sorted(set(successful_read_files)),
        "successful_code_files": successful_code_files,
        "successful_code_file_count": len(successful_code_files),
        "blocked_access_patterns": BLOCKED_ACCESS_DESCRIPTIONS,
        "disallowed_tool_uses": disallowed_tool_uses,
        "policy_violations": violations,
    }


def write_tool_usage_summary(sample_dir: Path, summary: dict[str, Any]) -> None:
    (sample_dir / "tool_usage_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def prepare_sample_workspace(sample_dir: Path) -> None:
    """Expose the method1 corpus at the relative path shown in the prompt."""
    corpus_link = sample_dir / METHOD1_CORPUS_RELATIVE
    corpus_link.parent.mkdir(parents=True, exist_ok=True)
    if corpus_link.exists() or corpus_link.is_symlink():
        if corpus_link.is_symlink():
            corpus_link.unlink()
        else:
            raise RuntimeError(f"Cannot create corpus link because path already exists: {corpus_link}")
    corpus_link.symlink_to(METHOD1_CORPUS_DIR, target_is_directory=True)


def check_claude_bin(claude_bin: str) -> str:
    try:
        proc = subprocess.run(
            [claude_bin, "--version"],
            text=True,
            capture_output=True,
            check=False,
            timeout=15,
        )
    except Exception as exc:
        raise RuntimeError(f"Failed to run Claude CLI version check for {claude_bin}: {exc}") from exc

    output = (proc.stdout or proc.stderr or "").strip()
    if proc.returncode != 0:
        raise RuntimeError(f"Claude CLI version check failed for {claude_bin}:\n{output}")
    return output


def run_claude_cli(
    *,
    claude_bin: str,
    model: str,
    prompt: str,
    sample_dir: Path,
    timeout: float | None,
    extra_args: list[str],
) -> dict[str, Any]:
    base_cmd = [
        claude_bin,
        "-p",
        "--add-dir",
        str(METHOD1_CORPUS_DIR),
        *DEFAULT_CLAUDE_ARGS,
        *list(extra_args),
    ]

    def _exec(command: list[str]) -> dict[str, Any]:
        try:
            proc = subprocess.run(
                command,
                input=prompt,
                text=True,
                capture_output=True,
                cwd=sample_dir,
                check=False,
                timeout=timeout,
            )
            raw_stdout = coerce_output_text(proc.stdout)
            parsed_stdout = extract_stream_json_text(raw_stdout)
            return {
                "return_code": int(proc.returncode),
                "stdout": parsed_stdout,
                "raw_stdout": raw_stdout if raw_stdout != parsed_stdout else "",
                "stderr": coerce_output_text(proc.stderr),
                "command": command,
            }
        except subprocess.TimeoutExpired as exc:
            raw_stdout = coerce_output_text(exc.stdout)
            parsed_stdout = extract_stream_json_text(raw_stdout)
            return {
                "return_code": 124,
                "stdout": parsed_stdout,
                "raw_stdout": raw_stdout if raw_stdout != parsed_stdout else "",
                "stderr": coerce_output_text(exc.stderr) or f"Claude CLI timed out after {timeout} seconds",
                "command": command,
            }
        except FileNotFoundError:
            return {
                "return_code": 127,
                "stdout": "",
                "raw_stdout": "",
                "stderr": f"Claude CLI not found: {claude_bin}",
                "command": command,
            }
        except Exception as exc:
            return {
                "return_code": 1,
                "stdout": "",
                "raw_stdout": "",
                "stderr": f"{type(exc).__name__}: {exc}",
                "command": command,
            }

    if model:
        command = base_cmd + ["--model", model]
        result = _exec(command)
        err_text = str(result.get("stderr") or "").lower()
        unknown_model_flag = (
            "unknown option" in err_text
            or "unrecognized option" in err_text
            or "unexpected argument '--model'" in err_text
        )
        if unknown_model_flag:
            result = _exec(base_cmd)
            result["model_flag_fallback"] = True
        else:
            result["model_flag_fallback"] = False
        result["tried_with_model"] = True
        return result

    result = _exec(base_cmd)
    result["model_flag_fallback"] = False
    result["tried_with_model"] = False
    return result


def pick_primary_text(cli_result: dict[str, Any]) -> str:
    stdout = str(cli_result.get("stdout") or "")
    stderr = str(cli_result.get("stderr") or "")
    for candidate in (stdout, stderr):
        low = candidate.lower()
        if "<answer>" in low and "</answer>" in low:
            return candidate
    return stdout or stderr


def write_result_markdown(
    *,
    sample_dir: Path,
    question_id: str,
    prompt: str,
    primary_text: str,
    cli_result: dict[str, Any],
    function_name: str,
) -> None:
    command = " ".join(shlex.quote(str(part)) for part in cli_result.get("command", []))
    sections = [
        f"# Claude Result - {question_id}",
        "",
        f"- question_id: `{question_id}`",
        f"- return_code: `{cli_result.get('return_code')}`",
        f"- function_name: `{function_name}`",
        "",
        "## Prompt",
        "",
        "````text",
        prompt.rstrip(),
        "````",
        "",
        "## CLI Command",
        "",
        "````bash",
        command,
        "````",
        "",
        "## Primary Text Used For Parsing",
        "",
        "````text",
        primary_text.strip(),
        "````",
        "",
        "## CLI STDERR",
        "",
        "````text",
        str(cli_result.get("stderr") or "").strip(),
        "````",
        "",
    ]
    raw_stdout = str(cli_result.get("raw_stdout") or "").strip()
    if raw_stdout:
        sections.extend(["## CLI RAW STDOUT", "", "````text", raw_stdout, "````", ""])
    (sample_dir / "result.md").write_text("\n".join(sections), encoding="utf-8")


def write_rendered_trajectory(
    *,
    sample_dir: Path,
    question_id: str,
    prompt: str,
    primary_text: str,
    cli_result: dict[str, Any],
    function_name: str,
    tool_usage_summary: dict[str, Any],
) -> None:
    raw_stdout = str(cli_result.get("raw_stdout") or "")
    events = parse_stream_json_events(raw_stdout)
    result_event = next((event for event in events if event.get("type") == "result"), {})
    command = " ".join(shlex.quote(str(part)) for part in cli_result.get("command", []))

    lines: list[str] = [
        f"# Rendered Claude CLI Trajectory - {question_id}",
        "",
        "## Run Summary",
        "",
        f"- condition: `{CLAUDE_CONDITION}`",
        f"- question_id: `{question_id}`",
        f"- return_code: `{cli_result.get('return_code')}`",
        f"- function_name: `{function_name}`",
        f"- num_turns: `{result_event.get('num_turns')}`",
        f"- event_count: `{len(events)}`",
        f"- duration_ms: `{result_event.get('duration_ms')}`",
        f"- corpus: `{METHOD1_CORPUS_DIR}`",
        f"- allowed_tools: `{','.join(ALLOWED_TOOLS)}`",
        f"- tool_use_count: `{tool_usage_summary.get('tool_use_count')}`",
        f"- policy_violation_count: `{len(tool_usage_summary.get('policy_violations', []))}`",
        "",
        "## CLI Command",
        "",
        "````bash",
        command,
        "````",
        "",
        "## Tool Usage Summary",
        "",
        "````json",
        json.dumps(tool_usage_summary, ensure_ascii=False, indent=2),
        "````",
        "",
        "## Event Timeline",
        "",
    ]

    for event_index, event in enumerate(events):
        event_type = event.get("type")
        subtype = event.get("subtype")
        lines.extend(
            [
                f"### Event {event_index}: {event_type}" + (f" / {subtype}" if subtype else ""),
                "",
            ]
        )

        if event_type == "system":
            fields = {
                "cwd": event.get("cwd"),
                "session_id": event.get("session_id"),
                "model": event.get("model"),
                "tools": event.get("tools", []),
                "mcp_servers": event.get("mcp_servers", []),
                "permissionMode": event.get("permissionMode"),
                "claude_code_version": event.get("claude_code_version"),
                "fast_mode_state": event.get("fast_mode_state"),
            }
            lines.extend(["````json", json.dumps(fields, ensure_ascii=False, indent=2), "````", ""])
            continue

        message = event.get("message")
        if isinstance(message, dict):
            fields = {
                "id": message.get("id"),
                "role": message.get("role"),
                "model": message.get("model"),
                "stop_reason": message.get("stop_reason"),
                "usage": message.get("usage"),
            }
            lines.extend(["````json", json.dumps(fields, ensure_ascii=False, indent=2), "````"])
            content = message.get("content")
            if isinstance(content, list):
                for block_index, block in enumerate(content):
                    if not isinstance(block, dict):
                        continue
                    block_type = block.get("type")
                    if block_type == "text":
                        text = str(block.get("text") or "")
                        lines.extend(
                            [
                                "",
                                f"- content_part_{block_index}: `text`, chars=`{len(text)}`",
                                "",
                                "````text",
                                text.rstrip(),
                                "````",
                            ]
                        )
                    elif block_type == "tool_use":
                        lines.extend(
                            [
                                "",
                                f"- content_part_{block_index}: `tool_use`, name=`{block.get('name')}`",
                                "",
                                "````json",
                                json.dumps(block, ensure_ascii=False, indent=2),
                                "````",
                            ]
                        )
                    elif block_type == "tool_result":
                        content_text = block.get("content")
                        lines.extend(
                            [
                                "",
                                f"- content_part_{block_index}: `tool_result`, chars=`{len(coerce_output_text(content_text))}`",
                                f"- preview: `{compact_text(content_text)}`",
                            ]
                        )
                    else:
                        lines.append(f"- content_part_{block_index}: `{block_type}`")
            lines.append("")
            continue

        if event_type == "result":
            result_text = str(event.get("result") or "")
            fields = {key: value for key, value in event.items() if key != "result"}
            fields["result_chars"] = len(result_text)
            fields["result_equals_primary_text"] = result_text == primary_text
            lines.extend(["````json", json.dumps(fields, ensure_ascii=False, indent=2), "````", ""])
            continue

        lines.extend(["````json", json.dumps(event, ensure_ascii=False, indent=2), "````", ""])

    lines.extend(
        [
            "## Prompt",
            "",
            "````text",
            prompt.rstrip(),
            "````",
            "",
            "## Primary Text Used For Parsing",
            "",
            "````text",
            primary_text.strip(),
            "````",
            "",
        ]
    )
    (sample_dir / "trajectory.rendered.md").write_text("\n".join(lines), encoding="utf-8")


def run_one(args: tuple[Any, ...]) -> tuple[int, dict[str, str], dict[str, Any]]:
    idx, question_path, bench_run_dir, claude_bin, model, timeout, extra_args = args
    question_path = Path(question_path)
    question_id = question_path.parent.name
    sample_dir = Path(bench_run_dir) / f"{idx:04d}_{question_id}"
    sample_dir.mkdir(parents=True, exist_ok=True)
    prepare_sample_workspace(sample_dir)

    question = question_path.read_text(encoding="utf-8").strip()
    prompt = build_prompt(question)
    cli_result = run_claude_cli(
        claude_bin=claude_bin,
        model=model,
        prompt=prompt,
        sample_dir=sample_dir,
        timeout=timeout,
        extra_args=extra_args,
    )
    primary_text = pick_primary_text(cli_result)
    function_code, function_name = extract_response(primary_text)
    stream_events = parse_stream_json_events(str(cli_result.get("raw_stdout") or ""))
    tool_usage_summary = build_tool_usage_summary(stream_events)
    write_tool_usage_summary(sample_dir, tool_usage_summary)

    output_entry = {
        "question_file_path": question_id,
        "function": function_code,
        "function_name": function_name,
    }
    raw_entry: dict[str, Any] = {
        "index": idx,
        "question_file_path": question_id,
        "question_path": str(question_path),
        "prompt": prompt,
        "primary_text": primary_text,
        "parsed_function_name": function_name,
        "parsed_function": function_code,
        "return_code": cli_result.get("return_code"),
        "stdout": cli_result.get("stdout") or "",
        "raw_stdout": cli_result.get("raw_stdout") or "",
        "stderr": cli_result.get("stderr") or "",
        "command": cli_result.get("command", []),
        "tried_with_model": cli_result.get("tried_with_model", False),
        "model_flag_fallback": cli_result.get("model_flag_fallback", False),
        "sample_dir": str(sample_dir),
        "tool_usage_summary": tool_usage_summary,
    }
    result_json = {
        "summary": {
            "question_file_path": question_id,
            "llm_model": model,
            "return_code": cli_result.get("return_code"),
            "claude_condition": CLAUDE_CONDITION,
        },
        "action_history": [{"finish": primary_text}],
        "context": raw_entry,
        "parsed": output_entry,
    }
    (sample_dir / "result.json").write_text(json.dumps(result_json, ensure_ascii=False, indent=2), encoding="utf-8")
    write_result_markdown(
        sample_dir=sample_dir,
        question_id=question_id,
        prompt=prompt,
        primary_text=primary_text,
        cli_result=cli_result,
        function_name=function_name,
    )
    write_rendered_trajectory(
        sample_dir=sample_dir,
        question_id=question_id,
        prompt=prompt,
        primary_text=primary_text,
        cli_result=cli_result,
        function_name=function_name,
        tool_usage_summary=tool_usage_summary,
    )
    return idx, output_entry, raw_entry


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def get_sample_dir(bench_run_dir: Path, idx: int, question_path: Path) -> Path:
    return bench_run_dir / f"{idx:04d}_{question_path.parent.name}"


def load_completed_result(sample_dir: Path, expected_idx: int, expected_question_id: str) -> tuple[dict[str, str], dict[str, Any]] | None:
    result_path = sample_dir / "result.json"
    if not result_path.is_file():
        return None

    try:
        result_json = json.loads(result_path.read_text(encoding="utf-8"))
    except Exception:
        return None

    output_entry = result_json.get("parsed")
    raw_entry = result_json.get("context")
    if not isinstance(output_entry, dict) or not isinstance(raw_entry, dict):
        return None
    if output_entry.get("question_file_path") != expected_question_id:
        return None

    normalized_output = {
        "question_file_path": expected_question_id,
        "function": output_entry.get("function") or "",
        "function_name": output_entry.get("function_name") or "",
    }
    normalized_raw = dict(raw_entry)
    normalized_raw.setdefault("index", expected_idx)
    normalized_raw.setdefault("question_file_path", expected_question_id)
    normalized_raw.setdefault("sample_dir", str(sample_dir))
    return normalized_output, normalized_raw


def rebuild_jsonl_from_sample_results(bench_run_dir: Path, questions: list[Path]) -> tuple[int, list[dict[str, str]], list[dict[str, Any]]]:
    output_entries: list[dict[str, str]] = []
    raw_entries: list[dict[str, Any]] = []
    missing: list[str] = []

    for idx, question_path in enumerate(questions):
        question_id = question_path.parent.name
        sample_dir = get_sample_dir(bench_run_dir, idx, question_path)
        loaded = load_completed_result(sample_dir, idx, question_id)
        if loaded is None:
            missing.append(f"{idx:04d}_{question_id}")
            output_entries.append(
                {
                    "question_file_path": question_id,
                    "function": "",
                    "function_name": "",
                }
            )
            raw_entries.append(
                {
                    "index": idx,
                    "question_file_path": question_id,
                    "question_path": str(question_path),
                    "sample_dir": str(sample_dir),
                    "error": {"type": "missing_result_json"},
                }
            )
            continue

        output_entry, raw_entry = loaded
        output_entries.append(output_entry)
        raw_entries.append(raw_entry)

    write_jsonl(bench_run_dir / "function_generation_results.jsonl", output_entries)
    write_jsonl(bench_run_dir / "raw_responses.jsonl", raw_entries)
    if missing:
        write_jsonl(
            bench_run_dir / "rebuild_missing.jsonl",
            [{"sample": sample} for sample in missing],
        )
    return len(missing), output_entries, raw_entries


def run_parser_self_test() -> None:
    normal = """<answer><code>
```python
def foo():
    return {"a": 1}
```
</code><name>foo</name></answer>"""
    assert extract_response(normal) == ('def foo():\n    return {"a": 1}', "foo")

    no_fence = "<answer><code>def bar():\n    return {'b': 2}</code><name>bar</name></answer>"
    assert extract_response(no_fence) == ("def bar():\n    return {'b': 2}", "bar")

    assert extract_response("missing tags") == ("", "")

    stream = "\n".join(
        [
            json.dumps({"type": "system", "tools": []}),
            json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": normal}]}}),
            json.dumps({"type": "result", "result": normal}),
        ]
    )
    assert extract_response(extract_stream_json_text(stream)) == ('def foo():\n    return {"a": 1}', "foo")
    assert extract_stream_json_text(stream).count("<answer>") == 1

    tool_stream = "\n".join(
        [
            json.dumps({"type": "system", "tools": ALLOWED_TOOLS, "mcp_servers": []}),
            json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "content": [
                            {
                                "type": "tool_use",
                                "id": "toolu_1",
                                "name": "Read",
                                "input": {"file_path": "code_segments/pymatgen_analysis_defects/test_core.json"},
                            }
                        ]
                    },
                }
            ),
        ]
    )
    tool_summary = build_tool_usage_summary(parse_stream_json_events(tool_stream))
    assert tool_summary["tool_use_count"] == 1
    assert tool_summary["policy_violations"]
    print("parser self-test passed")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run MatTools real-world tasks with Claude Code method1 read-only access.")
    parser.add_argument(
        "--claude-bin",
        default=os.environ.get("CLAUDE_BIN")
        or (str(DEFAULT_CLAUDE_BIN) if DEFAULT_CLAUDE_BIN.exists() else "claude"),
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("CLAUDE_MODEL") or os.environ.get("ANTHROPIC_MODEL") or "sonnet",
        help="Claude model name or alias. Pass an empty string to omit --model.",
    )
    parser.add_argument("--run-name", default="", help="Output run name under claude_cli_test/.")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of tasks for smoke runs. 0 means all.")
    parser.add_argument("--timeout", type=float, default=None, help="Per-task Claude CLI timeout in seconds.")
    parser.add_argument("--max-process", type=int, default=1, help="Maximum concurrent Claude CLI processes.")
    parser.add_argument(
        "--resume-existing",
        action="store_true",
        help="Reuse existing per-task result.json files in --run-name and only run missing tasks.",
    )
    parser.add_argument(
        "--rebuild-only",
        action="store_true",
        help="Do not call Claude. Rebuild top-level JSONL files from per-task result.json files in --run-name.",
    )
    parser.add_argument("--parser-self-test", action="store_true", help="Run parser and trajectory helper self-tests.")
    parser.add_argument(
        "--claude-extra-args",
        nargs=argparse.REMAINDER,
        default=[],
        help="Additional arguments passed to Claude CLI. Must be the last option.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    if args.parser_self_test:
        run_parser_self_test()
        return

    if not METHOD1_CORPUS_DIR.is_dir():
        raise RuntimeError(f"Method1 corpus directory not found: {METHOD1_CORPUS_DIR}")

    questions = load_questions_path_from_directories(BASE_QUESTIONS_DIR)
    if args.limit and args.limit > 0:
        questions = questions[: args.limit]
    if not questions:
        raise RuntimeError(f"No question.txt files found under {BASE_QUESTIONS_DIR}")

    run_name = args.run_name.strip() or f"claude_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if args.rebuild_only and not args.run_name.strip():
        raise RuntimeError("--rebuild-only requires --run-name so an existing run directory can be rebuilt")
    bench_run_dir = DEFAULT_OUTPUT_ROOT / run_name
    bench_run_dir.mkdir(parents=True, exist_ok=True)

    if args.rebuild_only:
        missing_count, _, _ = rebuild_jsonl_from_sample_results(bench_run_dir, questions)
        print(
            f"[Claude MatTools] Rebuilt JSONL from {len(questions) - missing_count}/{len(questions)} completed sample results.",
            flush=True,
        )
        if missing_count:
            print(f"[Claude MatTools] Missing sample count: {missing_count}; see rebuild_missing.jsonl", flush=True)
        print(f"Wrote {bench_run_dir / 'function_generation_results.jsonl'}", flush=True)
        print("RESULTS_DIR=" + str(bench_run_dir.resolve()), flush=True)
        return

    claude_version = check_claude_bin(args.claude_bin)
    print(f"[Claude MatTools] Using Claude CLI: {args.claude_bin} ({claude_version})", flush=True)

    extra_args = list(args.claude_extra_args or [])
    run_meta = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "runner": "claude_cli_test/build_agent.py",
        "claude_condition": CLAUDE_CONDITION,
        "base_questions_dir": str(BASE_QUESTIONS_DIR),
        "results_dir": str(bench_run_dir),
        "claude_bin": args.claude_bin,
        "claude_version": claude_version,
        "model": args.model,
        "corpus": METHOD1_CORPUS_RELATIVE,
        "method1_corpus_dir": str(METHOD1_CORPUS_DIR),
        "allowed_tools": ALLOWED_TOOLS,
        "standard_claude_args": DEFAULT_CLAUDE_ARGS,
        "limit": args.limit,
        "timeout": args.timeout,
        "max_process": max(1, args.max_process),
        "claude_extra_args": extra_args,
        "num_questions": len(questions),
    }
    (bench_run_dir / "claude_run_meta.json").write_text(
        json.dumps(run_meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    output_entries: list[dict[str, str] | None] = [None] * len(questions)
    raw_entries: list[dict[str, Any] | None] = [None] * len(questions)
    errors: list[dict[str, Any]] = []
    task_args = []
    reused_count = 0
    for idx, question_path in enumerate(questions):
        question_id = question_path.parent.name
        if args.resume_existing:
            loaded = load_completed_result(get_sample_dir(bench_run_dir, idx, question_path), idx, question_id)
            if loaded is not None:
                output_entry, raw_entry = loaded
                output_entries[idx] = output_entry
                raw_entries[idx] = raw_entry
                reused_count += 1
                continue
        task_args.append((idx, str(question_path), str(bench_run_dir), args.claude_bin, args.model, args.timeout, extra_args))

    max_process = max(1, int(args.max_process))
    if args.resume_existing:
        print(f"[Claude MatTools] Reusing {reused_count}/{len(questions)} completed tasks from result.json.", flush=True)
    print(f"[Claude MatTools] Queued {len(task_args)} tasks; running with max_process={max_process}.", flush=True)
    if max_process == 1:
        iterator = tqdm(task_args, desc="mattools claude", leave=True)
        for one_arg in iterator:
            idx = one_arg[0]
            try:
                _, output_entry, raw_entry = run_one(one_arg)
                output_entries[idx] = output_entry
                raw_entries[idx] = raw_entry
            except Exception as exc:
                errors.append({"index": idx, "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()})
    else:
        with ThreadPoolExecutor(max_workers=max_process) as executor:
            future_to_idx = {executor.submit(run_one, one_arg): one_arg[0] for one_arg in task_args}
            for future in tqdm(as_completed(future_to_idx), total=len(future_to_idx), desc="mattools claude", leave=True):
                idx = future_to_idx[future]
                try:
                    _, output_entry, raw_entry = future.result()
                    output_entries[idx] = output_entry
                    raw_entries[idx] = raw_entry
                except Exception as exc:
                    errors.append({"index": idx, "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()})

    for idx, question_path in enumerate(questions):
        if output_entries[idx] is None:
            output_entries[idx] = {
                "question_file_path": question_path.parent.name,
                "function": "",
                "function_name": "",
            }
        if raw_entries[idx] is None:
            raw_entries[idx] = {
                "index": idx,
                "question_file_path": question_path.parent.name,
                "question_path": str(question_path),
                "error": next((e for e in errors if e["index"] == idx), {}),
            }

    write_jsonl(bench_run_dir / "function_generation_results.jsonl", [row for row in output_entries if row is not None])
    write_jsonl(bench_run_dir / "raw_responses.jsonl", [row for row in raw_entries if row is not None])
    if errors:
        write_jsonl(bench_run_dir / "errors.jsonl", errors)

    print(f"Wrote {bench_run_dir / 'function_generation_results.jsonl'}", flush=True)
    print("RESULTS_DIR=" + str(bench_run_dir.resolve()), flush=True)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
