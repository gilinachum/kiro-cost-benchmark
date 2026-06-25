# gf-url-shortener-hard

A multi-module URL shortener benchmark scenario for evaluating AI coding agents on complex, multi-file Python projects.

## What This Tests

- Multi-module architecture (7 source files with cross-dependencies)
- Abstract base classes and concrete implementations
- Thread safety (RLock usage)
- Dataclass modeling
- Input validation with descriptive errors
- Sliding window rate limiting
- TTL/expiration logic
- Atomic bulk operations with rollback
- Deterministic hashing for idempotent operations
- Proper test isolation via fixtures

## Structure

```
SPEC.md          — Agent-facing specification (give this to the agent)
tests/           — 71 tests across 8 files (agent receives these)
reference/src/   — Working reference implementation
```

## How to Run

```bash
# Verify reference passes
cd reference && PYTHONPATH=. pytest ../tests/ -v

# Agent workflow: give them SPEC.md + tests/, they produce src/
# Dependencies: pip install pytest (no other packages required)
```

## Success Criteria

All 71 tests pass with `PYTHONPATH=. pytest tests/ -v`.

## Test Distribution

| File | Tests |
|------|-------|
| test_models.py | 4 |
| test_storage.py | 8 |
| test_validation.py | 7 + 6 = 13 |
| test_shortener.py | 15 |
| test_analytics.py | 9 |
| test_rate_limiter.py | 9 |
| test_expiration.py | 7 |
| test_integration.py | 6 |
| **Total** | **71** |
