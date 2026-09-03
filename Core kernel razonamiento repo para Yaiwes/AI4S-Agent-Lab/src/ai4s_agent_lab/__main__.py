"""Command-line entry point for the dependency-free demonstration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .toy_decay import run_demo


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run an auditable synthetic decay-calibration research loop."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/decay_demo"),
        help="directory for evidence.jsonl and best_model.json",
    )
    parser.add_argument("--iterations", type=int, default=6, help="bounded proposal budget")
    parser.add_argument("--run-id", help="optional stable identifier for this run")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = run_demo(args.output_dir, iterations=args.iterations, run_id=args.run_id)
    output = {
        "run_id": summary.run_id,
        "floor_score": summary.floor_score,
        "best_score": summary.best_result.score,
        "best_parameters": dict(summary.best_proposal.parameters),
        "promotions": sum(item.action == "promote" for item in summary.trials),
        "rollbacks": sum(item.action == "rollback" for item in summary.trials),
        "evidence": str(args.output_dir / "evidence.jsonl"),
        "artifact": str(args.output_dir / "best_model.json"),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
