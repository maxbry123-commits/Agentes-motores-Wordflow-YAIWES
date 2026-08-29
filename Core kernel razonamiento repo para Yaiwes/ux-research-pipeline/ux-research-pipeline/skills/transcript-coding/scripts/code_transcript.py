#!/usr/bin/env python3
"""transcript-coding CLI.

Subcommands:
  run <transcript.json> <brief.json> --respondent-id <id>
      Full pipeline: segment → global → code → validate on one interview.
  segment <transcript.json>
      Only stage 7.1.
  global <transcript.json> <brief.json>
      Only stage 7.2 (requires brief).
  code <transcript.json> <brief.json> --respondent-id <id>
      Only stage 7.3 (requires segments.json and global_context.json checkpoints).
  validate <coded.json> <transcript.json> <brief.json>
      Only stage 7.9 validation.
  unify <project_dir>
      Propose codebook unification across all coded interviews in the folder.
  run-batch <folder>
      Run full pipeline on every interview in the folder's 2-interviews/json/ subdir.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Optional

# Make scripts/ importable when run as a file
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import yaml
from dotenv import load_dotenv

from backends import make_backend
from pipeline import (
    build_global_context,
    code_segments,
    propose_unification,
    segment_transcript,
    validate_coded_transcript,
)
from pipeline.global_pass import load_global_context, save_global_context
from pipeline.segmentation import load_segments, save_segments
from pipeline.unification import (
    load_codebook,
    save_codebook,
    write_unification_proposal_csv,
)
from prompt_loader import PromptLoader
from schemas import (
    Brief,
    CodedTranscript,
    RawTranscript,
    TranscriptUtterance,
)


SKILL_ROOT = SCRIPT_DIR.parent
DEFAULT_CONFIG_PATH = SKILL_ROOT / "config.default.yaml"
REFERENCES_DIR = SKILL_ROOT / "references"


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def load_config(override_path: Optional[Path] = None) -> dict[str, Any]:
    """Load default config, then merge override if present."""
    config = yaml.safe_load(DEFAULT_CONFIG_PATH.read_text(encoding="utf-8"))
    if override_path and override_path.exists():
        override = yaml.safe_load(override_path.read_text(encoding="utf-8")) or {}
        _deep_merge(config, override)
    elif override_path is None:
        # Look for transcript-coding.yaml in CWD
        cwd_config = Path.cwd() / "transcript-coding.yaml"
        if cwd_config.exists():
            override = yaml.safe_load(cwd_config.read_text(encoding="utf-8")) or {}
            _deep_merge(config, override)
    return config


def _deep_merge(base: dict, override: dict) -> None:
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v


def load_raw_transcript(path: Path, interview_id: Optional[str] = None) -> RawTranscript:
    """Load a raw transcript from ux-transcribe JSON (list of utterances)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected a JSON array of utterances, got {type(data).__name__}")
    utterances = [TranscriptUtterance(**u) for u in data]
    iid = interview_id or path.stem
    return RawTranscript(interview_id=iid, utterances=utterances)


def load_brief(path: Path) -> Brief:
    return Brief(**json.loads(path.read_text(encoding="utf-8")))


def coding_dir_for(transcript_path: Path, config: dict[str, Any]) -> Path:
    subdir = config.get("paths", {}).get("coding_subdir", "coding")
    return transcript_path.parent / subdir / transcript_path.stem


def codebook_path_for(brief_path: Path, config: dict[str, Any]) -> Path:
    filename = config.get("paths", {}).get("codebook_filename", "project_codebook.json")
    return brief_path.parent / filename


# ---- Subcommand: segment ----

def cmd_segment(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    setup_logging(config["logging"]["level"])
    transcript = load_raw_transcript(Path(args.transcript))

    cfg = config["stages"]["segmentation"]
    seg_cfg = config["segmentation"]
    loader = PromptLoader(REFERENCES_DIR)
    prompt = loader.load("prompt_segmentation")
    backend = make_backend(cfg["backend"])

    segments = segment_transcript(
        transcript,
        backend=backend,
        model=cfg["model"],
        prompt_system=prompt.sections["System"],
        prompt_user=prompt.sections["User"],
        reasoning_effort=cfg.get("reasoning_effort", "low"),
        max_tokens=cfg.get("max_completion_tokens", 4000),
        target_duration=seg_cfg["target_duration_seconds"],
        max_duration=seg_cfg["max_duration_seconds"],
        min_duration=seg_cfg["min_duration_seconds"],
    )

    out_dir = coding_dir_for(Path(args.transcript), config)
    out = out_dir / "segments.json"
    save_segments(segments, out)
    print(f"Wrote {len(segments)} segments to {out}")
    return 0


# ---- Subcommand: global ----

def cmd_global(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    setup_logging(config["logging"]["level"])
    transcript = load_raw_transcript(Path(args.transcript))
    brief = load_brief(Path(args.brief))

    cfg = config["stages"]["global_pass"]
    loader = PromptLoader(REFERENCES_DIR)
    prompt = loader.load("prompt_global_pass")
    backend = make_backend(cfg["backend"])

    ctx = build_global_context(
        transcript, brief,
        backend=backend,
        model=cfg["model"],
        prompt_system=prompt.sections["System"],
        prompt_user=prompt.sections["User"],
        reasoning_effort=cfg.get("reasoning_effort", "medium"),
        max_tokens=cfg.get("max_completion_tokens", 3000),
    )
    out_dir = coding_dir_for(Path(args.transcript), config)
    out = out_dir / "global_context.json"
    save_global_context(ctx, out)
    print(f"Wrote global context to {out}")
    return 0


# ---- Subcommand: code ----

def cmd_code(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    setup_logging(config["logging"]["level"])
    transcript = load_raw_transcript(Path(args.transcript))
    brief = load_brief(Path(args.brief))
    respondent = brief.respondent_by_id(args.respondent_id)
    if respondent is None:
        print(f"ERROR: respondent_id {args.respondent_id!r} not found in brief", file=sys.stderr)
        return 2

    out_dir = coding_dir_for(Path(args.transcript), config)
    segments_path = out_dir / "segments.json"
    global_path = out_dir / "global_context.json"
    if not segments_path.exists() or not global_path.exists():
        print(f"ERROR: run `segment` and `global` first. Missing: {segments_path}, {global_path}",
              file=sys.stderr)
        return 2

    segments = load_segments(segments_path)
    global_ctx = load_global_context(global_path)

    codebook_path = codebook_path_for(Path(args.brief), config)
    codebook = load_codebook(codebook_path, brief.project_id)

    cfg = config["stages"]["local_coding"]
    lc_cfg = config["local_coding"]
    vision_cfg = config["vision"]
    val_cfg = config["validation"]

    loader = PromptLoader(REFERENCES_DIR)
    prompt = loader.load("prompt_local_coding")
    frames = loader.load_frames(lc_cfg["interpretive_preset"])
    backend = make_backend(cfg["backend"])

    checkpoint_path = None if args.fresh else (out_dir / "coded.checkpoint.json")
    if args.fresh and checkpoint_path and checkpoint_path.exists():
        checkpoint_path.unlink()

    coded_segments = code_segments(
        transcript, segments, global_ctx, brief, respondent, codebook,
        backend=backend,
        model=cfg["model"],
        prompt_system_template=prompt.sections["System"],
        prompt_user_template=prompt.sections["User"],
        interpretive_frames=frames,
        prompt_version=prompt.version,
        reasoning_effort=cfg.get("reasoning_effort", "medium"),
        max_tokens=cfg.get("max_completion_tokens", 4000),
        context_window_size=lc_cfg["context_window_size"],
        max_retries=lc_cfg["max_retries"],
        vision_mode=vision_cfg["mode"],
        trigger_words=vision_cfg.get("trigger_words", []),
        citation_match_mode=val_cfg["citation_match_mode"],
        fuzzy_threshold=val_cfg["fuzzy_threshold"],
        on_citation_mismatch=val_cfg["on_citation_mismatch"],
        checkpoint_path=out_dir / "coded.checkpoint.json",
    )

    # Assemble final CodedTranscript
    coded_transcript = CodedTranscript(
        interview_id=transcript.interview_id,
        project_id=brief.project_id,
        global_context=global_ctx,
        segments=coded_segments,
        prompt_versions={
            "segmentation": loader.load("prompt_segmentation").version,
            "global_pass": loader.load("prompt_global_pass").version,
            "local_coding": prompt.version,
            "interpretive_frames_preset": lc_cfg["interpretive_preset"],
        },
    )
    out = out_dir.parent / f"{Path(args.transcript).stem}.coded.json"
    out.write_text(
        json.dumps(coded_transcript.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8",
    )
    print(f"Wrote coded transcript to {out}")
    return 0


# ---- Subcommand: validate ----

def cmd_validate(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    setup_logging(config["logging"]["level"])
    coded = CodedTranscript(**json.loads(Path(args.coded).read_text(encoding="utf-8")))
    transcript = load_raw_transcript(Path(args.transcript), interview_id=coded.interview_id)
    brief = load_brief(Path(args.brief))
    val_cfg = config["validation"]

    report = validate_coded_transcript(
        coded, transcript, brief,
        citation_match_mode=val_cfg["citation_match_mode"],
        fuzzy_threshold=val_cfg["fuzzy_threshold"],
    )
    out = Path(args.coded).parent / (Path(args.coded).stem + ".validation.md")
    out.write_text(report.to_markdown(), encoding="utf-8")
    print(report.to_markdown())
    print(f"\nWrote report to {out}")
    return 0 if not report.errors else 1


# ---- Subcommand: unify ----

def cmd_unify(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    setup_logging(config["logging"]["level"])
    project_dir = Path(args.project_dir)

    # Find all *.coded.json files in project_dir
    coded_files = list(project_dir.rglob("*.coded.json"))
    if not coded_files:
        print(f"No *.coded.json files found under {project_dir}", file=sys.stderr)
        return 2

    coded_interviews = [
        CodedTranscript(**json.loads(p.read_text(encoding="utf-8"))) for p in coded_files
    ]
    project_id = coded_interviews[0].project_id

    codebook_path = project_dir / config["paths"]["codebook_filename"]
    codebook = load_codebook(codebook_path, project_id)

    cfg = config["stages"]["unification"]
    loader = PromptLoader(REFERENCES_DIR)
    prompt = loader.load("prompt_unification")
    backend = make_backend(cfg["backend"])

    proposal = propose_unification(
        coded_interviews, codebook,
        backend=backend,
        model=cfg["model"],
        prompt_system=prompt.sections["System"],
        prompt_user=prompt.sections["User"],
        reasoning_effort=cfg.get("reasoning_effort", "low"),
        max_tokens=cfg.get("max_completion_tokens", 4000),
    )

    proposal_json_path = project_dir / "unification_proposal.json"
    proposal_json_path.write_text(
        json.dumps(proposal, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    proposal_csv_path = project_dir / "unification_proposal.csv"
    write_unification_proposal_csv(proposal, proposal_csv_path)

    print(f"Wrote unification proposal to:")
    print(f"  {proposal_csv_path}  (review, set 'approved'=Y for merges you accept)")
    print(f"  {proposal_json_path}  (full JSON with rationale)")
    print()
    print(f"After reviewing, run:")
    print(f"  python3 {Path(__file__).name} apply-unification {project_dir}")
    return 0


# ---- Subcommand: run (full pipeline) ----

def cmd_run(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    setup_logging(config["logging"]["level"])
    # Run the three stages in sequence.
    for sub in ("segment", "global", "code"):
        sub_args = argparse.Namespace(
            transcript=args.transcript,
            brief=args.brief,
            respondent_id=args.respondent_id,
            fresh=args.fresh,
            config=args.config,
        )
        if sub == "segment":
            rc = cmd_segment(sub_args)
        elif sub == "global":
            rc = cmd_global(sub_args)
        else:
            rc = cmd_code(sub_args)
        if rc != 0:
            return rc

    # Run validation on the final coded output.
    coded_path = Path(args.transcript).parent / (Path(args.transcript).stem + ".coded.json")
    val_args = argparse.Namespace(
        coded=str(coded_path),
        transcript=args.transcript,
        brief=args.brief,
        config=args.config,
    )
    return cmd_validate(val_args)


# ---- Subcommand: run-batch ----

def cmd_run_batch(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    setup_logging(config["logging"]["level"])
    folder = Path(args.folder)
    brief_path = folder / "brief.json"
    if not brief_path.exists():
        print(f"ERROR: {brief_path} not found", file=sys.stderr)
        return 2
    brief = load_brief(brief_path)

    # Find transcripts
    transcripts_dir = folder / "2-interviews" / "json"
    if not transcripts_dir.exists():
        transcripts_dir = folder / "2-interviews"
    transcript_files = sorted(transcripts_dir.glob("*.json"))
    transcript_files = [t for t in transcript_files if not t.name.endswith(".coded.json")]
    if not transcript_files:
        print(f"ERROR: no transcripts found in {transcripts_dir}", file=sys.stderr)
        return 2

    # Need a mapping of transcript filename → respondent_id
    mapping_path = folder / "respondents_map.json"
    if not mapping_path.exists():
        print(f"ERROR: {mapping_path} required for batch mode. "
              f"Format: {{'interview_filename.json': 'r_1', ...}}", file=sys.stderr)
        return 2
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))

    overall_rc = 0
    for tpath in transcript_files:
        resp_id = mapping.get(tpath.name)
        if not resp_id:
            logging.warning("No respondent mapping for %s — skipping", tpath.name)
            continue
        print(f"\n=== Processing {tpath.name} (respondent {resp_id}) ===")
        run_args = argparse.Namespace(
            transcript=str(tpath),
            brief=str(brief_path),
            respondent_id=resp_id,
            fresh=args.fresh,
            config=args.config,
        )
        rc = cmd_run(run_args)
        if rc != 0:
            overall_rc = rc
            logging.error("Failed on %s with rc=%d", tpath.name, rc)

    return overall_rc


# ---- Main ----

def main() -> int:
    load_dotenv(Path.cwd() / ".env")  # picks up OPENAI_API_KEY etc. from current folder

    parser = argparse.ArgumentParser(description="transcript-coding CLI")
    parser.add_argument("--config", type=Path, default=None, help="Path to config override")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("run", help="Full pipeline on one interview")
    p.add_argument("transcript")
    p.add_argument("brief")
    p.add_argument("--respondent-id", required=True)
    p.add_argument("--fresh", action="store_true", help="Ignore any existing checkpoints")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("segment", help="Stage 7.1 only")
    p.add_argument("transcript")
    p.set_defaults(func=cmd_segment)

    p = sub.add_parser("global", help="Stage 7.2 only")
    p.add_argument("transcript")
    p.add_argument("brief")
    p.set_defaults(func=cmd_global)

    p = sub.add_parser("code", help="Stage 7.3 only (requires segment + global checkpoints)")
    p.add_argument("transcript")
    p.add_argument("brief")
    p.add_argument("--respondent-id", required=True)
    p.add_argument("--fresh", action="store_true")
    p.set_defaults(func=cmd_code)

    p = sub.add_parser("validate", help="Stage 7.9 validation")
    p.add_argument("coded")
    p.add_argument("transcript")
    p.add_argument("brief")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("unify", help="Propose codebook unification across project")
    p.add_argument("project_dir")
    p.set_defaults(func=cmd_unify)

    p = sub.add_parser("run-batch", help="Full pipeline on every interview in a folder")
    p.add_argument("folder")
    p.add_argument("--fresh", action="store_true")
    p.set_defaults(func=cmd_run_batch)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
