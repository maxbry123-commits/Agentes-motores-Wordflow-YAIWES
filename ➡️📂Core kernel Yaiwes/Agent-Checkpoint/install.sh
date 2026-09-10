#!/bin/bash
#
# Agent Checkpoint - One-Click Install
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/YOUR_REPO/agent-checkpoint/main/install.sh | bash
#   OR
#   ./install.sh
#   OR
#   ./install.sh --with-claude    # Also creates CLAUDE.md
#   ./install.sh --with-cursor    # Also creates .cursorrules
#   ./install.sh --all            # Creates both

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Agent Checkpoint - Control Plane for AI Coding Agents${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}Installing to: $(pwd)${NC}"
echo ""

# Check if files already exist
if [ -f "TASKS.md" ] || [ -f "verify.py" ]; then
    echo -e "${YELLOW}Warning: Some files already exist in this folder.${NC}"
    read -p "Overwrite? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Parse arguments
WITH_CLAUDE=false
WITH_CURSOR=false
for arg in "$@"; do
    case $arg in
        --with-claude) WITH_CLAUDE=true ;;
        --with-cursor) WITH_CURSOR=true ;;
        --all) WITH_CLAUDE=true; WITH_CURSOR=true ;;
    esac
done

# Create TASKS.md
echo -e "${GREEN}Creating TASKS.md...${NC}"
cat > TASKS.md << 'EOF'
# Project Tasks

## Status Legend
| Marker | Meaning |
|--------|---------|
| `[ ]`  | Pending |
| `[~]`  | In Progress |
| `[x]`  | Complete (verified) |
| `[?]`  | Needs Review |
| `[!]`  | Blocked |

## Verification Levels
| Level | Description |
|-------|-------------|
| `none` | Just mark complete |
| `auto` | File exists + not-stub |
| `tests` | Auto + run tests |
| `human` | Auto + human review |

---

## Your Tasks

<!-- Add tasks below. Example:

- [ ] 1.1 Create user model `src/models/user.py:User`
  - verify: auto

- [ ] 1.2 Add validation `src/models/user.py:validate`
  - verify: tests
  - tests: tests/test_user.py

- [ ] 1.3 Create API endpoint `src/routes/users.py`
  - verify: human
  - depends: 1.1, 1.2
-->
EOF

# Create AGENT_LOG.md
echo -e "${GREEN}Creating AGENT_LOG.md...${NC}"
cat > AGENT_LOG.md << 'EOF'
# Agent Execution Log

> **APPEND-ONLY**: Never edit past entries.

---

<!-- Agents append entries below this line -->
EOF

# Create verify.py
echo -e "${GREEN}Creating verify.py...${NC}"
cat > verify.py << 'PYTHON_EOF'
#!/usr/bin/env python3
"""Agent Checkpoint Verification - Catches stub/mock code"""
import re, sys, subprocess, argparse
from pathlib import Path
from datetime import datetime

STUB_PATTERNS = [
    r'\bTODO\b', r'\bFIXME\b', r'\bXXX\b', r'NotImplementedError',
    r'raise\s+NotImplementedError', r'throw\s+new\s+Error\s*\(\s*["\']Not\s+implemented',
    r'pass\s*#', r'pass\s*$', r'\.\.\.(?:\s*#.*)?$', r'//\s*stub', r'//\s*todo',
    r'/\*\s*mock\s*\*/', r'#\s*placeholder', r'#\s*stub',
]

def parse_tasks():
    if not Path("TASKS.md").exists(): return {}
    content = Path("TASKS.md").read_text()
    tasks = {}
    for m in re.finditer(r'^-\s*\[([~x?! ])\]\s*(\d+(?:\.\d+)?)\s+(.+?)(?:\s*`([^`]+)`)?$', content, re.M):
        status, tid, desc, fref = m.groups()
        block = content[m.end():re.search(r'^-\s*\[', content[m.end():], re.M).start()+m.end() if re.search(r'^-\s*\[', content[m.end():], re.M) else len(content)]
        meta = dict(re.findall(r'^\s+-\s*(verify|tests|depends):\s*(.+)$', block, re.M))
        tasks[tid] = {'status': status, 'desc': desc, 'file': fref, 'verify': meta.get('verify', 'auto'), 'tests': meta.get('tests')}
    return tasks

def parse_log():
    if not Path("AGENT_LOG.md").exists(): return []
    content = Path("AGENT_LOG.md").read_text()
    entries = []
    for m in re.finditer(r'^---\s*\n##\s*(\S+)\s*\|\s*(\S+)\s*\|\s*Task\s+(\S+)', content, re.M):
        ts, agent, tid = m.groups()
        block = content[m.end():re.search(r'^---', content[m.end():], re.M).start()+m.end() if re.search(r'^---', content[m.end():], re.M) else len(content)]
        status = re.search(r'\*\*Status\*\*:\s*(\w+)', block)
        files = re.findall(r'-\s*(\S+:\d+(?:-\d+)?)', block)
        entries.append({'ts': ts, 'agent': agent, 'tid': tid, 'status': status.group(1) if status else None, 'files': files})
    return entries

def parse_ref(ref):
    if ':' not in ref: return ref, None, None
    path, loc = ref.rsplit(':', 1)
    if m := re.match(r'(\d+)-(\d+)', loc): return path, int(m[1]), int(m[2])
    if m := re.match(r'(\d+)', loc): return path, int(m[1]), int(m[1])
    return path, None, None

def check_file(path):
    exists = Path(path).exists()
    return exists, f"file-exists: {'PASS' if exists else 'FAIL'} - {path}"

def check_stub(path, start, end):
    if not Path(path).exists(): return False, f"not-stub: FAIL - file not found"
    lines = Path(path).read_text().splitlines()
    if start < 1 or end > len(lines): return False, f"not-stub: FAIL - lines out of range"
    code = '\n'.join(lines[start-1:end])
    for p in STUB_PATTERNS:
        if re.search(p, code, re.I|re.M): return False, f"not-stub: FAIL - stub pattern '{p}'"
    meaningful = [l for l in lines[start-1:end] if l.strip() and not re.match(r'^\s*(#|//|/\*|\*)', l)]
    if len(meaningful) < 3: return False, f"not-stub: FAIL - only {len(meaningful)} lines"
    return True, f"not-stub: PASS - {len(meaningful)} meaningful lines"

def check_tests(test_file):
    if not Path(test_file).exists(): return False, f"tests: FAIL - {test_file} not found"
    ext = Path(test_file).suffix
    cmd = ['python', '-m', 'pytest', test_file, '-v'] if ext == '.py' else ['npx', 'jest', test_file]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return r.returncode == 0, f"tests: {'PASS' if r.returncode == 0 else 'FAIL'}"
    except: return False, "tests: FAIL - runner error"

def verify(tid):
    tasks, log = parse_tasks(), parse_log()
    if tid not in tasks: return False, [f"Task {tid} not found"]
    t = tasks[tid]
    results, passed = [], True
    claims = [e for e in log if e['tid'] == tid and e['status'] == 'CLAIM']
    refs = [f for c in claims for f in c['files']] if claims else ([t['file']] if t['file'] else [])
    if not refs: return False, ["No claims found in AGENT_LOG.md"]
    for ref in refs:
        path, s, e = parse_ref(ref)
        ok, msg = check_file(path); results.append(msg); passed &= ok
        if s and e and t['verify'] in ['auto','tests','human']:
            ok, msg = check_stub(path, s, e); results.append(msg); passed &= ok
    if t['verify'] in ['tests','human'] and t.get('tests'):
        ok, msg = check_tests(t['tests']); results.append(msg); passed &= ok
    return passed, results

def log_result(tid, passed, results):
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = f"\n---\n## {ts} | verify.py | Task {tid}\n\n**Status**: {'VERIFIED' if passed else 'FAILED'}\n"
    for r in results: entry += f"- {r}\n"
    with open("AGENT_LOG.md", "a") as f: f.write(entry)

def main():
    p = argparse.ArgumentParser(description="Agent Checkpoint Verification")
    p.add_argument('task_id', nargs='?', help='Task ID (e.g., 1.1)')
    p.add_argument('--all', action='store_true', help='Verify all in-progress')
    p.add_argument('--check', help='Quick check file:line')
    p.add_argument('--no-log', action='store_true')
    args = p.parse_args()

    if args.check:
        path, s, e = parse_ref(args.check)
        ok1, m1 = check_file(path); print(f"  {'[PASS]' if ok1 else '[FAIL]'} {m1}")
        if s and e: ok2, m2 = check_stub(path, s, e); print(f"  {'[PASS]' if ok2 else '[FAIL]'} {m2}")
        sys.exit(0 if ok1 and (not s or ok2) else 1)

    if args.all:
        tasks = parse_tasks()
        in_prog = [t for t,v in tasks.items() if v['status'] == '~']
        if not in_prog: print("No in-progress tasks."); sys.exit(0)
        all_ok = True
        for tid in in_prog:
            ok, res = verify(tid)
            print(f"\n{'='*50}\nTask {tid}: {'PASS' if ok else 'FAIL'}\n{'='*50}")
            for r in res: print(f"  {r}")
            if not args.no_log: log_result(tid, ok, res)
            all_ok &= ok
        sys.exit(0 if all_ok else 1)

    if args.task_id:
        ok, res = verify(args.task_id)
        print(f"\n{'='*50}\nTask {args.task_id}: {'PASS' if ok else 'FAIL'}\n{'='*50}")
        for r in res: print(f"  {r}")
        if not args.no_log: log_result(args.task_id, ok, res)
        sys.exit(0 if ok else 1)

    p.print_help()

if __name__ == '__main__': main()
PYTHON_EOF
chmod +x verify.py

# Create .agent-rules.md (compact version)
echo -e "${GREEN}Creating .agent-rules.md...${NC}"
cat > .agent-rules.md << 'EOF'
# Agent Checkpoint Rules

## Quick Reference

1. **Read TASKS.md** before starting any work
2. **Mark [~]** when starting a task
3. **Log to AGENT_LOG.md** for every action (STARTED, CLAIM, COMPLETED)
4. **Include file:line** references in claims (e.g., `src/auth.ts:15-45`)
5. **Run verification** before completing: `python verify.py <task-id>`
6. **Only mark [x]** after verification PASS
7. **Never edit** past log entries (append-only)

## Log Entry Format

```markdown
---
## 2025-01-25T10:30:00Z | agent-name | Task 1.1

**Status**: STARTED | CLAIM | VERIFIED | COMPLETED | FAILED
**Files**: (for CLAIM)
- src/file.py:10-50 (description)
```

## Copy to Agent Config

Add this to CLAUDE.md, .cursorrules, or agent context:

```
ALWAYS read TASKS.md before starting work.
When working: mark [~] → log STARTED → implement → log CLAIM with file:line → run verify.py → mark [x] on PASS
```
EOF

# Optionally create CLAUDE.md
if [ "$WITH_CLAUDE" = true ]; then
    echo -e "${GREEN}Creating CLAUDE.md...${NC}"
    cat > CLAUDE.md << 'EOF'
# Claude Code Instructions

## Task Management (Agent Checkpoint)

ALWAYS read TASKS.md before starting any work.

When working on tasks:
1. Read TASKS.md to find next pending task `[ ]`
2. Change `[ ]` to `[~]` when starting
3. Append STARTED entry to AGENT_LOG.md
4. Implement the task
5. Append CLAIM entry with file:line references
6. Run: `python verify.py <task-id>`
7. If PASS: mark `[x]`, log COMPLETED
8. If FAIL: keep `[~]`, log FAILED, fix issues
9. If verify:human: mark `[?]`, log AWAITING_REVIEW

## Log Format

```markdown
---
## YYYY-MM-DDTHH:MM:SSZ | claude-code | Task X.Y

**Status**: STARTED
**Task**: Description here

---
## YYYY-MM-DDTHH:MM:SSZ | claude-code | Task X.Y

**Status**: CLAIM
**Files**:
- src/file.py:10-50 (added function X)
```
EOF
fi

# Optionally create .cursorrules
if [ "$WITH_CURSOR" = true ]; then
    echo -e "${GREEN}Creating .cursorrules...${NC}"
    cat > .cursorrules << 'EOF'
# Cursor Rules - Agent Checkpoint

ALWAYS read TASKS.md before starting any work.

When working on tasks:
1. Read TASKS.md to find next pending task [ ]
2. Change [ ] to [~] when starting
3. Append STARTED entry to AGENT_LOG.md
4. Implement the task
5. Append CLAIM entry with file:line references
6. Run: python verify.py <task-id>
7. If PASS: mark [x], log COMPLETED
8. If FAIL: keep [~], log FAILED, fix issues

Log format:
---
## YYYY-MM-DDTHH:MM:SSZ | cursor | Task X.Y
**Status**: STARTED | CLAIM | COMPLETED
**Files**: (for claims)
- src/file.py:10-50 (description)
EOF
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Done! Agent Checkpoint installed.${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Files created:"
echo "  - TASKS.md        (define your tasks here)"
echo "  - AGENT_LOG.md    (agents log here)"
echo "  - verify.py       (run to verify claims)"
echo "  - .agent-rules.md (conventions for agents)"
[ "$WITH_CLAUDE" = true ] && echo "  - CLAUDE.md       (Claude Code config)"
[ "$WITH_CURSOR" = true ] && echo "  - .cursorrules    (Cursor config)"
echo ""
echo "Next steps:"
echo "  1. Edit TASKS.md to add your tasks"
echo "  2. Run your AI agent - it will follow the rules"
echo "  3. Run 'python verify.py <task-id>' to verify claims"
echo ""
