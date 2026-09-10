#!/usr/bin/env bash
# fable5-methodology installer for Claude Code.
#   ./install.sh                 install at user level (~/.claude) — all projects
#   ./install.sh --project DIR   install into a single project's DIR/.claude
#   ./install.sh --dir DIR       install into an explicit Claude config dir (advanced/testing)
#   ./install.sh --check         verify an existing install, change nothing
#   ./install.sh --uninstall     reverse a previous install (uses the install manifest)
#
# Safe by design: backs up settings.json + CLAUDE.md before edits; the settings hook-merge is
# ADDITIVE and idempotent (never clobbers your existing hooks); name collisions are installed
# under a `fable5-` prefix, never overwriting your files; writes a manifest for clean uninstall.
# Requires: bash, python3, cp, awk. Optional (for the post-edit hook): ruff/eslint/rustfmt.
set -uo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
MODE="install"; SCOPE="user"; DIR=""
while [ $# -gt 0 ]; do
  case "$1" in
    --check) MODE="check";;
    --uninstall) MODE="uninstall";;
    --project) SCOPE="project"; DIR="${2:-}"; shift;;
    --dir) SCOPE="explicit"; DIR="${2:-}"; shift;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac; shift
done

# Resolve the Claude config dir we install into.
case "$SCOPE" in
  user)     CLAUDE_DIR="$HOME/.claude";;
  project)  [ -n "$DIR" ] || { echo "--project needs a directory" >&2; exit 2; }; CLAUDE_DIR="$DIR/.claude";;
  explicit) [ -n "$DIR" ] || { echo "--dir needs a directory" >&2; exit 2; }; CLAUDE_DIR="$DIR";;
esac
HOOKS_DIR="$CLAUDE_DIR/hooks"
SKILLS_DIR="$CLAUDE_DIR/skills"
AGENTS_DIR="$CLAUDE_DIR/agents"
HOME_DIR="$CLAUDE_DIR/fable5-methodology"          # reference copy + @import target
MANIFEST="$HOME_DIR/.install-manifest"
IMPORT_LINE="@$HOME_DIR/CLAUDE.md"

command -v python3 >/dev/null || { echo "python3 is required" >&2; exit 1; }

# Names that collide with Claude Code bundled skills / common agents → always prefixed.
COLLIDE_SKILLS="code-review security-review verification-loop"
COLLIDE_AGENTS="code-reviewer"

say() { printf '  %s\n' "$*"; }

# ---------------------------------------------------------------- CHECK
if [ "$MODE" = "check" ]; then
  echo "== fable5 install check: $CLAUDE_DIR =="
  ok=0; bad=0
  for s in task-planning integrity-guardrails predictive-execution problem-framing context-economy; do
    [ -f "$SKILLS_DIR/$s/SKILL.md" ] || [ -f "$SKILLS_DIR/fable5-$s/SKILL.md" ] && { say "skill ok: $s"; ok=$((ok+1)); } || { say "MISSING skill: $s"; bad=$((bad+1)); }
  done
  for a in builder qa-verifier research-scout; do
    [ -f "$AGENTS_DIR/$a.md" ] && { say "agent ok: $a"; ok=$((ok+1)); } || { say "MISSING agent: $a"; bad=$((bad+1)); }
  done
  for h in pre-tool-guard.py delivery-gate.sh evidence-log.sh post-edit-verify.sh pre-compact-handoff.sh session-loader.sh; do
    [ -x "$HOOKS_DIR/$h" ] && say "hook exec ok: $h" || { say "MISSING/!exec hook: $h"; bad=$((bad+1)); }
  done
  grep -qF "$IMPORT_LINE" "$CLAUDE_DIR/CLAUDE.md" 2>/dev/null && say "CLAUDE.md import ok" || { say "MISSING @import in CLAUDE.md"; bad=$((bad+1)); }
  python3 -c "import json;json.load(open('$CLAUDE_DIR/settings.json'))" 2>/dev/null && say "settings.json valid" || { say "settings.json missing/invalid"; bad=$((bad+1)); }
  echo "== check done: ok=$ok problems=$bad =="
  exit $([ "$bad" -eq 0 ] && echo 0 || echo 1)
fi

# ---------------------------------------------------------------- UNINSTALL
if [ "$MODE" = "uninstall" ]; then
  [ -f "$MANIFEST" ] || { echo "no manifest at $MANIFEST — nothing to uninstall (or installed elsewhere)"; exit 1; }
  echo "== uninstalling per $MANIFEST =="
  while IFS= read -r path; do
    [ -z "$path" ] && continue
    if [ -e "$path" ] || [ -L "$path" ]; then rm -rf "$path" && say "removed $path"; fi
  done < "$MANIFEST"
  # Remove @import line and de-register hooks from settings.json.
  python3 - "$CLAUDE_DIR" "$IMPORT_LINE" <<'PY'
import json, os, sys, re
cd, imp = sys.argv[1], sys.argv[2]
cm = os.path.join(cd, "CLAUDE.md")
if os.path.exists(cm):
    lines = open(cm).read().splitlines(keepends=True)
    lines = [l for l in lines if l.strip() != imp and "fable5-methodology enforcement layer" not in l]
    open(cm, "w").writelines(lines)
sp = os.path.join(cd, "settings.json")
if os.path.exists(sp):
    d = json.load(open(sp))
    for ev, blocks in list(d.get("hooks", {}).items()):
        d["hooks"][ev] = [b for b in blocks
                          if not any("fable5-methodology" in h.get("command","") or
                                     "/hooks/pre-tool-guard.py" in h.get("command","") or
                                     "/hooks/delivery-gate.sh" in h.get("command","") or
                                     "/hooks/evidence-log.sh" in h.get("command","") or
                                     "/hooks/post-edit-verify.sh" in h.get("command","") or
                                     "/hooks/pre-compact-handoff.sh" in h.get("command","") or
                                     "/hooks/session-loader.sh" in h.get("command","")
                                     for h in b.get("hooks", []))]
        if not d["hooks"][ev]: del d["hooks"][ev]
    json.dump(d, open(sp, "w"), indent=2); open(sp, "a").write("\n")
    print("  settings.json cleaned")
PY
  rm -rf "$HOME_DIR" 2>/dev/null && say "removed $HOME_DIR"
  echo "== uninstall done. Restart Claude Code. Your settings/CLAUDE.md backups are in $CLAUDE_DIR/backups =="
  exit 0
fi

# ---------------------------------------------------------------- INSTALL
echo "== installing fable5-methodology → $CLAUDE_DIR ($SCOPE scope) =="
mkdir -p "$CLAUDE_DIR" "$HOOKS_DIR" "$SKILLS_DIR" "$AGENTS_DIR" "$CLAUDE_DIR/backups"
: > "$MANIFEST.tmp"

ts="$(date +%Y%m%d-%H%M%S)"
[ -f "$CLAUDE_DIR/settings.json" ] && cp -p "$CLAUDE_DIR/settings.json" "$CLAUDE_DIR/backups/settings.json.$ts.bak"
[ -f "$CLAUDE_DIR/CLAUDE.md" ]     && cp -p "$CLAUDE_DIR/CLAUDE.md"     "$CLAUDE_DIR/backups/CLAUDE.md.$ts.bak"
say "backed up settings.json + CLAUDE.md (if present) → backups/*.$ts.bak"

# 1. Reference copy of the whole collection (import target + docs). Exclude VCS/caches.
rm -rf "$HOME_DIR"; mkdir -p "$HOME_DIR"
( cd "$REPO" && for item in *; do
    case "$item" in .git|.ruff_cache|__pycache__) continue;; esac
    cp -a "$item" "$HOME_DIR/"
  done )
find "$HOME_DIR" -name '.ruff_cache' -type d -prune -exec rm -rf {} + 2>/dev/null || true
say "reference copy → $HOME_DIR"

in_list() { case " $2 " in *" $1 "*) return 0;; *) return 1;; esac; }

# 2. Skills — prefix on known collision OR pre-existing dir; never clobber.
sc=0
for d in "$REPO"/skills/*/; do
  name="$(basename "$d")"
  dest="$name"
  if in_list "$name" "$COLLIDE_SKILLS" || { [ -e "$SKILLS_DIR/$name" ] && [ ! -f "$SKILLS_DIR/$name/.fable5" ]; }; then
    dest="fable5-$name"
  fi
  rm -rf "$SKILLS_DIR/$dest"; cp -a "$d" "$SKILLS_DIR/$dest"; touch "$SKILLS_DIR/$dest/.fable5"
  if [ "$dest" != "$name" ]; then
    python3 - "$SKILLS_DIR/$dest/SKILL.md" "$name" "$dest" <<'PY'
import sys; p,old,new=sys.argv[1:4]; s=open(p).read()
open(p,"w").write(s.replace(f"name: {old}\n", f"name: {new}\n", 1))
PY
  fi
  echo "$SKILLS_DIR/$dest" >> "$MANIFEST.tmp"; sc=$((sc+1))
done
say "installed $sc skills (collisions prefixed 'fable5-')"

# 3. Agents — same collision policy. Agents are single files, so provenance is a trailing
#    marker comment (not a sidecar file as with skills): prefix only on a known collision or a
#    FOREIGN same-named file; a file WE installed (carries the marker) is overwritten in place,
#    which keeps re-runs idempotent (no orphaned fable5-<name> duplicate).
ac=0
for a in "$REPO"/agents/*.md; do
  name="$(basename "$a" .md)"; dest="$name"
  if in_list "$name" "$COLLIDE_AGENTS"; then
    dest="fable5-$name"
  elif [ -e "$AGENTS_DIR/$name.md" ] && ! grep -q 'installed-by: fable5-methodology' "$AGENTS_DIR/$name.md" 2>/dev/null; then
    dest="fable5-$name"   # a foreign agent of that name exists — don't clobber it
  fi
  cp -a "$a" "$AGENTS_DIR/$dest.md"
  if [ "$dest" != "$name" ]; then
    python3 - "$AGENTS_DIR/$dest.md" "$name" "$dest" <<'PY'
import sys; p,old,new=sys.argv[1:4]; s=open(p).read()
open(p,"w").write(s.replace(f"name: {old}\n", f"name: {new}\n", 1))
PY
  fi
  printf '\n<!-- installed-by: fable5-methodology -->\n' >> "$AGENTS_DIR/$dest.md"
  echo "$AGENTS_DIR/$dest.md" >> "$MANIFEST.tmp"; ac=$((ac+1))
done
say "installed $ac agents"

# 4. Hooks — copy + make executable.
for h in "$REPO"/hooks/*.sh "$REPO"/hooks/*.py; do
  cp -a "$h" "$HOOKS_DIR/$(basename "$h")"; chmod +x "$HOOKS_DIR/$(basename "$h")"
  echo "$HOOKS_DIR/$(basename "$h")" >> "$MANIFEST.tmp"
done
say "installed 6 hooks (executable)"

# 5. Patch the reference-copy CLAUDE.md so its refs match the prefixed installs (deterministic).
python3 - "$HOME_DIR/CLAUDE.md" <<'PY'
import sys; p=sys.argv[1]; s=open(p).read()
for a,b in [("builder → qa-verifier → code-reviewer","builder → qa-verifier → fable5-code-reviewer"),
            ("- **code-reviewer** — adversarial cold review.","- **fable5-code-reviewer** — adversarial cold review."),
            ("**qa-verifier** · **code-reviewer** · **research-scout**","**qa-verifier** · **fable5-code-reviewer** · **research-scout**"),
            ("**security-review** · **code-review**","**fable5-security-review** · **fable5-code-review**"),
            ("**verification-loop**","**fable5-verification-loop**")]:
    s=s.replace(a,b)
open(p,"w").write(s)
PY

# 6. Merge hook registrations into settings.json — ADDITIVE + idempotent, absolute paths for
#    user scope / ${CLAUDE_PROJECT_DIR} for project scope.
python3 - "$CLAUDE_DIR/settings.json" "$HOOKS_DIR" "$SCOPE" <<'PY'
import json, os, sys
sp, hooks_dir, scope = sys.argv[1], sys.argv[2], sys.argv[3]
base = "${CLAUDE_PROJECT_DIR}/.claude/hooks" if scope == "project" else hooks_dir
d = json.load(open(sp)) if os.path.exists(sp) else {}
H = d.setdefault("hooks", {})
adds = [("PreToolUse","Bash",f"python3 {base}/pre-tool-guard.py"),
        ("PostToolUse","Edit|Write|MultiEdit",f"bash {base}/post-edit-verify.sh"),
        ("PostToolUse","*",f"bash {base}/evidence-log.sh"),
        ("Stop",None,f"bash {base}/delivery-gate.sh"),
        ("PreCompact",None,f"bash {base}/pre-compact-handoff.sh"),
        ("SessionStart",None,f"bash {base}/session-loader.sh")]
def present(ev,cmd): return any(h.get("command")==cmd for b in H.get(ev,[]) for h in b.get("hooks",[]))
added=0
for ev,matcher,cmd in adds:
    if present(ev,cmd): continue
    blk={} if matcher is None else {"matcher":matcher}
    blk["hooks"]=[{"type":"command","command":cmd}]
    H.setdefault(ev,[]).append(blk); added+=1
json.dump(d, open(sp,"w"), indent=2); open(sp,"a").write("\n")
json.load(open(sp))  # validate
print(f"  settings.json: {added} hook(s) registered (base={base})")
PY

# 7. @import into CLAUDE.md (idempotent).
if ! grep -qF "$IMPORT_LINE" "$CLAUDE_DIR/CLAUDE.md" 2>/dev/null; then
  { printf '\n<!-- fable5-methodology enforcement layer — remove the line below to deactivate -->\n%s\n' "$IMPORT_LINE"; } >> "$CLAUDE_DIR/CLAUDE.md"
  say "added @import to CLAUDE.md"
else
  say "@import already present"
fi

mv "$MANIFEST.tmp" "$MANIFEST"
echo "== install complete. RESTART Claude Code so hooks + new skills load. Then: ./install.sh --check =="
