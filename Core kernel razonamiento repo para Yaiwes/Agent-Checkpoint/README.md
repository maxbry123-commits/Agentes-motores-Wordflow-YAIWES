<p align="center">
  <h1 align="center">Agent Checkpoint</h1>
  <p align="center">
    <strong>A control plane for AI coding agents that prevents lies and ensures transparency.</strong>
  </p>
  <p align="center">
    <a href="https://github.com/akz4ol/agent-checkpoint/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
    <a href="https://github.com/akz4ol/agent-checkpoint"><img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python"></a>
    <a href="https://github.com/akz4ol/agent-checkpoint"><img src="https://img.shields.io/badge/agents-Claude%20%7C%20Cursor%20%7C%20Gemini%20%7C%20Copilot-purple.svg" alt="Agents"></a>
  </p>
</p>

---

## The Problem

AI coding agents frequently:
- Claim implementations are complete when they're mocked/stubbed
- Lose track of progress between sessions
- Make verification tedious and manual
- Operate without transparency or audit trails

> **Studies show 42% of AI-generated code contains hallucinations** — Stanford/Hugging Face, 2024

## The Solution

```
┌─────────────────────────────────────────────────────────────┐
│                     AGENT CHECKPOINT                        │
├─────────────────────────────────────────────────────────────┤
│  TASKS.md        │  Human-editable task list (control)     │
│  AGENT_LOG.md    │  Append-only audit trail (transparency) │
│  verify.py       │  Stub/mock detection (verification)     │
│  .agent-rules.md │  Works with ANY agent (universal)       │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### One-Line Install

```bash
curl -fsSL https://raw.githubusercontent.com/akz4ol/agent-checkpoint/main/install.sh | bash
```

**With agent config:**
```bash
# For Claude Code
curl -fsSL https://raw.githubusercontent.com/akz4ol/agent-checkpoint/main/install.sh | bash -s -- --with-claude

# For Cursor
curl -fsSL https://raw.githubusercontent.com/akz4ol/agent-checkpoint/main/install.sh | bash -s -- --with-cursor

# Both
curl -fsSL https://raw.githubusercontent.com/akz4ol/agent-checkpoint/main/install.sh | bash -s -- --all
```

### Manual Install

```bash
git clone https://github.com/akz4ol/agent-checkpoint.git
cp agent-checkpoint/{TASKS.md,AGENT_LOG.md,.agent-rules.md,verify.py} /your/project/
```

## How It Works

```
Human defines tasks in TASKS.md
         │
         ▼
Agent picks up task, marks [~], logs to AGENT_LOG.md
         │
         ▼
Agent implements, logs claims with file:line references
         │
         ▼
Verification runs: file exists? not a stub? tests pass?
         │
         ▼
PASS → mark [x]    FAIL → keep [~], fix issues
```

## Define Tasks

Edit `TASKS.md`:

```markdown
## Your Feature

- [ ] 1.1 Create user model `src/models/user.py:User`
  - verify: auto

- [ ] 1.2 Add validation `src/models/user.py:validate_user`
  - verify: tests
  - tests: tests/test_user.py

- [ ] 1.3 Create API endpoint `src/routes/users.py`
  - verify: human
  - depends: 1.1, 1.2
```

## Verification Levels

| Level | What It Checks | Use For |
|-------|----------------|---------|
| `none` | Nothing | Trivial tasks |
| `auto` | File exists, function exists, not-stub | Standard work |
| `tests` | Auto + runs specified tests | Code with coverage |
| `human` | Auto + pauses for human review | Critical features |

## Stub Detection

Catches common lie patterns:

| Pattern | Example |
|---------|---------|
| TODO markers | `TODO`, `FIXME`, `XXX`, `HACK` |
| Not implemented | `raise NotImplementedError` |
| Empty functions | `pass`, `pass #`, `...` |
| Stub comments | `// stub`, `/* mock */`, `# placeholder` |
| Too short | Functions with < 3 meaningful lines |

## CLI Usage

```bash
# Verify a specific task
python verify.py 1.1

# Verify all in-progress tasks
python verify.py --all

# Quick check a file:line claim
python verify.py --check src/auth.ts:15-45

# Verify without logging
python verify.py 1.1 --no-log
```

## Task Status Markers

| Marker | Meaning |
|--------|---------|
| `[ ]` | Pending |
| `[~]` | In Progress |
| `[x]` | Complete (verified) |
| `[?]` | Needs Human Review |
| `[!]` | Blocked |

## Agent Compatibility

Works with any agent that can read/edit markdown:

| Agent | Config File | Auto-reads on |
|-------|-------------|---------------|
| Claude Code | `CLAUDE.md` | Session start |
| Cursor | `.cursorrules` | IDE start |
| GitHub Copilot | `.github/copilot-instructions.md` | New chat |
| Gemini CLI | Context prompt | Each session |
| Cline | `.clinerules` | Session start |
| Windsurf | `.windsurfrules` | IDE start |

## Example Audit Trail

`AGENT_LOG.md` after agent completes a task:

```markdown
---
## 2025-01-25T10:30:00Z | claude-code | Task 1.1

**Status**: STARTED
**Task**: Create user model

---
## 2025-01-25T10:45:00Z | claude-code | Task 1.1

**Status**: CLAIM
**Files**:
- src/models/user.py:1-45 (created User model)

---
## 2025-01-25T10:46:00Z | verify.py | Task 1.1

**Status**: VERIFIED
**Results**:
- file-exists: PASS
- not-stub: PASS
```

## Why It Works

| Problem | Solution |
|---------|----------|
| Agents lie about completion | Verification gates check actual code |
| Stubs marked as done | Stub detection catches TODO/FIXME/etc |
| Lost progress between sessions | TASKS.md persists in git |
| No audit trail | AGENT_LOG.md is append-only |
| Works with one agent only | Markdown conventions work everywhere |
| Complex setup | One-line install |

## Requirements

- Python 3.8+
- pytest (for Python test verification)
- jest/node (for JS/TS test verification)

## Contributing

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Run `python verify.py --all` on your changes
5. Submit a PR

## License

[MIT](LICENSE) — Use freely, attribution appreciated.

---

<p align="center">
  <sub>Built to keep AI agents honest.</sub>
</p>
