# Contributing to VerDiff

Thanks for contributing to **VerDiff** (part of **Vernal Forge**).

## Development Setup

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

pip install -e ".[dev]"
pytest tests/test_verdiff.py -v
```

## Guidelines

- Keep runtime dependencies at zero (Python standard library only).
- Ensure generated reproduction tests remain standalone, deterministic, and runnable with `pytest`.
- Add or update unit tests in `tests/test_verdiff.py` for any new fuzzing strategy, AST probe, or diff rule.
