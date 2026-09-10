#!/usr/bin/env python3
"""
UX Transcribe — standalone pipeline for transcribing UX research interviews.

Usage:
    python3 transcribe_folder.py /path/to/interviews [--skip-existing] [--raw]

Reads MISTRAL_API_KEY from env or ~/.config/ux-transcribe/.env
Saves *_transcript.txt into the same folder as the source audio.

Speed optimizations:
  - Pipeline: formats file N while transcribing file N+1
  - Parallel formatting: processes 3 text chunks concurrently
  - --raw flag: skip formatting entirely (~2x faster)
"""

from __future__ import annotations

import asyncio
import functools
import json
import os
import re
import sys
import tempfile
import time
from codecs import BOM_UTF8
from datetime import datetime
from pathlib import Path

# Force unbuffered stdout for real-time progress in subprocesses
print = functools.partial(print, flush=True)

import subprocess

import httpx
from dotenv import load_dotenv

try:
    from mistralai import Mistral
except ImportError:
    from mistralai.client import Mistral

# ---------------------------------------------------------------------------
# Configuration — empirically tested Mistral free-tier limits
# ---------------------------------------------------------------------------
ALLOWED_EXTENSIONS = (".m4a", ".mp3", ".wav")
VIDEO_EXTENSIONS = (".mp4", ".mkv", ".webm")

MAX_CHUNK_DURATION_MINUTES = 40
MINI_SPLIT_THRESHOLD_MINUTES = 45
CHUNK_OVERLAP_SECONDS = 30
FORMATTER_MAX_CHARS = 12000
FORMATTER_CHUNK_CHARS = 10000
MAX_RETRIES = 6
RETRY_DELAY_TRANSCRIBE = 5
RETRY_DELAY_FORMAT = 10
INTER_CHUNK_DELAY = 3
FORMAT_CONCURRENCY = 3

VOXTRAL_MINI_MODEL = "voxtral-mini-latest"
CHAT_MODEL = "mistral-small-latest"
CHAT_MODEL_FALLBACK = "mistral-medium-latest"

MISTRAL_API_BASE = "https://api.mistral.ai/v1"


# ---------------------------------------------------------------------------
# Diagnostic collector — gathers metrics for debugging
# ---------------------------------------------------------------------------
class Diagnostic:
    def __init__(self):
        self.start_time = time.time()
        self.env = {
            "os": sys.platform,
            "python": sys.version.split()[0],
            "script": str(Path(__file__).resolve()),
        }
        try:
            import mistralai
            self.env["mistralai"] = getattr(mistralai, "__version__", "unknown")
        except Exception:
            self.env["mistralai"] = "import_failed"
        try:
            r = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=5)
            self.env["ffmpeg"] = r.stdout.split("\n")[0] if r.returncode == 0 else "error"
        except Exception:
            self.env["ffmpeg"] = "not_found"
        self.args: dict = {}
        self.files: list[dict] = []
        self.events: list[dict] = []
        self.summary: dict = {}

    def add_file(self, entry: dict):
        self.files.append(entry)

    def event(self, kind: str, **kwargs):
        """Record a timestamped event (retry, fallback, error, etc.)."""
        self.events.append({
            "t": round(time.time() - self.start_time, 1),
            "kind": kind,
            **kwargs,
        })

    def save(self, folder: str):
        self.summary["total_time_sec"] = round(time.time() - self.start_time, 1)
        self.summary["total_events"] = len(self.events)
        self.summary["retries"] = sum(1 for e in self.events if e["kind"] == "retry")
        self.summary["errors"] = sum(1 for e in self.events if e["kind"] == "error")
        report = {
            "generated": datetime.now().isoformat(),
            "env": self.env,
            "args": self.args,
            "files": self.files,
            "events": self.events,
            "summary": self.summary,
        }
        out_dir = os.path.join(folder, "transcripts")
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "_diagnostic.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n📋 Diagnostic saved: {path}")


diag = Diagnostic()

# ---------------------------------------------------------------------------
# Load API key — cross-platform config locations
# ---------------------------------------------------------------------------
def _find_config_env() -> Path:
    _script_dir = Path(__file__).resolve().parent.parent
    portable = _script_dir / ".env"

    if sys.platform == "win32":
        candidates = [
            portable,
            Path(os.environ.get("APPDATA", ""), "ux-transcribe", ".env"),
            Path("~/.config/ux-transcribe/.env").expanduser(),
        ]
    else:
        candidates = [
            portable,
            Path("~/.config/ux-transcribe/.env").expanduser(),
        ]
    for p in candidates:
        if p.exists():
            return p
    return candidates[-1]

_config_env = _find_config_env()
if _config_env.exists():
    load_dotenv(_config_env)

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
if not MISTRAL_API_KEY:
    if sys.platform == "win32":
        hint = r"%APPDATA%\ux-transcribe\.env"
    else:
        hint = "~/.config/ux-transcribe/.env"
    print("❌ MISTRAL_API_KEY not found.")
    print(f"   Set it in {hint} or as an environment variable.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------
def _check_ffmpeg():
    for tool in ("ffmpeg", "ffprobe"):
        try:
            subprocess.run([tool, "-version"], capture_output=True, timeout=5)
        except FileNotFoundError:
            print(f"❌ {tool} not found. Install ffmpeg:")
            if sys.platform == "darwin":
                print("   brew install ffmpeg")
            elif sys.platform == "win32":
                print("   winget install ffmpeg  OR  https://ffmpeg.org/download.html")
            else:
                print("   sudo apt install ffmpeg")
            sys.exit(1)

_check_ffmpeg()


def _is_ssl_error(exc: Exception) -> bool:
    """Check if an exception is caused by SSL certificate issues."""
    err_chain = str(exc).lower()
    cause = exc
    while cause.__cause__ or cause.__context__:
        cause = cause.__cause__ or cause.__context__
        err_chain += " " + str(cause).lower()
    ssl_keywords = ("certificate", "ssl", "self-signed", "self signed",
                    "verify", "cert_required", "certificate_verify")
    return any(kw in err_chain for kw in ssl_keywords)


def _classify_error(exc: Exception) -> str:
    """Classify an API error into a short category for diagnostics."""
    msg = str(exc).lower()
    if _is_ssl_error(exc):
        return "ssl"
    if "429" in msg or "rate limit" in msg:
        return "rate_limit_429"
    if "disconnect" in msg or "connection" in msg:
        return "disconnect"
    if "timeout" in msg:
        return "timeout"
    if "500" in msg or "502" in msg or "503" in msg:
        return "server_5xx"
    return "other"


def _export_system_certs() -> str | None:
    """Export system CA certificates to a temp PEM file (macOS only)."""
    if sys.platform != "darwin":
        return None
    pem_path = os.path.join(tempfile.gettempdir(), "ux-transcribe-ca-bundle.pem")
    try:
        keychains = [
            "/Library/Keychains/System.keychain",
            "/System/Library/Keychains/SystemRootCertificates.keychain",
        ]
        pem_data = b""
        for kc in keychains:
            if os.path.exists(kc):
                result = subprocess.run(
                    ["security", "find-certificate", "-a", "-p", kc],
                    capture_output=True, timeout=15,
                )
                if result.returncode == 0:
                    pem_data += result.stdout
        if pem_data:
            with open(pem_path, "wb") as f:
                f.write(pem_data)
            return pem_path
    except Exception as exc:
        print(f"  ⚠ Could not export system certificates: {exc}")
    return None


def _resolve_ssl_context() -> str | bool | None:
    """Probe Mistral API and resolve SSL verification strategy.

    Returns:
        None  — default verification works fine
        str   — path to CA bundle PEM file (system certs exported)
    """
    try:
        httpx.head(MISTRAL_API_BASE, timeout=10)
        return None
    except Exception as exc:
        if not _is_ssl_error(exc):
            return None

    pem_path = _export_system_certs()
    if pem_path:
        try:
            httpx.head(MISTRAL_API_BASE, timeout=10, verify=pem_path)
            print("✅ Corporate proxy detected — using system certificates.")
            return pem_path
        except Exception:
            pass

    print("⚠️  Corporate proxy detected, but the system certificates didn't help.")
    print("   Get the corporate proxy's root certificate from your IT department.")
    print("   Save it and set its path in the SSL_CERT_FILE variable:")
    print("   export SSL_CERT_FILE=/path/to/corporate-ca.pem")
    sys.exit(1)


_ssl_cert_env = os.getenv("SSL_CERT_FILE", "").strip()
if _ssl_cert_env and os.path.isfile(_ssl_cert_env):
    _ssl_verify = _ssl_cert_env
    print(f"✅ Using the CA certificate from SSL_CERT_FILE: {_ssl_cert_env}")
else:
    _ssl_verify = _resolve_ssl_context()

# ---------------------------------------------------------------------------
# Mistral clients
# ---------------------------------------------------------------------------
_httpx_kwargs: dict = dict(timeout=httpx.Timeout(600.0, connect=30.0))
if _ssl_verify is not None:
    _httpx_kwargs["verify"] = _ssl_verify

_http_client = httpx.Client(**_httpx_kwargs)
_transcribe_client = httpx.Client(**_httpx_kwargs)
_client = Mistral(
    api_key=MISTRAL_API_KEY,
    timeout_ms=1200000,
    client=_http_client,
)

_format_http_client = httpx.Client(**_httpx_kwargs)
_format_client = Mistral(
    api_key=MISTRAL_API_KEY,
    timeout_ms=600000,
    client=_format_http_client,
)

# ---------------------------------------------------------------------------
# Video → Audio extraction
# ---------------------------------------------------------------------------
def extract_audio_from_video(video_path: str) -> str:
    """Extract audio track from a video file via ffmpeg. Returns path to .m4a."""
    base = os.path.splitext(video_path)[0]
    audio_path = base + ".m4a"
    if os.path.exists(audio_path):
        print(f"  Audio already exists: {os.path.basename(audio_path)}")
        return audio_path

    print(f"  Extracting audio from {os.path.basename(video_path)}...")
    result = subprocess.run(
        ["ffmpeg", "-i", video_path, "-vn", "-acodec", "aac", "-y", audio_path],
        capture_output=True, text=True, timeout=600,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr[-300:]}")
    print(f"  ✅ Extracted: {os.path.basename(audio_path)}")
    return audio_path


# ---------------------------------------------------------------------------
# Audio utilities (pure ffmpeg — no pydub, works on any Python version)
# ---------------------------------------------------------------------------
def get_audio_duration(file_path: str) -> float:
    """Get audio duration in seconds via ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", file_path],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {file_path}: {result.stderr[-200:]}")
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def split_audio(file_path: str, max_duration_min: int, overlap_sec: int) -> list[str]:
    """Split audio into chunks via ffmpeg. No pydub dependency."""
    duration_sec = get_audio_duration(file_path)
    max_duration_sec = max_duration_min * 60

    if duration_sec <= max_duration_sec:
        return [file_path]

    ext = os.path.splitext(file_path)[1]
    chunk_paths: list[str] = []
    start = 0.0
    idx = 0

    while start < duration_sec:
        chunk_len = min(max_duration_sec, duration_sec - start)
        tmp = tempfile.NamedTemporaryFile(
            suffix=ext, prefix=f"chunk_{idx:02d}_", delete=False
        )
        tmp.close()

        cmd = [
            "ffmpeg", "-y", "-i", file_path,
            "-ss", str(start), "-t", str(chunk_len),
            "-acodec", "copy", tmp.name,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg split failed: {result.stderr[-200:]}")

        chunk_paths.append(tmp.name)
        idx += 1
        next_start = start + chunk_len - overlap_sec
        if start + chunk_len >= duration_sec:
            break
        start = next_start

    return chunk_paths


def cleanup_chunks(chunk_paths: list[str], original_path: str) -> None:
    for path in chunk_paths:
        if path != original_path and os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Transcription — Voxtral Mini via HTTP (SDK lacks diarize param)
# ---------------------------------------------------------------------------
async def upload_to_mistral(file_path: str) -> str:
    filename = os.path.basename(file_path)

    def _upload():
        with open(file_path, "rb") as f:
            uploaded = _client.files.upload(
                file={"content": f, "file_name": filename},
                purpose="audio",
            )
        return uploaded.id

    return await asyncio.to_thread(_upload)


async def transcribe_chunk(file_path: str) -> dict:
    filename = os.path.basename(file_path)
    file_id = await upload_to_mistral(file_path)

    def _call():
        resp = _transcribe_client.post(
            f"{MISTRAL_API_BASE}/audio/transcriptions",
            data={
                "model": VOXTRAL_MINI_MODEL,
                "file_id": file_id,
                "diarize": "true",
                "timestamp_granularities": "segment",
                "language": "ru",
            },
            headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Mistral API HTTP {resp.status_code}: {resp.text[:500]}")
        return resp.json()

    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = await asyncio.to_thread(_call)
            break
        except Exception as exc:
            last_err = exc
            err_type = _classify_error(exc)
            diag.event("retry", stage="transcribe", file=filename,
                       attempt=attempt, error_type=err_type,
                       error=str(exc)[:200])
            print(f"  ⚠ Transcription attempt {attempt}/{MAX_RETRIES} failed: {exc}")
            if attempt < MAX_RETRIES:
                delay = RETRY_DELAY_TRANSCRIBE * (2 ** (attempt - 1))
                print(f"  Retrying in {delay}s...")
                await asyncio.sleep(delay)
    else:
        diag.event("error", stage="transcribe", file=filename,
                   error=f"All {MAX_RETRIES} attempts failed: {last_err}")
        try:
            await asyncio.to_thread(lambda: _client.files.delete(file_id=file_id))
        except Exception:
            pass
        raise RuntimeError(f"Transcription failed after {MAX_RETRIES} attempts: {last_err}")

    try:
        await asyncio.to_thread(lambda: _client.files.delete(file_id=file_id))
    except Exception:
        pass

    return result


# ---------------------------------------------------------------------------
# Segment processing
# ---------------------------------------------------------------------------
def extract_segments(response: dict) -> list[dict]:
    segments = []
    for seg in response.get("segments", []):
        segments.append({
            "start": seg.get("start", 0),
            "end": seg.get("end", 0),
            "text": (seg.get("text", "") or "").strip(),
            "speaker": seg.get("speaker_id") or seg.get("speaker"),
        })
    if not segments:
        text = response.get("text", "")
        if text:
            segments.append({"start": 0, "end": 0, "text": text, "speaker": None})
    return segments


def merge_segments(all_segments: list[list[dict]], chunk_offsets: list[float]) -> list[dict]:
    if len(all_segments) == 1:
        return all_segments[0]

    merged: list[dict] = []
    for chunk_idx, (segs, offset) in enumerate(zip(all_segments, chunk_offsets)):
        for seg in segs:
            if chunk_idx > 0 and seg["start"] < CHUNK_OVERLAP_SECONDS:
                continue
            merged.append({
                "start": seg["start"] + offset,
                "end": seg["end"] + offset,
                "text": seg["text"],
                "speaker": seg["speaker"],
            })
    return merged


def merge_speakers(segments: list[dict], expected_count: int) -> list[dict]:
    """Collapse extra speaker IDs down to expected_count by speech volume.

    Voxtral sometimes assigns different speaker_ids to the same person across
    audio chunks. This merges the smallest speakers into the closest major one.
    """
    from collections import Counter
    speaker_chars: Counter = Counter()
    for seg in segments:
        sp = seg.get("speaker") or "unknown"
        speaker_chars[sp] += len(seg.get("text", ""))

    unique = speaker_chars.most_common()
    if len(unique) <= expected_count:
        return segments

    kept_list = [sp for sp, _ in unique[:expected_count]]
    merge_map: dict[str, str] = {}
    for sp, _ in unique[expected_count:]:
        merge_map[sp] = kept_list[-1]

    print(f"  ⚠ Found {len(unique)} speakers, merging to {expected_count}: "
          f"{', '.join(f'{k}→{v}' for k, v in merge_map.items())}")

    result = []
    for seg in segments:
        new_seg = dict(seg)
        sp = new_seg.get("speaker") or "unknown"
        if sp in merge_map:
            new_seg["speaker"] = merge_map[sp]
        result.append(new_seg)
    return result


# ---------------------------------------------------------------------------
# Session types — fixed roles and speaker counts
# ---------------------------------------------------------------------------
SESSION_TYPES = {
    "ux-interview": {
        "label": "In-depth interview",
        "expected_speakers": 2,
        "roles": {0: "Interviewer", 1: "Respondent"},
        "role_hint": "speaker with less text is the Interviewer",
    },
    "meeting": {
        "label": "Working meeting",
        "expected_speakers": None,
        "roles": None,
    },
    "presentation": {
        "label": "Presentation",
        "expected_speakers": None,
        "roles": None,
    },
}


def _detect_interviewer(segments: list[dict]) -> str | None:
    """Identify the interviewer by analysing the first ~20 segments.

    Heuristics (in priority order):
    1. The speaker who talks first in the opening is usually the interviewer
       (they greet, introduce themselves, explain the process).
    2. Among the first 20 segments, the speaker with more segments is the
       interviewer (they drive the conversation with short cues/questions).
    """
    if not segments:
        return None

    first_speakers: list[str] = []
    for seg in segments[:20]:
        sp = seg.get("speaker")
        if sp and sp not in first_speakers:
            first_speakers.append(sp)

    if not first_speakers:
        return None

    opening_speaker = first_speakers[0]
    opening_count = sum(
        1 for seg in segments[:20] if seg.get("speaker") == opening_speaker
    )
    other_count = len([s for s in segments[:20] if s.get("speaker")]) - opening_count

    if opening_count >= other_count:
        return opening_speaker

    return opening_speaker


def fixed_roles_for_type(
    session_type: str, segments: list[dict],
) -> tuple[str, dict[str, str]]:
    """Return (label, role_map) using Speaker N labels.

    For ux-interview: detect the interviewer by opening segment analysis,
    assign the other speaker as the Respondent.
    The role_map keys are 'Speaker N' to match segments_to_raw_text() output.
    """
    cfg = SESSION_TYPES.get(session_type)
    if not cfg or cfg["roles"] is None:
        return "", {}

    from collections import Counter
    speaker_order: list[str] = []
    for seg in segments:
        sp = seg.get("speaker") or "unknown"
        if sp not in speaker_order:
            speaker_order.append(sp)

    raw_to_speaker_n: dict[str, str] = {}
    for i, sp in enumerate(speaker_order):
        raw_to_speaker_n[sp] = f"Speaker {i}"

    fixed = cfg["roles"]
    role_map: dict[str, str] = {}

    interviewer_raw = _detect_interviewer(segments)
    if interviewer_raw and session_type == "ux-interview":
        for raw_sp in speaker_order:
            label = raw_to_speaker_n[raw_sp]
            if raw_sp == interviewer_raw:
                role_map[label] = "Interviewer"
            else:
                role_map[label] = "Respondent"
    else:
        for i, raw_sp in enumerate(speaker_order):
            label = raw_to_speaker_n[raw_sp]
            if i in fixed:
                role_map[label] = fixed[i]
            else:
                role_map[label] = fixed.get(len(fixed) - 1, f"Participant {i}")

    return cfg["label"], role_map


# ---------------------------------------------------------------------------
# Formatting — Mistral Chat API
# ---------------------------------------------------------------------------
CONTEXT_DETECTION_PROMPT = """\
Below is the beginning of an audio transcript with participants (Speaker 0, Speaker 1, ...).

Your task:
1. Determine the recording type: "In-depth interview", "Interview", "Working meeting", "Presentation", "Lecture", or another fitting label.
2. For each Speaker N, pick a structural role based on the context of the conversation:
   - If it's an interview (2 people): "Interviewer" and "Respondent"
   - If it's a meeting (2+ people): "Moderator", "Participant 1", "Participant 2", ...
   - If it's a presentation/lecture (1 main speaker): "Speaker", the rest — "Listener 1", "Listener 2", ...

IMPORTANT: use ONLY structural roles. Do NOT add personal names, parenthetical clarifications, or other notes. The role must be the same throughout a single recording type — for example, always "Respondent", not "Respondent (Olga)".

Respond STRICTLY in JSON format (nothing else):
{"type": "recording type", "roles": {"Speaker 0": "Role", "Speaker 1": "Role"}}\
"""

FORMATTING_PROMPT = """\
You are a transcript formatter. You work with text only.

Input: a transcript with roles and timecodes (format [start – end] or [start]).

Task: clean up the text of each turn:
1. Remove meaningless filler words (uh, umm, like), repeated words.
2. Preserve meaningful pauses → (pause).
3. Contextual notes in parentheses: (laughs), (inaudible), (pauses to think).
4. Each turn is one coherent paragraph.
5. Timecodes and roles are already determined — carry them over as-is, do NOT change the timecode format.

Return JSON: {"turns": [{"ts": "...", "role": "...", "text": "..."}]}

Example input:
[00:00 – 00:07] Moderator: Uh good afternoon, well let's get started let's.
[00:08 – 00:14] Participant 1: Hello, I uh think that we can probably begin.

Example output:
{"turns": [{"ts": "[00:00 – 00:07]", "role": "Moderator", "text": "Good afternoon! Let's get started."}, {"ts": "[00:08 – 00:14]", "role": "Participant 1", "text": "Hello. I think we can begin."}]}\
"""


def format_timestamp(seconds: float, long_format: bool) -> str:
    total = int(seconds)
    h, remainder = divmod(total, 3600)
    m, s = divmod(remainder, 60)
    if long_format:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def segments_to_raw_text(segments: list[dict], long_format: bool) -> str:
    speaker_map: dict = {}
    counter = 0
    lines: list[str] = []
    for seg in segments:
        start_ts = format_timestamp(seg.get("start", 0), long_format)
        end_val = seg.get("end", 0)
        start_val = seg.get("start", 0)
        if end_val and end_val > start_val:
            end_ts = format_timestamp(end_val, long_format)
            ts = f"[{start_ts} – {end_ts}]"
        else:
            ts = f"[{start_ts}]"

        raw_speaker = seg.get("speaker") or ""
        if raw_speaker and raw_speaker not in speaker_map:
            speaker_map[raw_speaker] = f"Speaker {counter}"
            counter += 1
        speaker_label = speaker_map.get(raw_speaker, "Speaker")
        text = seg.get("text", "").strip()
        if text:
            lines.append(f"{ts} {speaker_label}: {text}")
    return "\n".join(lines)


def split_raw_text(raw_text: str, max_chars: int) -> list[str]:
    lines = raw_text.split("\n")
    chunks: list[str] = []
    current_lines: list[str] = []
    current_len = 0

    for line in lines:
        line_len = len(line) + 1
        if current_len + line_len > max_chars and current_lines:
            chunks.append("\n".join(current_lines))
            current_lines = []
            current_len = 0
        current_lines.append(line)
        current_len += line_len

    if current_lines:
        chunks.append("\n".join(current_lines))
    return chunks


async def call_chat(
    prompt: str, raw_text: str, model: str = "",
    temperature: float = 0.0, json_mode: bool = False,
) -> str:
    chosen_model = model or CHAT_MODEL

    def _call():
        kwargs: dict = dict(
            model=chosen_model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": raw_text},
            ],
            temperature=temperature,
            timeout_ms=600000,
        )
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        response = _format_client.chat.complete(**kwargs)
        return response.choices[0].message.content

    return await asyncio.to_thread(_call)


_sticky_model: str | None = None


async def call_chat_with_retry(
    prompt: str, raw_text: str, json_mode: bool = False,
) -> str:
    global _sticky_model

    if _sticky_model:
        models = [_sticky_model]
    else:
        models = [CHAT_MODEL, CHAT_MODEL_FALLBACK]

    last_err = None

    for model in models:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                result = await call_chat(
                    prompt, raw_text, model=model, json_mode=json_mode,
                )
                if not _sticky_model:
                    _sticky_model = model
                    diag.event("model_selected", stage="format", model=model)
                return result
            except Exception as exc:
                last_err = exc
                err_type = _classify_error(exc)
                err_str = str(exc).lower()
                if "capacity" in err_str or "rate" in err_str or "overloaded" in err_str:
                    diag.event("model_fallback", stage="format",
                               from_model=model, to_model=CHAT_MODEL_FALLBACK,
                               reason=err_type)
                    print(f"  ⚠ Model {model} overloaded, trying fallback...")
                    _sticky_model = CHAT_MODEL_FALLBACK
                    break
                diag.event("retry", stage="format", model=model,
                           attempt=attempt, error_type=err_type,
                           error=str(exc)[:200])
                print(f"  ⚠ Formatting ({model}) attempt {attempt}/{MAX_RETRIES}: {exc}")
                if attempt < MAX_RETRIES:
                    delay = RETRY_DELAY_FORMAT * (2 ** (attempt - 1))
                    await asyncio.sleep(delay)

    if _sticky_model and _sticky_model not in models:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return await call_chat(
                    prompt, raw_text, model=_sticky_model, json_mode=json_mode,
                )
            except Exception as exc:
                last_err = exc
                err_type = _classify_error(exc)
                diag.event("retry", stage="format_fallback", model=_sticky_model,
                           attempt=attempt, error_type=err_type,
                           error=str(exc)[:200])
                print(f"  ⚠ Formatting ({_sticky_model}) attempt {attempt}/{MAX_RETRIES}: {exc}")
                if attempt < MAX_RETRIES:
                    delay = RETRY_DELAY_FORMAT * (2 ** (attempt - 1))
                    await asyncio.sleep(delay)

    diag.event("error", stage="format",
               error=f"All attempts failed: {last_err}")
    raise RuntimeError(f"Formatting failed after all attempts: {last_err}")


def build_header(source_filename: str, duration_seconds: float, session_type: str = "") -> str:
    total = int(duration_seconds)
    h, remainder = divmod(total, 3600)
    m, s = divmod(remainder, 60)
    dur_str = f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"
    date_str = datetime.now().strftime("%d.%m.%Y")
    title = f"TRANSCRIPT — {session_type.upper()}" if session_type else "TRANSCRIPT"

    return (
        "============================================\n"
        f"{title}\n"
        "============================================\n"
        f"Source file: {source_filename}\n"
        f"Transcription date: {date_str}\n"
        f"Audio duration: {dur_str}\n"
        f"Model: Voxtral Mini Transcribe V2\n"
        "============================================\n\n"
    )


_cached_context: tuple[str, dict[str, str]] | None = None


async def detect_context(
    raw_text: str, use_cache: bool = True,
) -> tuple[str, dict[str, str]]:
    """Detect session type and speaker roles. Returns (type, role_mapping).

    When use_cache=True and a previous result exists, reuse it to ensure
    consistency across files in the same batch.
    """
    global _cached_context
    if use_cache and _cached_context is not None:
        return _cached_context

    sample = raw_text[:3000]
    try:
        answer = await call_chat(CONTEXT_DETECTION_PROMPT, sample, json_mode=True)
        data = json.loads(answer)
        session_type = data.get("type", "")
        roles = data.get("roles", {})
        if roles and all(k.startswith("Speaker") for k in roles):
            result = (session_type, roles)
            _cached_context = result
            return result
    except Exception as exc:
        print(f"  ⚠ Context detection failed, using defaults: {exc}")

    speakers = set(re.findall(r"Speaker \d+", raw_text))
    if len(speakers) == 2:
        result = ("", {"Speaker 0": "Interviewer", "Speaker 1": "Respondent"})
    else:
        result = ("", {s: f"Participant {s.split()[-1]}" for s in sorted(speakers)})
    _cached_context = result
    return result


def apply_roles(raw_text: str, role_map: dict[str, str]) -> str:
    """Replace Speaker N labels with role names. Unmapped speakers become Participant N."""
    result = raw_text
    for speaker, role in sorted(role_map.items(), key=lambda x: x[0], reverse=True):
        result = result.replace(f"{speaker}:", f"{role}:")
    result = re.sub(r"Speaker (\d+):", lambda m: f"Participant {m.group(1)}:", result)
    return result


def _turns_to_text(turns: list[dict]) -> str:
    """Convert list of turn dicts to formatted text with consistent structure."""
    lines: list[str] = []
    prev_ts = ""
    for turn in turns:
        ts = turn.get("ts", "").strip()
        role = turn.get("role", "").strip()
        text = turn.get("text", "").strip()
        if not text:
            continue
        if not ts:
            ts = prev_ts
        if ts:
            prev_ts = ts
        lines.append(f"{ts} {role}: {text}")
    return "\n\n".join(lines)


def _parse_json_turns(raw_json: str) -> list[dict] | None:
    """Try to parse JSON response into a list of turn dicts."""
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError:
        return None

    turns = data.get("turns") if isinstance(data, dict) else None
    if isinstance(turns, list) and len(turns) > 0:
        if all(isinstance(t, dict) and "text" in t for t in turns):
            return turns
    return None


def _extract_json_from_text(text: str) -> list[dict] | None:
    """Try to find and parse a JSON block embedded in mixed text."""
    for pattern in (r'\{[\s\S]*"turns"\s*:\s*\[[\s\S]*\]\s*\}', r'\[[\s\S]*\{[\s\S]*"text"[\s\S]*\}[\s\S]*\]'):
        match = re.search(pattern, text)
        if match:
            turns = _parse_json_turns(match.group())
            if turns:
                return turns
    return None


async def _format_chunk_json(raw_chunk: str) -> str:
    """Format a single chunk via JSON mode, with fallback to clean raw text."""
    response = await call_chat_with_retry(FORMATTING_PROMPT, raw_chunk, json_mode=True)

    turns = _parse_json_turns(response)
    if turns:
        return _turns_to_text(turns)

    turns = _extract_json_from_text(response)
    if turns:
        diag.event("json_fallback", detail="extracted_from_mixed_text",
                   response_len=len(response))
        print("  ⚠ Extracted JSON from mixed response")
        return _turns_to_text(turns)

    diag.event("json_fallback", detail="parse_failed_used_raw",
               response_preview=response[:200])
    print("  ⚠ JSON parse failed, using unformatted input chunk")
    return raw_chunk


_JSON_NOISE_RE = re.compile(
    r'(?:\{"turns"\s*:\s*\[.*?\]\s*\}|\{"ts"\s*:.*?\})', re.DOTALL,
)


def sanitize_transcript(text: str) -> str:
    """Remove or convert stray JSON fragments embedded in formatted text."""
    def _replace(m: re.Match) -> str:
        turns = _parse_json_turns(m.group())
        if turns:
            return _turns_to_text(turns)
        extracted = _extract_json_from_text(m.group())
        if extracted:
            return _turns_to_text(extracted)
        return ""

    return _JSON_NOISE_RE.sub(_replace, text)


def validate_transcript(text: str, filename: str) -> list[str]:
    """Run QA checks on the final transcript text. Returns list of warnings."""
    warnings: list[str] = []

    json_fragments = re.findall(r'\{"(?:turns|ts|role)":', text)
    if json_fragments:
        warnings.append(f"Found {len(json_fragments)} JSON fragment(s) in text")

    ts_pattern = re.compile(r'\[(\d+:\d{2}:\d{2}|\d{2}:\d{2})(?:\s*–\s*(?:\d+:\d{2}:\d{2}|\d{2}:\d{2}))?\]')
    timestamps = []
    for m in ts_pattern.finditer(text):
        parts = m.group(1).split(":")
        if len(parts) == 3:
            sec = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        else:
            sec = int(parts[0]) * 60 + int(parts[1])
        timestamps.append(sec)

    for i in range(1, len(timestamps)):
        if timestamps[i] < timestamps[i - 1] - 5:
            warnings.append(
                f"Timestamp goes backwards at position {i}: "
                f"{timestamps[i-1]}s → {timestamps[i]}s"
            )
            break

    for i in range(1, len(timestamps)):
        gap = timestamps[i] - timestamps[i - 1]
        if gap > 300:
            warnings.append(
                f"Large gap ({gap // 60} min) between timestamps at "
                f"{timestamps[i-1]}s → {timestamps[i]}s"
            )

    roles = set(re.findall(r'\] ([^:]+):', text))
    if len(roles) > 6:
        warnings.append(f"Too many distinct roles ({len(roles)}): {', '.join(sorted(roles))}")

    return warnings


def _apply_merge_and_roles(
    segments: list[dict], session_type_hint: str,
) -> tuple[list[dict], str, dict[str, str]]:
    """Apply speaker merge and determine roles. Returns (segments, type_label, role_map)."""
    stype = session_type_hint if session_type_hint != "auto" else ""
    cfg = SESSION_TYPES.get(stype) if stype else None

    if cfg and cfg.get("expected_speakers"):
        segments = merge_speakers(segments, cfg["expected_speakers"])

    if cfg and cfg.get("roles") is not None:
        session_type, role_map = fixed_roles_for_type(stype, segments)
    else:
        session_type = ""
        role_map = {}

    return segments, session_type, role_map


async def format_transcript(
    segments: list[dict], duration: float, filename: str,
    long_format: bool = False, session_type_hint: str = "auto",
) -> tuple[str, list[dict], dict[str, str]]:
    """Format transcript via Chat API. Returns (text, processed_segments, role_map)."""
    long_format = long_format or duration > 3600

    segments, session_type, role_map = _apply_merge_and_roles(segments, session_type_hint)

    raw_text = segments_to_raw_text(segments, long_format)

    if not role_map:
        session_type, role_map = await detect_context(raw_text)
        detected_key = next(
            (k for k, v in SESSION_TYPES.items() if v["label"] == session_type),
            None,
        )
        detected_cfg = SESSION_TYPES.get(detected_key) if detected_key else None
        if detected_cfg and detected_cfg.get("expected_speakers"):
            segments = merge_speakers(segments, detected_cfg["expected_speakers"])
            raw_text = segments_to_raw_text(segments, long_format)
            session_type, role_map = fixed_roles_for_type(detected_key, segments)

    if session_type:
        print(f"  Type: {session_type}")
    print(f"  Roles: {', '.join(f'{k} → {v}' for k, v in role_map.items())}")
    raw_text = apply_roles(raw_text, role_map)

    diag.event("format_start", file=filename, raw_chars=len(raw_text))
    if len(raw_text) <= FORMATTER_MAX_CHARS:
        formatted = await _format_chunk_json(raw_text)
        diag.event("format_done", file=filename, format_chunks=1)
    else:
        chunks = split_raw_text(raw_text, FORMATTER_CHUNK_CHARS)
        total_chunks = len(chunks)
        print(f"  Formatting in {total_chunks} chunks ({FORMAT_CONCURRENCY} parallel)...")

        sem = asyncio.Semaphore(FORMAT_CONCURRENCY)
        done_count = 0

        async def _format_one(idx: int, chunk: str) -> str:
            nonlocal done_count
            async with sem:
                result = await _format_chunk_json(chunk)
                done_count += 1
                print(f"  Formatted chunk {done_count}/{total_chunks}")
                return result

        tasks = [_format_one(i, c) for i, c in enumerate(chunks)]
        parts = await asyncio.gather(*tasks)
        formatted = "\n\n".join(parts)
        diag.event("format_done", file=filename, format_chunks=total_chunks)

    header = build_header(filename, duration, session_type)
    return header + formatted, segments, role_map


def build_raw_transcript(segments: list[dict], duration: float, filename: str, long_format: bool = False) -> str:
    """Build transcript without LLM formatting — just clean up raw segments."""
    long_format = long_format or duration > 3600
    raw_text = segments_to_raw_text(segments, long_format)
    lines: list[str] = []
    for line in raw_text.split("\n"):
        stripped = line.strip()
        if stripped:
            lines.append(stripped)
    header = build_header(filename, duration)
    return header + "\n\n".join(lines)


# ---------------------------------------------------------------------------
# Two-phase pipeline: transcribe (phase 1) then format (phase 2)
# ---------------------------------------------------------------------------
async def transcribe_file(file_path: str, file_index: int, total_files: int) -> dict:
    """Phase 1: split → upload → transcribe → merge segments. No LLM formatting."""
    filename = os.path.basename(file_path)
    prefix = f"[{file_index}/{total_files}]"
    file_diag: dict = {"filename": filename, "status": "started"}
    t0 = time.time()

    duration = get_audio_duration(file_path)
    dur_min = duration / 60
    file_diag["duration_min"] = round(dur_min, 1)
    file_diag["size_mb"] = round(os.path.getsize(file_path) / 1024 / 1024, 1)
    print(f"{prefix} Processing {filename} ({dur_min:.1f} min)...")

    threshold = MINI_SPLIT_THRESHOLD_MINUTES * 60
    needs_split = duration > threshold

    if needs_split:
        chunk_paths = split_audio(file_path, MAX_CHUNK_DURATION_MINUTES, CHUNK_OVERLAP_SECONDS)
        print(f"{prefix} Split into {len(chunk_paths)} chunks")
    else:
        chunk_paths = [file_path]

    file_diag["audio_chunks"] = len(chunk_paths)
    retries = 0

    try:
        all_segments: list[list[dict]] = []
        chunk_offsets: list[float] = []
        offset = 0.0
        total_chunks = len(chunk_paths)

        for i, cpath in enumerate(chunk_paths):
            if total_chunks > 1:
                print(f"{prefix} Transcribing chunk {i + 1}/{total_chunks}...")
            else:
                print(f"{prefix} Transcribing...")

            response = await transcribe_chunk(cpath)
            segs = extract_segments(response)
            all_segments.append(segs)
            chunk_offsets.append(offset)

            if needs_split and segs:
                last_end = max(s["end"] for s in segs)
                offset += last_end - CHUNK_OVERLAP_SECONDS

            if i < total_chunks - 1:
                await asyncio.sleep(INTER_CHUNK_DELAY)

        merged = merge_segments(all_segments, chunk_offsets)
        file_diag["segments_count"] = len(merged)
        file_diag["transcribe_sec"] = round(time.time() - t0, 1)
        print(f"{prefix} ✅ Transcription done")

        return {
            "filename": filename, "segments": merged,
            "duration": duration, "file_path": file_path,
            "file_index": file_index, "total_files": total_files,
            "_diag": file_diag,
        }

    except Exception as exc:
        file_diag["status"] = "transcription_failed"
        file_diag["error"] = str(exc)[:300]
        file_diag["transcribe_sec"] = round(time.time() - t0, 1)
        diag.add_file(file_diag)
        raise

    finally:
        if needs_split:
            cleanup_chunks(chunk_paths, file_path)


async def format_and_save(
    raw: dict, folder: str, raw_mode: bool = False, long_format: bool = False,
    session_type_hint: str = "auto",
) -> dict:
    """Phase 2: format transcript via Chat API (or raw) and save to disk."""
    filename = raw["filename"]
    segments = raw["segments"]
    duration = raw["duration"]
    idx = raw["file_index"]
    total = raw["total_files"]
    prefix = f"[{idx}/{total}]"
    file_diag: dict = raw.get("_diag", {"filename": filename})
    fmt_t0 = time.time()

    role_map: dict[str, str] = {}
    if raw_mode:
        final_text = build_raw_transcript(segments, duration, filename, long_format)
        segments, _, role_map = _apply_merge_and_roles(segments, session_type_hint)
        file_diag["format_mode"] = "raw"
    else:
        print(f"{prefix} Formatting {filename}...")
        final_text, segments, role_map = await format_transcript(
            segments, duration, filename, long_format, session_type_hint,
        )
        file_diag["format_mode"] = "llm"

    file_diag["format_sec"] = round(time.time() - fmt_t0, 1)
    file_diag["format_model"] = _sticky_model or CHAT_MODEL
    file_diag["roles"] = role_map

    final_text = sanitize_transcript(final_text)
    qa_warnings = validate_transcript(final_text, filename)
    file_diag["qa_warnings"] = qa_warnings

    base_name = os.path.splitext(filename)[0]
    out_name = f"{base_name}_transcript.txt"

    txt_dir = os.path.join(folder, "transcripts")
    json_dir = os.path.join(txt_dir, "json")
    os.makedirs(json_dir, exist_ok=True)

    out_path = os.path.join(txt_dir, out_name)
    with open(out_path, "wb") as f:
        f.write(BOM_UTF8)
        f.write(final_text.encode("utf-8"))

    inv_speaker_map: dict[str, str] = {}
    counter = 0
    for seg in segments:
        sp = seg.get("speaker") or "unknown"
        if sp not in inv_speaker_map:
            inv_speaker_map[sp] = f"Speaker {counter}"
            counter += 1

    json_out_path = os.path.join(json_dir, f"{base_name}.json")
    json_segments = []
    for seg in segments:
        raw_sp = seg.get("speaker") or "unknown"
        speaker_label = inv_speaker_map.get(raw_sp, raw_sp)
        role = role_map.get(speaker_label, speaker_label)
        json_segments.append({
            "start": seg.get("start", 0),
            "end": seg.get("end", 0),
            "speaker": role,
            "text": seg.get("text", "").strip(),
        })
    with open(json_out_path, "w", encoding="utf-8") as f:
        json.dump(json_segments, f, ensure_ascii=False, indent=2)

    file_diag["output_chars"] = len(final_text)
    file_diag["status"] = "ok" if not qa_warnings else "ok_with_warnings"
    diag.add_file(file_diag)

    if qa_warnings:
        print(f"{prefix} ⚠ QA warnings for {filename}:")
        for w in qa_warnings:
            print(f"      {w}")
        print(f"{prefix} ✅ Saved (with warnings): {out_path}")
        return {"filename": filename, "out_path": out_path, "ok": True, "warnings": qa_warnings}

    print(f"{prefix} ✅ Saved: {out_path}")
    return {"filename": filename, "out_path": out_path, "ok": True}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def discover_files(folder: str) -> list[str]:
    """Find audio and video files. Extract audio from videos automatically."""
    audio: list[str] = []
    video: list[str] = []

    for name in sorted(os.listdir(folder)):
        ext = os.path.splitext(name)[1].lower()
        full = os.path.join(folder, name)
        if not os.path.isfile(full):
            continue
        if ext in ALLOWED_EXTENSIONS:
            audio.append(full)
        elif ext in VIDEO_EXTENSIONS:
            base = os.path.splitext(full)[0]
            has_audio_pair = any(
                os.path.exists(base + ae) for ae in ALLOWED_EXTENSIONS
            )
            if not has_audio_pair:
                video.append(full)

    if video:
        print(f"Extracting audio from {len(video)} video file(s)...")
        for v in video:
            audio.append(extract_audio_from_video(v))

    return audio


def _transcript_exists(audio_path: str, folder: str) -> bool:
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    txt_name = f"{base_name}_transcript.txt"
    return (
        os.path.exists(os.path.join(folder, "transcripts", txt_name))
        or os.path.exists(os.path.join(folder, txt_name))
    )


async def main(
    folder: str, skip_existing: bool = False, raw_mode: bool = False,
    session_type_hint: str = "auto",
) -> None:
    task_id = os.path.basename(folder)
    all_files = discover_files(folder)

    if not all_files:
        print(f"❌ No audio or video files found in {folder}")
        sys.exit(1)

    diag.args = {
        "folder": folder,
        "task_id": task_id,
        "skip_existing": skip_existing,
        "raw_mode": raw_mode,
        "session_type_hint": session_type_hint,
        "total_files_found": len(all_files),
    }

    if skip_existing:
        skipped = [f for f in all_files if _transcript_exists(f, folder)]
        file_paths = [f for f in all_files if not _transcript_exists(f, folder)]
        if skipped:
            print(f"⏩ Skipping {len(skipped)} file(s) with existing transcripts:")
            for s in skipped:
                print(f"   {os.path.basename(s)}")
        if not file_paths:
            print("✅ All files already have transcripts. Nothing to do.")
            diag.summary = {"result": "nothing_to_do", "skipped": len(skipped)}
            diag.save(folder)
            return
    else:
        file_paths = all_files

    total = len(file_paths)
    durations = [get_audio_duration(f) for f in file_paths]
    long_format = any(d > 3600 for d in durations)

    t0 = time.monotonic()

    mode_label = "raw (no formatting)" if raw_mode else "pipeline (parallel)"
    print(f"\n{'='*50}")
    print(f"Transcribe — {task_id}")
    print(f"Folder: {folder}")
    print(f"Files to process: {total}" + (f" (skipped: {len(all_files) - total})" if skip_existing else ""))
    print(f"Mode: {mode_label}")
    print(f"{'='*50}\n")

    success = 0
    failed = 0
    warned = 0
    saved_paths: list[str] = []
    file_times: list[tuple[str, float]] = []
    format_task: asyncio.Task | None = None
    format_file_info: str = ""
    format_file_t0: float = 0.0

    async def _collect_format_result():
        """Await the background formatting task and record its result."""
        nonlocal success, failed, warned
        assert format_task is not None
        try:
            result = await format_task
            elapsed = time.monotonic() - format_file_t0
            if result["ok"]:
                saved_paths.append(result["out_path"])
                file_times.append((format_file_info, elapsed))
                if result.get("warnings"):
                    warned += 1
                success += 1
        except Exception as exc:
            print(f"  ❌ Formatting failed for {format_file_info}: {exc}")
            diag.add_file({
                "filename": format_file_info,
                "status": "format_failed",
                "error": str(exc)[:300],
            })
            failed += 1

    for i, fpath in enumerate(file_paths, 1):
        if format_task is not None and i > 1:
            await asyncio.sleep(INTER_CHUNK_DELAY)

        file_start = time.monotonic()

        try:
            raw = await transcribe_file(fpath, i, total)
        except Exception as exc:
            print(f"[{i}/{total}] ❌ Transcription failed: {os.path.basename(fpath)} — {exc}")
            failed += 1
            continue

        if format_task is not None:
            await _collect_format_result()

        format_file_t0 = file_start
        format_task = asyncio.create_task(
            format_and_save(raw, folder, raw_mode, long_format, session_type_hint)
        )
        format_file_info = raw["filename"]

    if format_task is not None:
        await _collect_format_result()

    total_elapsed = time.monotonic() - t0
    total_min = int(total_elapsed // 60)
    total_sec = int(total_elapsed % 60)

    print(f"\n{'='*50}")
    summary = f"Done. Success: {success}, Failed: {failed}"
    if warned:
        summary += f", Warnings: {warned}"
    print(summary)
    print(f"Total time: {total_min}m {total_sec}s")
    for fname, elapsed in file_times:
        m = int(elapsed // 60)
        s = int(elapsed % 60)
        print(f"  {fname}: {m}m {s}s")
    print(f"\nOutput:")
    for p in saved_paths:
        print(f"  {p}")
    print(f"{'='*50}")

    diag.summary = {
        "success": success,
        "failed": failed,
        "warnings": warned,
        "total_files": total,
        "total_time_sec": round(total_elapsed, 1),
    }
    diag.save(folder)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="UX Transcribe — audio transcription pipeline")
    parser.add_argument("folder", help="Path to the folder with audio files")
    parser.add_argument(
        "--skip-existing", action="store_true",
        help="Skip files that already have a *_transcript.txt",
    )
    parser.add_argument(
        "--raw", action="store_true",
        help="Save raw transcript without LLM formatting (~2x faster)",
    )
    parser.add_argument(
        "--type", choices=["ux-interview", "meeting", "presentation", "auto"],
        default="auto",
        help="Recording type: ux-interview, meeting, presentation, or auto-detect",
    )
    args = parser.parse_args()

    folder = os.path.abspath(args.folder)

    if not os.path.isdir(folder):
        print(f"❌ Folder not found: {folder}")
        sys.exit(1)

    asyncio.run(main(
        folder,
        skip_existing=args.skip_existing,
        raw_mode=args.raw,
        session_type_hint=args.type,
    ))
