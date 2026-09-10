#!/usr/bin/env bash
# install-transcript-coding.sh
# Locally vendors the external `transcript-coding` skill into the pipeline.
# Run by the agent on the first switch to `coding_mode: external`.
#
# Behavior:
#   - If `skills/transcript-coding/SKILL.md` already exists — does nothing (idempotent).
#   - Otherwise — looks for the upstream source in standard locations and copies it.
#   - If no upstream is found — prints instructions for the researcher.
#
# Usage:
#   bash shared/scripts/install-transcript-coding.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TARGET="$REPO_ROOT/skills/transcript-coding"

# If already installed — fine.
if [[ -f "$TARGET/SKILL.md" ]]; then
  echo "[ok] transcript-coding already vendored in $TARGET"
  exit 0
fi

# Candidate upstream locations
CANDIDATES=(
  "$HOME/.claude/skills/transcript-coding"
  "$HOME/Library/Application Support/Claude/skills/transcript-coding"
  "$REPO_ROOT/../transcript-coding"
)

SOURCE=""
for c in "${CANDIDATES[@]}"; do
  if [[ -f "$c/SKILL.md" ]]; then
    SOURCE="$c"
    break
  fi
done

if [[ -z "$SOURCE" ]]; then
  cat <<'EOF'
[fail] Could not find the upstream transcript-coding skill.

Install it one of these ways:
1. If you use a Cowork / Claude Code marketplace:
     install the `transcript-coding` skill via UI → plugins.
2. If you downloaded a .skill archive:
     unzip /path/to/transcript-coding.skill -d ~/.claude/skills/

Run this script again after installing.
EOF
  exit 1
fi

# If the folder exists as an empty "zombie" from a failed cp — remove and recreate.
if [[ -d "$TARGET" ]] && [[ -z "$(ls -A "$TARGET" 2>/dev/null)" ]]; then
  rmdir "$TARGET" 2>/dev/null || true
fi

mkdir -p "$TARGET"
# Copy with symlinks resolved and drop readonly
cp -RL "$SOURCE/." "$TARGET/"
chmod -R u+w "$TARGET"

echo "[ok] vendored transcript-coding from $SOURCE → $TARGET"
echo "[hint] 09-flat-coding in coding_mode: external can now call $TARGET/SKILL.md"
