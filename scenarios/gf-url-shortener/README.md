# URL Shortener — Benchmark Scenario

## What This Is
A benchmark scenario for evaluating an AI agent's ability to implement a Python library from a spec and test suite.

## The Task
The agent receives `SPEC.md` and `tests/` and must produce a `shortener.py` module that passes all tests.

## How to Run Tests
```bash
cd scenarios/gf-url-shortener
cp reference/shortener.py shortener.py  # or use agent's implementation
pytest tests/
```

## What Success Means
All tests pass (`pytest tests/` exits 0).

## Structure
- `SPEC.md` — Requirements given to the agent
- `tests/` — Test suite (given to agent)
- `reference/` — Working reference implementation (NOT given to agent)
