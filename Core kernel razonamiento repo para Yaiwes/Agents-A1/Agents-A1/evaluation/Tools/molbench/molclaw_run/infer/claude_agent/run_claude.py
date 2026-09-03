"""
Run llm_bench datasets with Claude CLI and write eval-compatible prediction files.

Usage:
  python run_claude.py --cfg config/launch_rdkit_bench.yaml --claude-mode both
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import http.client
import ipaddress
import json
import os
import shlex
import shutil
import subprocess
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import yaml


_REQUEST_SKIP_HEADERS = {"host", "content-length", "connection", "accept-encoding", "proxy-connection"}
_RESPONSE_SKIP_HEADERS = {"transfer-encoding", "connection", "content-encoding", "content-length", "proxy-connection"}


def tqdm(iterable, **kwargs):  # type: ignore
    try:
        import importlib

        mod = importlib.import_module("tqdm")
        return mod.tqdm(iterable, **kwargs)
    except Exception:
        return iterable


_script_dir = os.path.dirname(os.path.abspath(__file__))
_pkg_root = os.path.dirname(os.path.dirname(_script_dir))
_llm_bench_root = os.path.dirname(_pkg_root)
_workspace_root = os.path.dirname(_llm_bench_root)

for _d in (_pkg_root, _llm_bench_root, _workspace_root):
    if _d not in sys.path:
        sys.path.insert(0, _d)

try:
    from MolClaw.molclaw_run.data_loader.bench_loaders import collect_result_text, get_loader
    from MolClaw.molclaw_run.templates.template import ANSWER_OUTPUT_HINT
    from MolClaw.utils.fix_seed import set_global_seed
except ModuleNotFoundError:
    from molclaw_run.data_loader.bench_loaders import collect_result_text, get_loader
    from molclaw_run.templates.template import ANSWER_OUTPUT_HINT
    from utils.fix_seed import set_global_seed

CLAUDE_MODES = {"non", "both"}
SKILLS_MATERIALIZATION_MODES = {"copy", "hardlink_snapshot"}
_SKILLS_HARDLINK_FALLBACK_COUNT = 0
_SKILLS_HARDLINK_FALLBACK_LOCK = threading.Lock()


def _load_dotenv(path: str | None) -> None:
    if not path:
        return
    env_path = Path(path).expanduser()
    if not env_path.is_absolute():
        env_path = Path(_llm_bench_root) / env_path
    if not env_path.is_file():
        return
    with env_path.open("r", encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if not raw or raw.startswith("#") or "=" not in raw:
                continue
            key, value = raw.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def _openrouter_anthropic_base_url(value: str | None) -> str:
    base_url = (value or "").strip() or "https://openrouter.ai/api"
    if base_url.rstrip("/") == "https://openrouter.ai/api/v1":
        return "https://openrouter.ai/api"
    return base_url.rstrip("/")


def _resolve_model_name(model_cfg: dict[str, Any]) -> str:
    configured = str(model_cfg.get("llm_model") or "").strip()
    if configured:
        return configured
    return (
        os.environ.get("CLAUDE_MODEL", "").strip()
        or os.environ.get("ANTHROPIC_MODEL", "").strip()
        or os.environ.get("MODEL_NAME", "").strip()
        or os.environ.get("LLM_MODEL", "").strip()
    )


def _resolve_claude_subprocess_env(model_cfg: dict[str, Any]) -> tuple[dict[str, str], dict[str, Any]]:
    """Build Claude-only environment without mutating the parent process."""
    env = dict(os.environ)
    provider = str(model_cfg.get("claude_provider") or model_cfg.get("provider") or "").strip().lower()
    info: dict[str, Any] = {"provider": provider or "default"}

    if provider == "openrouter":
        base_url = _openrouter_anthropic_base_url(
            model_cfg.get("anthropic_base_url")
            or env.get("ANTHROPIC_BASE_URL")
            or env.get("OPENROUTER_BASE_URL")
            or env.get("OPENAI_BASE_URL")
        )
        token_env = str(
            model_cfg.get("anthropic_auth_token_env")
            or model_cfg.get("openrouter_api_key_env")
            or "OPENROUTER_API_KEY"
        ).strip()
        token = env.get(token_env, "").strip()
        if not token and token_env != "OPENAI_API_KEY":
            token = env.get("OPENAI_API_KEY", "").strip()
            token_env = "OPENAI_API_KEY" if token else token_env
        if not token:
            token = env.get("ANTHROPIC_AUTH_TOKEN", "").strip()
            token_env = "ANTHROPIC_AUTH_TOKEN" if token else token_env
        if not token:
            raise RuntimeError(
                "Missing OpenRouter token for Claude CLI. Set OPENROUTER_API_KEY, "
                "OPENAI_API_KEY, ANTHROPIC_AUTH_TOKEN, or model.anthropic_auth_token_env."
            )
        env["ANTHROPIC_BASE_URL"] = base_url
        env["ANTHROPIC_AUTH_TOKEN"] = token
        env["ANTHROPIC_API_KEY"] = ""
        env.setdefault("OPENROUTER_API_KEY", token)
        info.update(
            {
                "anthropic_base_url": base_url,
                "anthropic_auth_token_env": token_env,
                "anthropic_auth_token_set": True,
                "anthropic_api_key_blank": True,
            }
        )
        return env, info

    base_url = str(model_cfg.get("anthropic_base_url") or "").strip()
    token_env = str(model_cfg.get("anthropic_auth_token_env") or "").strip()
    if base_url:
        env["ANTHROPIC_BASE_URL"] = base_url
        info["anthropic_base_url"] = base_url
    if token_env:
        token = env.get(token_env, "").strip()
        if not token:
            raise RuntimeError(f"Missing token in configured env var: {token_env}")
        env["ANTHROPIC_AUTH_TOKEN"] = token
        info.update({"anthropic_auth_token_env": token_env, "anthropic_auth_token_set": True})
    if "anthropic_api_key" in model_cfg:
        env["ANTHROPIC_API_KEY"] = str(model_cfg.get("anthropic_api_key") or "")
        info["anthropic_api_key_overridden"] = True
    return env, info


def _is_truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _apply_claude_config_dir(
    env: dict[str, str],
    model_cfg: dict[str, Any],
    bench_run_dir: str,
) -> dict[str, Any]:
    """Optionally isolate Claude Code config for experiment-only runs."""
    configured = str(model_cfg.get("claude_config_dir") or "").strip()
    isolate = _is_truthy(model_cfg.get("isolate_claude_config"))
    if not configured and not isolate:
        return {}

    if configured:
        config_dir = Path(configured).expanduser()
        if not config_dir.is_absolute():
            config_dir = Path(_llm_bench_root) / config_dir
    else:
        config_dir = Path(bench_run_dir) / "claude_config"

    config_dir.mkdir(parents=True, exist_ok=True)
    env["CLAUDE_CONFIG_DIR"] = str(config_dir)
    return {
        "claude_config_dir": str(config_dir),
        "claude_config_isolated": isolate and not configured,
    }


def _use_per_sample_claude_config(model_cfg: dict[str, Any]) -> bool:
    if "per_sample_claude_config" in model_cfg:
        return _is_truthy(model_cfg.get("per_sample_claude_config"))
    return _is_truthy(model_cfg.get("isolate_claude_config")) and not str(
        model_cfg.get("claude_config_dir") or ""
    ).strip()


def _selected_subtasks(bench_cfg: dict[str, Any], task_name: str, loader: Any) -> list[str]:
    configured = bench_cfg.get("subtasks")
    if isinstance(configured, dict):
        value = configured.get(task_name)
        if value is None:
            return loader.get_subtasks()
        if isinstance(value, str):
            return [value]
        if isinstance(value, list) and all(isinstance(x, str) for x in value):
            return value
        raise ValueError(f"bench.subtasks[{task_name!r}] must be a string or list of strings")
    return loader.get_subtasks()


def _resolve_cfg_mode(cfg: dict, cli_mode: str | None) -> str:
    if cli_mode:
        mode = cli_mode.strip().lower()
    else:
        mode = (
            cfg.get("settings", {}).get("claude_mode")
            or cfg.get("settings", {}).get("nanobot_mode")
            or "both"
        )
        mode = str(mode).strip().lower()
    if mode not in CLAUDE_MODES:
        raise ValueError(f"Invalid claude mode: {mode}. Expected one of {sorted(CLAUDE_MODES)}")
    return mode


def _resolve_skills_materialization(cfg: dict[str, Any]) -> str:
    raw = (
        (cfg.get("settings", {}) or {}).get("skills_materialization")
        or (cfg.get("model", {}) or {}).get("skills_materialization")
        or "hardlink_snapshot"
    )
    mode = str(raw).strip().lower().replace("-", "_")
    aliases = {"hardlink": "hardlink_snapshot", "snapshot_hardlink": "hardlink_snapshot"}
    mode = aliases.get(mode, mode)
    if mode not in SKILLS_MATERIALIZATION_MODES:
        raise ValueError(
            f"Invalid skills_materialization: {raw}. "
            f"Expected one of {sorted(SKILLS_MATERIALIZATION_MODES)}"
        )
    return mode


def _record_hardlink_fallback(count: int) -> None:
    global _SKILLS_HARDLINK_FALLBACK_COUNT
    if count <= 0:
        return
    with _SKILLS_HARDLINK_FALLBACK_LOCK:
        _SKILLS_HARDLINK_FALLBACK_COUNT += count


def _get_hardlink_fallback_count() -> int:
    with _SKILLS_HARDLINK_FALLBACK_LOCK:
        return _SKILLS_HARDLINK_FALLBACK_COUNT


def _safe_name(text: str) -> str:
    s = (text or "dataset").strip().lower()
    s = "".join(ch if (ch.isalnum() or ch in ("_", "-")) else "_" for ch in s)
    while "__" in s:
        s = s.replace("__", "_")
    s = s.strip("_")
    return s or "dataset"


def _remove_path(path: str) -> None:
    if not os.path.lexists(path):
        return
    if os.path.islink(path) or os.path.isfile(path):
        os.unlink(path)
    else:
        shutil.rmtree(path)


def _copy_tree(src: str, dst: str) -> None:
    if not os.path.isdir(src):
        return
    os.makedirs(dst, exist_ok=True)
    for name in os.listdir(src):
        src_path = os.path.join(src, name)
        dst_path = os.path.join(dst, name)
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        else:
            shutil.copy2(src_path, dst_path)


def _assert_no_symlinks(src: str) -> None:
    for dirpath, dirnames, filenames in os.walk(src, followlinks=False):
        for name in dirnames + filenames:
            path = os.path.join(dirpath, name)
            if os.path.islink(path):
                raise ValueError(f"skills tree must not contain symlinks: {path}")


def _hardlink_tree(src: str, dst: str) -> int:
    if not os.path.isdir(src):
        return 0
    os.makedirs(dst, exist_ok=True)
    fallback_count = 0
    with os.scandir(src) as entries:
        for entry in entries:
            src_path = entry.path
            dst_path = os.path.join(dst, entry.name)
            if entry.is_symlink():
                raise ValueError(f"skills tree must not contain symlinks: {src_path}")
            if entry.is_dir(follow_symlinks=False):
                fallback_count += _hardlink_tree(src_path, dst_path)
            elif entry.is_file(follow_symlinks=False):
                try:
                    os.link(src_path, dst_path)
                except OSError:
                    shutil.copy2(src_path, dst_path)
                    fallback_count += 1
    return fallback_count


def _tree_manifest(src: str) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    root = Path(src)
    tree_hash = hashlib.sha256()
    total_size = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(root).as_posix()
        data_hash = hashlib.sha256()
        size = 0
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                size += len(chunk)
                data_hash.update(chunk)
        digest = data_hash.hexdigest()
        total_size += size
        files.append({"path": rel, "size": size, "sha256": digest})
        tree_hash.update(rel.encode("utf-8") + b"\0")
        tree_hash.update(str(size).encode("ascii") + b"\0")
        tree_hash.update(digest.encode("ascii") + b"\0")
    return {
        "file_count": len(files),
        "total_size": total_size,
        "tree_sha256": tree_hash.hexdigest(),
        "files": files,
    }


def _chmod_tree_readonly(src: str) -> None:
    for dirpath, dirnames, filenames in os.walk(src):
        for name in filenames:
            path = os.path.join(dirpath, name)
            try:
                os.chmod(path, os.stat(path).st_mode & ~0o222)
            except OSError:
                pass


def _repo_relative_paths(*paths: str) -> list[str]:
    repo_root = Path(_llm_bench_root).resolve()
    rel_paths: list[str] = []
    for raw in paths:
        if not raw:
            continue
        try:
            rel_paths.append(Path(raw).resolve().relative_to(repo_root).as_posix())
        except ValueError:
            continue
    return sorted(set(rel_paths))


def _git_run_metadata(*paths: str) -> dict[str, Any]:
    pathspec = _repo_relative_paths(*paths)
    try:
        commit = subprocess.check_output(
            ["git", "-C", _llm_bench_root, "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        commit = ""
    try:
        tracked_dirty = subprocess.run(
            ["git", "-C", _llm_bench_root, "diff-index", "--quiet", "HEAD", "--"] + pathspec,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode != 0
    except Exception:
        tracked_dirty = None
    try:
        untracked = subprocess.check_output(
            ["git", "-C", _llm_bench_root, "ls-files", "--others", "--exclude-standard", "--"] + pathspec,
            text=True,
            stderr=subprocess.DEVNULL,
        ).splitlines()
    except Exception:
        untracked = []
    dirty = None if tracked_dirty is None else bool(tracked_dirty or untracked)
    return {
        "git_commit": commit,
        "git_dirty": dirty,
        "git_tracked_dirty": tracked_dirty,
        "git_metadata_paths": pathspec,
        "git_untracked_relevant_count": len(untracked),
        "git_untracked_relevant_files": untracked[:50],
    }


def _build_prompt(query: str, answer_hint: str, mode: str, input_file: str | None) -> str:
    lines: list[str] = []
    lines.append((query or "").strip())
    lines.append("")
    lines.append((answer_hint or ANSWER_OUTPUT_HINT).strip())
    lines.append("")
    lines.append("Execution constraints:")
    lines.append("1. You are already in the per-sample workspace directory. Do not access, read, or search for any files outside of this current directory.")
    lines.append("2. Put final answer inside <answer>...</answer> for evaluator parsing.")
    lines.append("3. Save process notes, skills you used and key outputs to result.md in current directory.")
    # if input_file:
    #     lines.append(f"4. Input data file is available at ./{input_file}.")
    if mode == "both":
        lines.append("Skills are available under ./.claude/skills; use them when needed.")
    return "\n".join(lines).strip() + "\n"


def _read_text_if_exists(path: str) -> str:
    if not os.path.isfile(path):
        return ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def _contains_answer_tag(text: str) -> bool:
    if not text:
        return False
    low = text.lower()
    return "<answer>" in low and "</answer>" in low


def _pick_primary_text(stdout: str, result_md: str, stderr: str) -> str:
    for candidate in (stdout, result_md, stderr):
        if _contains_answer_tag(candidate):
            return candidate
    for candidate in (stdout, result_md, stderr):
        if candidate and candidate.strip():
            return candidate
    return ""


def _extract_stream_json_text(stdout: str) -> str:
    if not stdout or not stdout.lstrip().startswith("{"):
        return stdout or ""

    text_chunks: list[str] = []
    assistant_texts: list[str] = []
    saw_json = False
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            return stdout
        saw_json = True

        event = obj.get("event") if isinstance(obj, dict) else None
        if isinstance(event, dict):
            delta = event.get("delta")
            if isinstance(delta, dict) and delta.get("type") == "text_delta":
                text_chunks.append(str(delta.get("text") or ""))

        message = obj.get("message") if isinstance(obj, dict) else None
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, list):
                assistant_texts.extend(
                    str(block.get("text") or "")
                    for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                )

        if obj.get("type") == "result" and obj.get("result"):
            assistant_texts.append(str(obj.get("result") or ""))

    if text_chunks:
        return "".join(text_chunks)
    if assistant_texts:
        return "\n".join(t for t in assistant_texts if t)
    return "" if saw_json else stdout


def _coerce_output_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _normalize_anthropic_request_body(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Make Claude CLI requests acceptable to stricter Anthropic-compatible servers."""
    messages = payload.get("messages")
    if not isinstance(messages, list):
        return payload, {}

    kept_messages: list[Any] = []
    lifted_system: list[Any] = []
    for message in messages:
        if isinstance(message, dict) and message.get("role") == "system":
            content = message.get("content")
            if isinstance(content, list):
                lifted_system.extend(content)
            elif content not in (None, ""):
                lifted_system.append({"type": "text", "text": str(content)})
            continue
        kept_messages.append(message)

    if not lifted_system:
        return payload, {}

    normalized = dict(payload)
    normalized["messages"] = kept_messages
    existing_system = normalized.get("system")
    if isinstance(existing_system, list):
        normalized["system"] = existing_system + lifted_system
    elif isinstance(existing_system, str) and existing_system:
        normalized["system"] = [{"type": "text", "text": existing_system}] + lifted_system
    elif existing_system:
        normalized["system"] = [{"type": "text", "text": json.dumps(existing_system, ensure_ascii=False)}] + lifted_system
    else:
        normalized["system"] = lifted_system
    return normalized, {"lifted_system_messages": len(lifted_system)}


def _normalize_capture_proxy_mode(value: Any) -> str:
    mode = str(value or "auto").strip().lower()
    if mode not in {"auto", "urllib", "forward"}:
        raise ValueError(f"Unsupported capture_proxy_mode: {value!r}; expected auto, urllib, or forward")
    return mode


def _env_first(env: dict[str, str] | None, keys: tuple[str, ...]) -> str:
    env = env or {}
    for key in keys:
        value = env.get(key)
        if value:
            return value.strip()
    return ""


def _append_no_proxy_entries(env: dict[str, str], entries: tuple[str, ...]) -> None:
    values: list[str] = []
    for key in ("no_proxy", "NO_PROXY"):
        values.extend(part.strip() for part in env.get(key, "").split(",") if part.strip())
    seen = {value.lower() for value in values}
    for entry in entries:
        if entry.lower() not in seen:
            values.append(entry)
            seen.add(entry.lower())
    joined = ",".join(values)
    env["no_proxy"] = joined
    env["NO_PROXY"] = joined


def _split_no_proxy_host_port(entry: str) -> tuple[str, int | None]:
    entry = entry.strip()
    if "://" in entry:
        parsed = urllib.parse.urlsplit(entry)
        try:
            return (parsed.hostname or "").strip(), parsed.port
        except ValueError:
            return (parsed.hostname or "").strip(), None
    if entry.startswith("["):
        end = entry.find("]")
        if end >= 0:
            host = entry[1:end]
            rest = entry[end + 1 :]
            if rest.startswith(":") and rest[1:].isdigit():
                return host, int(rest[1:])
            return host, None
    if entry.count(":") == 1:
        host, port_text = entry.rsplit(":", 1)
        if port_text.isdigit():
            return host, int(port_text)
    return entry, None


def _no_proxy_matches(target_url: str, env: dict[str, str] | None) -> bool:
    parsed = urllib.parse.urlsplit(target_url)
    host = (parsed.hostname or "").strip().lower().rstrip(".")
    if not host:
        return False
    try:
        port = parsed.port
    except ValueError:
        port = None
    if port is None:
        port = 443 if parsed.scheme.lower() == "https" else 80 if parsed.scheme.lower() == "http" else None

    try:
        if ipaddress.ip_address(host).is_loopback:
            return True
    except ValueError:
        if host == "localhost":
            return True

    no_proxy = ",".join(
        value.strip()
        for value in (_env_first(env, ("no_proxy",)), _env_first(env, ("NO_PROXY",)))
        if value.strip()
    )
    if not no_proxy:
        return False

    host_ip: Any | None = None
    try:
        host_ip = ipaddress.ip_address(host)
    except ValueError:
        host_ip = None

    for raw_entry in no_proxy.split(","):
        entry = raw_entry.strip()
        if not entry:
            continue
        if entry == "*":
            return True
        if "/" in entry and host_ip is not None:
            try:
                if host_ip in ipaddress.ip_network(entry, strict=False):
                    return True
            except ValueError:
                pass

        entry_host, entry_port = _split_no_proxy_host_port(entry)
        if entry_port is not None and port != entry_port:
            continue
        entry_host = entry_host.strip().lower().strip("[]").rstrip(".")
        if not entry_host:
            continue
        if entry_host.startswith("*."):
            entry_host = entry_host[1:]
        if entry_host.startswith("."):
            suffix = entry_host[1:]
            if host == suffix or host.endswith(entry_host):
                return True
        elif host == entry_host:
            return True
    return False


def _get_proxy_for_url(target_url: str, env: dict[str, str] | None) -> str | None:
    """Return the matching HTTP proxy URL for target_url, respecting no_proxy."""
    parsed = urllib.parse.urlsplit(target_url)
    scheme = parsed.scheme.lower()
    if scheme not in {"http", "https"} or _no_proxy_matches(target_url, env):
        return None

    if scheme == "https":
        proxy = _env_first(env, ("https_proxy", "HTTPS_PROXY", "http_proxy", "HTTP_PROXY"))
    else:
        proxy = _env_first(env, ("http_proxy", "HTTP_PROXY"))
    if not proxy:
        return None
    if "://" not in proxy:
        proxy = "http://" + proxy
    proxy_parsed = urllib.parse.urlsplit(proxy)
    if proxy_parsed.scheme.lower() != "http" or not proxy_parsed.hostname:
        return None
    try:
        proxy_parsed.port
    except ValueError:
        return None
    return proxy


def _host_header_for_url(target_url: str) -> str:
    parsed = urllib.parse.urlsplit(target_url)
    host = parsed.hostname or parsed.netloc
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    try:
        port = parsed.port
    except ValueError:
        port = None
    default_port = 443 if parsed.scheme.lower() == "https" else 80 if parsed.scheme.lower() == "http" else None
    if port is not None and port != default_port:
        return f"{host}:{port}"
    return host


class _ClaudeRequestCaptureProxy:
    """Local forwarding proxy that records Claude API request bodies.

    This is opt-in because it adds a local hop in front of the configured
    Anthropic/OpenRouter endpoint. It records request bodies only, not auth
    headers.
    """

    def __init__(
        self,
        upstream_base_url: str,
        log_path: str = "",
        record_bodies: bool = True,
        proxy_env: dict[str, str] | None = None,
        capture_proxy_mode: str = "auto",
    ) -> None:
        self.upstream_base_url = (upstream_base_url or "https://api.anthropic.com").rstrip("/")
        self.log_path = log_path
        self.record_bodies = record_bodies
        self.proxy_env = dict(proxy_env or {})
        self.capture_proxy_mode = _normalize_capture_proxy_mode(capture_proxy_mode)
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    def __enter__(self) -> "_ClaudeRequestCaptureProxy":
        if self.log_path:
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
            open(self.log_path, "w", encoding="utf-8").close()
        upstream_base_url = self.upstream_base_url
        log_path = self.log_path
        record_bodies = self.record_bodies
        proxy_env = dict(self.proxy_env)
        capture_proxy_mode = self.capture_proxy_mode
        request_lock = threading.Lock()
        request_counter = {"value": 0}

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, fmt: str, *args: Any) -> None:
                return

            def _record(self, body: bytes, normalize_info: dict[str, Any]) -> None:
                if not log_path:
                    return
                with request_lock:
                    request_index = request_counter["value"]
                    request_counter["value"] += 1
                record: dict[str, Any] = {
                    "request_index": request_index,
                    "method": self.command,
                    "path": self.path,
                }
                body_text = body.decode("utf-8", errors="replace")
                if record_bodies:
                    record["body"] = body_text
                try:
                    parsed = json.loads(body_text) if body_text else {}
                    if isinstance(parsed, dict):
                        record["model"] = parsed.get("model")
                        record["stream"] = parsed.get("stream")
                        record["system"] = parsed.get("system")
                        if normalize_info:
                            record["normalization"] = dict(normalize_info)
                        record["tool_count"] = len(parsed.get("tools") or []) if isinstance(parsed.get("tools"), list) else 0
                        record["message_count"] = len(parsed.get("messages") or []) if isinstance(parsed.get("messages"), list) else 0
                except Exception as exc:
                    record["parse_error"] = f"{type(exc).__name__}: {exc}"
                try:
                    with open(log_path, "a", encoding="utf-8") as f:
                        f.write(json.dumps(record, ensure_ascii=False) + "\n")
                except Exception:
                    pass

            def _send_proxy_error(self, exc: Exception, target: str) -> None:
                target_host = _host_header_for_url(target)
                data = json.dumps(
                    {
                        "error": f"{type(exc).__name__}: {exc}",
                        "proxy_mode": "forward",
                        "target_host": target_host,
                    },
                    ensure_ascii=False,
                ).encode("utf-8")
                self.send_response(502)
                self.send_header("content-type", "application/json")
                self.send_header("content-length", str(len(data)))
                self.end_headers()
                try:
                    self.wfile.write(data)
                except (BrokenPipeError, ConnectionResetError):
                    return

            def _forward_via_http_forward_proxy(
                self,
                target: str,
                body: bytes,
                headers: dict[str, str],
                proxy_url: str,
            ) -> None:
                proxy_parsed = urllib.parse.urlsplit(proxy_url)
                proxy_host = proxy_parsed.hostname
                if not proxy_host:
                    raise ValueError(f"Invalid HTTP proxy URL: {proxy_url!r}")
                proxy_port = proxy_parsed.port or 80
                request_headers = dict(headers)
                request_headers["Host"] = _host_header_for_url(target)
                if proxy_parsed.username:
                    username = urllib.parse.unquote(proxy_parsed.username)
                    password = urllib.parse.unquote(proxy_parsed.password or "")
                    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
                    request_headers["Proxy-Authorization"] = f"Basic {token}"

                conn = http.client.HTTPConnection(proxy_host, proxy_port, timeout=600)
                try:
                    request_body = body if self.command != "GET" else None
                    conn.request(self.command, target, body=request_body, headers=request_headers)
                    resp = conn.getresponse()
                    data = resp.read()
                    self.send_response(resp.status, resp.reason)
                    for key, value in resp.getheaders():
                        if key.lower() in _RESPONSE_SKIP_HEADERS:
                            continue
                        self.send_header(key, value)
                    self.send_header("content-length", str(len(data)))
                    self.end_headers()
                    try:
                        self.wfile.write(data)
                    except (BrokenPipeError, ConnectionResetError):
                        return
                except (BrokenPipeError, ConnectionResetError):
                    return
                except Exception as exc:
                    self._send_proxy_error(exc, target)
                finally:
                    conn.close()

            def _forward(self) -> None:
                body = self.rfile.read(int(self.headers.get("content-length") or 0))
                normalize_info: dict[str, Any] = {}
                if body:
                    try:
                        parsed_body = json.loads(body.decode("utf-8", errors="replace"))
                        if isinstance(parsed_body, dict):
                            parsed_body, normalize_info = _normalize_anthropic_request_body(parsed_body)
                            if normalize_info:
                                body = json.dumps(parsed_body, ensure_ascii=False).encode("utf-8")
                    except Exception:
                        normalize_info = {}
                self._record(body, normalize_info)
                target = urllib.parse.urljoin(upstream_base_url + "/", self.path.lstrip("/"))
                headers: dict[str, str] = {}
                for key, value in self.headers.items():
                    if key.lower() in _REQUEST_SKIP_HEADERS:
                        continue
                    headers[key] = value
                proxy_url = _get_proxy_for_url(target, proxy_env)
                if capture_proxy_mode != "urllib" and proxy_url and target.startswith("https://"):
                    self._forward_via_http_forward_proxy(target, body, headers, proxy_url)
                    return
                req = urllib.request.Request(target, data=body if self.command != "GET" else None, headers=headers, method=self.command)
                try:
                    with urllib.request.urlopen(req, timeout=600) as resp:
                        data = resp.read()
                        self.send_response(resp.status)
                        for key, value in resp.headers.items():
                            if key.lower() in _RESPONSE_SKIP_HEADERS:
                                continue
                            self.send_header(key, value)
                        self.send_header("content-length", str(len(data)))
                        self.end_headers()
                        try:
                            self.wfile.write(data)
                        except (BrokenPipeError, ConnectionResetError):
                            return
                except urllib.error.HTTPError as exc:
                    data = exc.read()
                    self.send_response(exc.code)
                    for key, value in exc.headers.items():
                        if key.lower() in _RESPONSE_SKIP_HEADERS:
                            continue
                        self.send_header(key, value)
                    self.send_header("content-length", str(len(data)))
                    self.end_headers()
                    try:
                        self.wfile.write(data)
                    except (BrokenPipeError, ConnectionResetError):
                        return
                except (BrokenPipeError, ConnectionResetError):
                    return
                except Exception as exc:
                    data = json.dumps({"error": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False).encode("utf-8")
                    self.send_response(502)
                    self.send_header("content-type", "application/json")
                    self.send_header("content-length", str(len(data)))
                    self.end_headers()
                    try:
                        self.wfile.write(data)
                    except (BrokenPipeError, ConnectionResetError):
                        return

            def do_GET(self) -> None:
                self._forward()

            def do_POST(self) -> None:
                self._forward()

        self._server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        return self

    @property
    def base_url(self) -> str:
        if self._server is None:
            raise RuntimeError("Claude request capture proxy is not running")
        host, port = self._server.server_address
        return f"http://{host}:{port}"

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=2)


def _run_claude_cli(
    sample_dir: str,
    prompt: str,
    claude_bin: str,
    llm_model: str,
    extra_args: list[str],
    claude_env: dict[str, str] | None,
    timeout: float | None,
    append_system_prompt: str = "",
    capture_requests: bool = False,
    proxy_requests: bool = False,
    capture_request_bodies: bool = True,
    capture_proxy_mode: str = "auto",
) -> dict[str, Any]:
    capture_proxy_mode = _normalize_capture_proxy_mode(capture_proxy_mode)
    base_cmd = [claude_bin, "--dangerously-skip-permissions", "-p"] + list(extra_args)
    if append_system_prompt.strip():
        base_cmd.extend(["--append-system-prompt", append_system_prompt.strip()])

    def _exec(command: list[str], env_override: dict[str, str] | None = None) -> dict[str, Any]:
        try:
            proc = subprocess.run(
                command,
                input=prompt,
                text=True,
                capture_output=True,
                cwd=sample_dir,
                check=False,
                env=env_override if env_override is not None else claude_env,
                timeout=timeout,
            )
            raw_stdout = _coerce_output_text(proc.stdout)
            parsed_stdout = _extract_stream_json_text(raw_stdout)
            return {
                "return_code": int(proc.returncode),
                "stdout": parsed_stdout,
                "raw_stdout": raw_stdout if raw_stdout != parsed_stdout else "",
                "stderr": _coerce_output_text(proc.stderr),
                "command": command,
            }
        except subprocess.TimeoutExpired as e:
            raw_stdout = _coerce_output_text(e.stdout)
            parsed_stdout = _extract_stream_json_text(raw_stdout)
            return {
                "return_code": 124,
                "stdout": parsed_stdout,
                "raw_stdout": raw_stdout if raw_stdout != parsed_stdout else "",
                "stderr": _coerce_output_text(e.stderr) or f"Claude CLI timed out after {timeout} seconds",
                "command": command,
            }
        except FileNotFoundError:
            return {
                "return_code": 127,
                "stdout": "",
                "stderr": f"Claude CLI not found: {claude_bin}",
                "command": command,
            }
        except Exception as e:
            return {
                "return_code": 1,
                "stdout": "",
                "stderr": str(e),
                "command": command,
            }

    tried_with_model = False
    res: dict[str, Any]

    exec_env = claude_env
    request_log_path = ""
    request_capture_upstream_base_url = ""
    proxy_cm: _ClaudeRequestCaptureProxy | None = None
    if (capture_requests or proxy_requests) and claude_env is not None:
        if capture_requests:
            request_log_path = os.path.join(sample_dir, "claude_requests.jsonl")
        request_capture_upstream_base_url = claude_env.get("ANTHROPIC_BASE_URL", "").strip() or "https://api.anthropic.com"
        proxy_cm = _ClaudeRequestCaptureProxy(
            request_capture_upstream_base_url,
            request_log_path,
            record_bodies=capture_request_bodies,
            proxy_env=claude_env,
            capture_proxy_mode=capture_proxy_mode,
        )
        proxy = proxy_cm.__enter__()
        exec_env = dict(claude_env)
        exec_env["ANTHROPIC_BASE_URL"] = proxy.base_url
        _append_no_proxy_entries(exec_env, ("127.0.0.1", "localhost", "::1"))

    try:
        if llm_model:
            tried_with_model = True
            cmd_with_model = base_cmd + ["--model", llm_model]
            res = _exec(cmd_with_model, exec_env)
            err_text = (res.get("stderr") or "").lower()
            unknown_model_flag = (
                "unknown option" in err_text
                or "unrecognized option" in err_text
                or "unexpected argument '--model'" in err_text
            )
            if unknown_model_flag:
                res = _exec(base_cmd, exec_env)
                res["model_flag_fallback"] = True
            else:
                res["model_flag_fallback"] = False
        else:
            res = _exec(base_cmd, exec_env)
            res["model_flag_fallback"] = False
    finally:
        if proxy_cm is not None:
            proxy_cm.__exit__(None, None, None)

    res["tried_with_model"] = tried_with_model
    if request_log_path:
        res["request_log_path"] = request_log_path
    if proxy_cm is not None:
        res["request_proxy_enabled"] = True
        res["request_capture_upstream_base_url"] = request_capture_upstream_base_url
    res["capture_proxy_mode"] = capture_proxy_mode
    return res


def _write_runner_markdown(
    sample_dir: str,
    dataset_name: str,
    question_idx: int,
    subtask: str,
    mode: str,
    model: str,
    prompt: str,
    cli_result: dict[str, Any],
    external_result_md: str,
    primary_text: str,
) -> None:
    out_path = os.path.join(sample_dir, "result.md")
    lines: list[str] = []
    lines.append(f"# Claude Result - {dataset_name}_{question_idx:04d}")
    lines.append("")
    lines.append(f"- dataset: `{dataset_name}`")
    lines.append(f"- subtask: `{subtask}`")
    lines.append(f"- question_idx: `{question_idx}`")
    lines.append(f"- mode: `{mode}`")
    lines.append(f"- model: `{model}`")
    lines.append(f"- return_code: `{cli_result.get('return_code')}`")
    lines.append("")

    lines.append("## Prompt")
    lines.append("")
    lines.append("```text")
    lines.append(prompt.rstrip())
    lines.append("```")
    lines.append("")

    lines.append("## CLI Command")
    lines.append("")
    cmd = cli_result.get("command") or []
    lines.append("```bash")
    lines.append(" ".join(shlex.quote(str(x)) for x in cmd))
    lines.append("```")
    lines.append("")

    lines.append("## Primary Text Used For Parsing")
    lines.append("")
    lines.append("```text")
    lines.append((primary_text or "").strip())
    lines.append("```")
    lines.append("")

    stdout = (cli_result.get("stdout") or "").strip()
    raw_stdout = (cli_result.get("raw_stdout") or "").strip()
    stderr = (cli_result.get("stderr") or "").strip()

    lines.append("## CLI STDOUT")
    lines.append("")
    lines.append("```text")
    lines.append(stdout)
    lines.append("```")
    lines.append("")

    if raw_stdout:
        lines.append("## CLI RAW STDOUT")
        lines.append("")
        lines.append("```text")
        lines.append(raw_stdout)
        lines.append("```")
        lines.append("")

    lines.append("## CLI STDERR")
    lines.append("")
    lines.append("```text")
    lines.append(stderr)
    lines.append("```")
    lines.append("")

    if external_result_md.strip():
        lines.append("## Claude Generated result.md (Original)")
        lines.append("")
        lines.append("```text")
        lines.append(external_result_md.rstrip())
        lines.append("```")
        lines.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def _run_one_claude(args: tuple[Any, ...]) -> tuple[int, dict | None]:
    (
        task_name,
        subtask,
        idx,
        sample,
        dataset_name,
        bench_run_dir,
        cfg,
        mode,
        claude_bin,
        extra_args,
        skills_src_dir,
        skills_materialization,
        claude_env,
        timeout,
    ) = args

    loader = get_loader(task_name)
    if not loader:
        return idx, None

    settings = cfg.get("settings", {})
    model_cfg = cfg.get("model", {}) or {}
    model = _resolve_model_name(model_cfg)
    seed = settings.get("seed")
    sample_claude_env = dict(claude_env) if claude_env is not None else None

    sample_dir = os.path.join(
        bench_run_dir,
        f"{_safe_name(dataset_name)}_{_safe_name(task_name)}_{_safe_name(subtask)}_{idx:04d}",
    )
    os.makedirs(sample_dir, exist_ok=True)
    if sample_claude_env is not None and _use_per_sample_claude_config(model_cfg):
        base_config_dir = sample_claude_env.get("CLAUDE_CONFIG_DIR") or os.path.join(sample_dir, ".claude_config")
        sample_config_dir = os.path.join(base_config_dir, f"{_safe_name(task_name)}_{_safe_name(subtask)}_{idx:04d}")
        os.makedirs(sample_config_dir, exist_ok=True)
        sample_claude_env["CLAUDE_CONFIG_DIR"] = sample_config_dir

    query = loader.get_query(sample, subtask)
    content = loader.get_dataset_content(sample, subtask)
    input_filename: str | None = None
    if content:
        input_filename = "candidates.smi" if task_name == "virtual_screening_curated" else "input.smi"
        input_path = os.path.join(sample_dir, input_filename)
        with open(input_path, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")

    claude_skills_dir = os.path.join(sample_dir, ".claude", "skills")
    _remove_path(claude_skills_dir)
    if mode == "both":
        if skills_materialization == "hardlink_snapshot":
            _record_hardlink_fallback(_hardlink_tree(skills_src_dir, claude_skills_dir))
        else:
            _copy_tree(skills_src_dir, claude_skills_dir)

    extra_answer_hint = getattr(loader, "get_extra_answer_hint", lambda s, t: None)(sample, subtask) or ANSWER_OUTPUT_HINT
    prompt = _build_prompt(query, extra_answer_hint, mode, input_filename)
    append_system_prompt = str(
        settings.get("append_system_prompt")
        or model_cfg.get("append_system_prompt")
        or settings.get("system_prompt")
        or model_cfg.get("system_prompt")
        or ""
    ).strip()
    append_system_prompt_source = (
        "settings.append_system_prompt"
        if settings.get("append_system_prompt")
        else "model.append_system_prompt"
        if model_cfg.get("append_system_prompt")
        else "settings.system_prompt"
        if settings.get("system_prompt")
        else "model.system_prompt"
        if model_cfg.get("system_prompt")
        else "none"
    )

    set_global_seed(seed)
    cli_result = _run_claude_cli(
        sample_dir=sample_dir,
        prompt=prompt,
        claude_bin=claude_bin,
        llm_model=str(model or ""),
        extra_args=extra_args,
        claude_env=sample_claude_env,
        timeout=timeout,
        append_system_prompt=append_system_prompt,
        capture_requests=bool(model_cfg.get("capture_claude_requests") or settings.get("capture_claude_requests")),
        proxy_requests=bool(
            model_cfg.get("proxy_claude_requests")
            or model_cfg.get("normalize_claude_requests")
            or settings.get("proxy_claude_requests")
            or settings.get("normalize_claude_requests")
        ),
        capture_request_bodies=not _is_truthy(
            model_cfg.get("capture_claude_request_metadata_only")
            or settings.get("capture_claude_request_metadata_only")
        ),
        capture_proxy_mode=str(model_cfg.get("capture_proxy_mode") or settings.get("capture_proxy_mode") or "auto"),
    )

    claude_result_md_path = os.path.join(sample_dir, "result.md")
    external_result_md = _read_text_if_exists(claude_result_md_path)
    if external_result_md:
        try:
            with open(os.path.join(sample_dir, "claude_result.md"), "w", encoding="utf-8") as f:
                f.write(external_result_md)
        except Exception:
            pass

    stdout = cli_result.get("stdout") or ""
    stderr = cli_result.get("stderr") or ""
    primary_text = _pick_primary_text(stdout, external_result_md, stderr)

    result: dict[str, Any] = {
        "summary": {
            "user_input": prompt,
            "claude_mode": mode,
            "llm_model": model,
            "return_code": cli_result.get("return_code"),
            "append_system_prompt": append_system_prompt,
            "append_system_prompt_source": append_system_prompt_source,
        },
        "action_history": [{"finish": primary_text}],
        "context": {
            "stdout": stdout,
            "raw_stdout": cli_result.get("raw_stdout") or "",
            "stderr": stderr,
            "command": cli_result.get("command", []),
            "request_log_path": cli_result.get("request_log_path", ""),
            "request_capture_upstream_base_url": cli_result.get("request_capture_upstream_base_url", ""),
            "request_capture_enabled": bool(cli_result.get("request_log_path")),
            "request_proxy_enabled": bool(cli_result.get("request_proxy_enabled")),
            "capture_proxy_mode": cli_result.get("capture_proxy_mode", ""),
            "claude_config_dir": (sample_claude_env or {}).get("CLAUDE_CONFIG_DIR", ""),
            "tried_with_model": cli_result.get("tried_with_model", False),
            "model_flag_fallback": cli_result.get("model_flag_fallback", False),
        },
    }

    if int(cli_result.get("return_code", 1)) != 0:
        result["error"] = f"Claude CLI failed with return code {cli_result.get('return_code')}"

    with open(os.path.join(sample_dir, "result.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    _write_runner_markdown(
        sample_dir=sample_dir,
        dataset_name=dataset_name,
        question_idx=idx,
        subtask=subtask,
        mode=mode,
        model=str(model),
        prompt=prompt,
        cli_result=cli_result,
        external_result_md=external_result_md,
        primary_text=primary_text,
    )

    raw_text = collect_result_text(result)
    parsed = loader.parse_agent_result(result, subtask)
    entry = loader.build_pred_entry(sample, parsed, raw_text, subtask)
    return idx, entry


def main() -> None:
    parser = argparse.ArgumentParser(description="Run llm_bench with Claude CLI.")
    parser.add_argument("--cfg", required=True, help="Launch YAML file path")
    parser.add_argument(
        "--claude-mode",
        default=None,
        choices=sorted(CLAUDE_MODES),
        help="Claude capability mode: non|both",
    )
    parser.add_argument(
        "--claude-bin",
        default=os.environ.get("CLAUDE_BIN", "claude"),
        help="Claude CLI executable name or path",
    )
    parser.add_argument(
        "--claude-extra-args",
        nargs="*",
        default=None,
        help="Additional CLI args appended to claude command",
    )
    args = parser.parse_args()

    cfg_path = os.path.abspath(args.cfg)
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    model_cfg = cfg.get("model", {}) or {}
    _load_dotenv(model_cfg.get("env_file"))

    bench_cfg = cfg.get("bench") or {}
    if not bench_cfg.get("enabled"):
        print("bench.enabled is not true; exiting.")
        sys.exit(0)

    mode = _resolve_cfg_mode(cfg, args.claude_mode)
    skills_materialization = _resolve_skills_materialization(cfg)
    settings = cfg.get("settings", {})
    extra_args = list(args.claude_extra_args or settings.get("claude_extra_args") or [])
    model = _resolve_model_name(model_cfg)
    claude_env, claude_env_info = _resolve_claude_subprocess_env(model_cfg)
    timeout = model_cfg.get("timeout") or settings.get("claude_timeout")
    timeout = float(timeout) if timeout is not None else None
    capture_proxy_mode = _normalize_capture_proxy_mode(
        model_cfg.get("capture_proxy_mode") or settings.get("capture_proxy_mode") or "auto"
    )
    seed = settings.get("seed")
    set_global_seed(seed)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    bench_run_dir = os.path.join(_llm_bench_root, "results", "agent_prediction", f"claude_run_{ts}")
    skills_src_dir = os.path.join(_llm_bench_root, "skills")
    os.makedirs(bench_run_dir, exist_ok=True)
    shutil.copy2(cfg_path, os.path.join(bench_run_dir, os.path.basename(cfg_path)))
    claude_env_info.update(_apply_claude_config_dir(claude_env, model_cfg, bench_run_dir))

    run_meta = {
        "claude_mode": mode,
        "claude_bin": args.claude_bin,
        "claude_extra_args": extra_args,
        "llm_model": model,
        "seed": seed,
        "claude_env": claude_env_info,
        "timeout": timeout,
        "capture_proxy_mode": capture_proxy_mode,
        "skills_materialization": skills_materialization,
    }
    run_meta.update(_git_run_metadata(cfg_path, skills_src_dir, os.path.abspath(__file__)))

    def _abs(p: str) -> str:
        return os.path.abspath(p) if os.path.isabs(p) else os.path.abspath(os.path.join(_llm_bench_root, p))

    data_path = bench_cfg.get("data_path")
    tasks = bench_cfg.get("tasks")
    dataset_name = bench_cfg.get("dataset") or "dataset"
    if not data_path or not tasks:
        raise ValueError("bench.data_path and bench.tasks are required")
    data_path = _abs(data_path)

    max_samples = bench_cfg.get("max_samples_per_subtask")
    max_process = max(1, int(bench_cfg.get("max_process") or bench_cfg.get("max_workers") or 1))
    configured_max_process = max_process
    run_meta["configured_max_process"] = configured_max_process
    run_meta["effective_max_process"] = max_process
    run_meta["per_sample_claude_config"] = _use_per_sample_claude_config(model_cfg)
    with open(os.path.join(bench_run_dir, "claude_run_meta.json"), "w", encoding="utf-8") as f:
        json.dump(run_meta, f, ensure_ascii=False, indent=2)

    skills_sample_src_dir = skills_src_dir
    skills_snapshot_dir = ""
    skills_manifest_path = ""
    skills_manifest: dict[str, Any] = {}
    if mode == "both":
        _assert_no_symlinks(skills_src_dir)
        if skills_materialization == "hardlink_snapshot":
            skills_snapshot_dir = os.path.join(bench_run_dir, "_shared", "skills")
            skills_manifest_path = os.path.join(bench_run_dir, "_shared", "skills_manifest.json")
            _remove_path(skills_snapshot_dir)
            _copy_tree(skills_src_dir, skills_snapshot_dir)
            skills_manifest = _tree_manifest(skills_snapshot_dir)
            os.makedirs(os.path.dirname(skills_manifest_path), exist_ok=True)
            with open(skills_manifest_path, "w", encoding="utf-8") as f:
                json.dump(skills_manifest, f, ensure_ascii=False, indent=2)
            _chmod_tree_readonly(skills_snapshot_dir)
            skills_sample_src_dir = skills_snapshot_dir
        else:
            skills_manifest = _tree_manifest(skills_src_dir)
        run_meta.update({
            "skills_source_dir": os.path.abspath(skills_src_dir),
            "skills_sample_source_dir": os.path.abspath(skills_sample_src_dir),
            "skills_snapshot_dir": os.path.abspath(skills_snapshot_dir) if skills_snapshot_dir else "",
            "skills_manifest_path": os.path.abspath(skills_manifest_path) if skills_manifest_path else "",
            "skills_file_count": skills_manifest.get("file_count", 0),
            "skills_total_size": skills_manifest.get("total_size", 0),
            "skills_tree_sha256": skills_manifest.get("tree_sha256", ""),
            "skills_hardlink_fallback_policy": "copy2_on_link_failure" if skills_materialization == "hardlink_snapshot" else "",
        })
        with open(os.path.join(bench_run_dir, "claude_run_meta.json"), "w", encoding="utf-8") as f:
            json.dump(run_meta, f, ensure_ascii=False, indent=2)

    group_order: list[tuple[str, str]] = []
    group_preds: dict[tuple[str, str], list[dict | None]] = {}
    all_args: list[tuple[Any, ...]] = []

    for task_name in tasks:
        loader = get_loader(task_name)
        if not loader:
            continue

        for subtask in _selected_subtasks(bench_cfg, task_name, loader):
            print(f"[Claude] Queue subtask: {task_name}/{subtask}", flush=True)
            samples = loader.load_data(data_path, subtask, max_samples)
            if not samples:
                print(f"[Claude] Skip subtask (no samples): {task_name}/{subtask}", flush=True)
                continue

            key = (task_name, subtask)
            group_order.append(key)
            group_preds[key] = [None] * len(samples)
            all_args.extend(
                (
                    task_name,
                    subtask,
                    idx,
                    sample,
                    dataset_name,
                    bench_run_dir,
                    cfg,
                    mode,
                    args.claude_bin,
                    extra_args,
                    skills_sample_src_dir,
                    skills_materialization,
                    claude_env,
                    timeout,
                )
                for idx, sample in enumerate(samples)
            )

    print(f"[Claude] Queued {len(all_args)} samples; running with max_process={max_process}.", flush=True)
    if max_process == 1:
        for one_arg in tqdm(all_args, desc="claude samples", leave=True):
            task_name, subtask, idx = one_arg[0], one_arg[1], one_arg[2]
            try:
                _, entry = _run_one_claude(one_arg)
            except Exception as e:
                print(f"[Claude] Failed sample {task_name}/{subtask}/{idx}: {e}", flush=True)
                entry = None
            if entry is not None:
                group_preds[(task_name, subtask)][idx] = entry
    else:
        with ThreadPoolExecutor(max_workers=max_process) as executor:
            future_to_key = {
                executor.submit(_run_one_claude, one_arg): (one_arg[0], one_arg[1], one_arg[2])
                for one_arg in all_args
            }
            for future in tqdm(
                as_completed(future_to_key),
                total=len(future_to_key),
                desc="claude samples",
                leave=True,
            ):
                task_name, subtask, idx = future_to_key[future]
                try:
                    _, entry = future.result()
                except Exception as e:
                    print(f"[Claude] Failed sample {task_name}/{subtask}/{idx}: {e}", flush=True)
                    entry = None
                if entry is not None:
                    group_preds[(task_name, subtask)][idx] = entry

    for task_name, subtask in group_order:
        pred_list = [x for x in group_preds[(task_name, subtask)] if x is not None]
        pred_dir = os.path.join(bench_run_dir, "preds", task_name)
        os.makedirs(pred_dir, exist_ok=True)
        pred_path = os.path.join(pred_dir, f"{subtask}.json")
        with open(pred_path, "w", encoding="utf-8") as f:
            json.dump(pred_list, f, ensure_ascii=False, indent=2)
        print(f"[Claude] Wrote {pred_path} ({len(pred_list)} entries)", flush=True)

    if mode == "both":
        run_meta["skills_hardlink_fallback_count"] = _get_hardlink_fallback_count()
        with open(os.path.join(bench_run_dir, "claude_run_meta.json"), "w", encoding="utf-8") as f:
            json.dump(run_meta, f, ensure_ascii=False, indent=2)

    print("RESULTS_DIR=" + os.path.abspath(bench_run_dir), flush=True)


if __name__ == "__main__":
    main()
