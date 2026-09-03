# Contributing to Agent Checkpoint

Thanks for your interest in improving Agent Checkpoint!

## Quick Start

1. Fork the repo
2. Clone your fork
3. Make changes
4. Test with `python verify.py --check verify.py:1-50`
5. Submit a PR

## Guidelines

### Code Style
- Keep `verify.py` compact — it's embedded in `install.sh`
- Python 3.8+ compatibility
- No external dependencies (stdlib only)

### Adding Stub Patterns
To add new stub detection patterns, edit `STUB_PATTERNS` in `verify.py`:

```python
STUB_PATTERNS = [
    r'\bTODO\b',
    r'\bYOUR_NEW_PATTERN\b',  # Add here
    ...
]
```

### Testing Changes
```bash
# Quick check
python verify.py --check verify.py:50-100

# Full verification
python verify.py --all --no-log
```

### Updating install.sh
If you modify `verify.py`, you must also update the embedded copy in `install.sh`.

## Pull Request Process

1. Update README.md if adding features
2. Test the install script: `bash install.sh`
3. Ensure `verify.py --help` works
4. Keep commits focused and atomic

## Reporting Issues

Include:
- OS and Python version
- Steps to reproduce
- Expected vs actual behavior
- Relevant TASKS.md/AGENT_LOG.md snippets

## Questions?

Open an issue with the `question` label.
