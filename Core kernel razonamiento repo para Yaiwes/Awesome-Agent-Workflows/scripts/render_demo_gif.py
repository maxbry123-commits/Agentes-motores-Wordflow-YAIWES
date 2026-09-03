#!/usr/bin/env python3
"""Render the README demo GIF from simple synthetic SVG frames.

Requires macOS `sips` for SVG-to-PNG rasterization and `ffmpeg` for GIF
assembly. The GIF is intentionally synthetic: no real terminals, private repo
names, tokens, vendor UI, or user data are captured.
"""

from __future__ import annotations

import argparse
import html
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import TypedDict

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "assets" / "demo-workflow.gif"
WIDTH = 960
HEIGHT = 540
SANS = "Inter, -apple-system, BlinkMacSystemFont, 'SF Pro Text', Helvetica, Arial, sans-serif"
MONO = "'SF Mono', SFMono-Regular, ui-monospace, Menlo, Consolas, monospace"


class Panel(TypedDict):
    title: str
    lines: list[str]
    accent: str
    mono: bool


class Frame(TypedDict):
    step: str
    title: str
    subtitle: str
    left: Panel
    right: Panel
    footer: str


FRAMES: list[Frame] = [
    {
        "step": "1/4",
        "title": "Pick a workflow card",
        "subtitle": "Start with an operating procedure, not a blank prompt.",
        "left": {
            "title": "Fresh-Context Code Review",
            "lines": [
                "Agent claims a PR is ready.",
                "Treat the summary as untrusted.",
                "Check diff, tests, evidence, risks.",
            ],
            "accent": "#38BDF8",
            "mono": False,
        },
        "right": {
            "title": "Why this matters",
            "lines": [
                "Bound task before the run.",
                "Make success observable.",
                "Stop before risky side effects.",
            ],
            "accent": "#A78BFA",
            "mono": False,
        },
        "footer": "Choose the situation first. The workflow supplies the guardrails.",
    },
    {
        "step": "2/4",
        "title": "Copy the bounded brief",
        "subtitle": "Goal, scope, non-goals, verification, and stop conditions travel together.",
        "left": {
            "title": "Brief fields",
            "lines": [
                "Goal",
                "Allowed scope",
                "Forbidden actions",
                "Verification",
                "Report format",
            ],
            "accent": "#22C55E",
            "mono": False,
        },
        "right": {
            "title": "Agent input",
            "lines": [
                "Goal: review a small docs change",
                "Scope: diff, tests, linked docs",
                "Do not: deploy or change settings",
                "Verify: run exact checks",
                "Report: evidence and risks",
            ],
            "accent": "#38BDF8",
            "mono": True,
        },
        "footer": "Copying the brief is the handoff, not just a prompt.",
    },
    {
        "step": "3/4",
        "title": "Run the agent inside the contract",
        "subtitle": "The agent can work quickly without drifting into unrelated changes.",
        "left": {
            "title": "Allowed",
            "lines": [
                "Read targeted files",
                "Patch the agreed scope",
                "Run verification commands",
                "Collect evidence",
            ],
            "accent": "#22C55E",
            "mono": False,
        },
        "right": {
            "title": "Blocked",
            "lines": [
                "No secrets",
                "No repo settings",
                "No production actions",
                "No unrelated cleanup",
            ],
            "accent": "#F97316",
            "mono": False,
        },
        "footer": "A good workflow narrows the blast radius before work begins.",
    },
    {
        "step": "4/4",
        "title": "Verify before done",
        "subtitle": "Success means traceable evidence, not a confident agent summary.",
        "left": {
            "title": "Verification",
            "lines": [
                "$ python3 scripts/lint_repo.py",
                "repo hygiene check passed",
                "$ git diff --check",
                "clean",
            ],
            "accent": "#22C55E",
            "mono": True,
        },
        "right": {
            "title": "Final report",
            "lines": [
                "Summary: what changed",
                "Files: exact paths",
                "Commands: exit status",
                "Risks: remaining uncertainty",
            ],
            "accent": "#A78BFA",
            "mono": False,
        },
        "footer": "Evidence before claims. Review before merge. Ship with less guesswork.",
    },
]


def command_bin(name: str) -> str:
    binary = shutil.which(name)
    if not binary:
        raise SystemExit(f"{name} is required to render assets/demo-workflow.gif")
    return binary


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def rect(
    x: int,
    y: int,
    w: int,
    h: int,
    fill: str,
    *,
    stroke: str | None = None,
    sw: int = 0,
    rx: int = 0,
    opacity: float | None = None,
) -> str:
    attrs = [f'x="{x}"', f'y="{y}"', f'width="{w}"', f'height="{h}"', f'fill="{fill}"']
    if rx:
        attrs.append(f'rx="{rx}"')
    if stroke:
        attrs.append(f'stroke="{stroke}"')
        attrs.append(f'stroke-width="{sw}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    return f"<rect {' '.join(attrs)}/>"


def text(
    value: str,
    x: int,
    y: int,
    size: int,
    fill: str = "#F8FAFC",
    *,
    family: str = SANS,
    weight: int | str = 500,
) -> str:
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-family="{family}" '
        f'font-size="{size}" font-weight="{weight}">{esc(value)}</text>'
    )


def pill(label: str, x: int, y: int, fill: str, *, width: int = 116) -> list[str]:
    return [
        rect(x, y, width, 34, fill, rx=17),
        text(label, x + 18, y + 23, 17, "#ECFEFF", weight=800),
    ]


def panel(panel_data: Panel, x: int, y: int, w: int, h: int) -> list[str]:
    accent = panel_data["accent"]
    family = MONO if panel_data["mono"] else SANS
    body_size = 17 if panel_data["mono"] else 20
    line_gap = 33 if len(panel_data["lines"]) > 4 else 40
    pieces = [
        rect(x, y, w, h, "#0B1224", stroke=accent, sw=2, rx=22),
        rect(x, y, w, 50, "#162033", rx=22),
        rect(x, y + 28, w, 24, "#162033"),
        text(panel_data["title"], x + 24, y + 33, 24, "#F8FAFC", weight=800),
    ]
    line_y = y + 86
    for line in panel_data["lines"]:
        pieces.append(rect(x + 24, line_y - 17, 8, 8, accent, rx=4))
        pieces.append(text(line, x + 44, line_y, body_size, "#E2E8F0", family=family, weight=650))
        line_y += line_gap
    return pieces


def render_svg(frame: Frame) -> str:
    pieces: list[str] = [
        f'<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg" role="img">',
        "<title>Awesome Agent Workflows demo</title>",
        "<defs>",
        '<linearGradient id="bg" x1="0" y1="0" x2="960" y2="540" gradientUnits="userSpaceOnUse">',
        '<stop stop-color="#07111F"/><stop offset="0.52" stop-color="#101936"/><stop offset="1" stop-color="#1E123A"/>',
        "</linearGradient>",
        '<radialGradient id="glow" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(770 72) rotate(135) scale(360 230)">',
        '<stop stop-color="#38BDF8" stop-opacity="0.32"/><stop offset="1" stop-color="#38BDF8" stop-opacity="0"/>',
        "</radialGradient>",
        "</defs>",
        rect(0, 0, WIDTH, HEIGHT, "url(#bg)"),
        rect(0, 0, WIDTH, HEIGHT, "url(#glow)"),
        rect(30, 26, 900, 488, "#0F172A", rx=32, opacity=0.94),
        rect(30, 26, 900, 7, "#38BDF8", rx=4),
        text("Awesome Agent Workflows", 66, 68, 24, "#F8FAFC", weight=850),
        *pill(frame["step"], 784, 46, "#0EA5E9", width=92),
        text(frame["title"], 66, 129, 40, "#F8FAFC", weight=900),
        text(frame["subtitle"], 68, 166, 22, "#CBD5E1", weight=550),
        *panel(frame["left"], 66, 208, 400, 226),
        *panel(frame["right"], 494, 208, 400, 226),
        rect(66, 462, 828, 38, "#111827", stroke="#334155", sw=1, rx=19),
        text(frame["footer"], 90, 487, 20, "#F8FAFC", weight=750),
        "</svg>",
    ]
    return "\n".join(pieces)


def render_png(sips: str, frame: Frame, svg_path: Path, png_path: Path) -> None:
    svg_path.write_text(render_svg(frame))
    cmd = [sips, "-s", "format", "png", svg_path.as_posix(), "--out", png_path.as_posix()]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def concat_path(path: Path) -> str:
    """Escape a path for a single-quoted ffmpeg concat-demuxer line."""
    return path.as_posix().replace("\\", "\\\\").replace("'", "\\'")


def render_gif(ffmpeg: str, frame_paths: list[Path], output: Path) -> None:
    list_file = frame_paths[0].parent / "demo-workflow.concat.txt"
    durations = [1.25, 1.4, 1.25, 1.8]
    lines: list[str] = []
    for frame_path, duration in zip(frame_paths, durations, strict=True):
        lines.append(f"file '{concat_path(frame_path)}'")
        lines.append(f"duration {duration}")
    lines.append(f"file '{concat_path(frame_paths[-1])}'")
    list_file.write_text("\n".join(lines) + "\n")
    try:
        palette = (
            "fps=8,scale=720:-1:flags=lanczos,split[s0][s1];"
            "[s0]palettegen=max_colors=88[p];"
            "[s1][p]paletteuse=dither=bayer:bayer_scale=5"
        )
        cmd = [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            list_file.as_posix(),
            "-vf",
            palette,
            "-loop",
            "0",
            output.as_posix(),
        ]
        subprocess.run(cmd, check=True)
    finally:
        list_file.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="GIF output path. Defaults to assets/demo-workflow.gif.",
    )
    args = parser.parse_args()

    sips = command_bin("sips")
    ffmpeg = command_bin("ffmpeg")
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="agent-workflows-demo-") as tmp:
        tmpdir = Path(tmp)
        frame_paths: list[Path] = []
        for index, frame in enumerate(FRAMES):
            svg_path = tmpdir / f"frame-{index:02d}.svg"
            png_path = tmpdir / f"frame-{index:02d}.png"
            render_png(sips, frame, svg_path, png_path)
            frame_paths.append(png_path)
        render_gif(ffmpeg, frame_paths, output)

    display_path = output.relative_to(ROOT) if output.is_relative_to(ROOT) else output
    print(f"rendered {display_path}")


if __name__ == "__main__":
    main()
