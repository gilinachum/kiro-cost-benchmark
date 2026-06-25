# URL Shortener Library — Specification

## Overview
Build a Python module `shortener.py` that provides an in-memory URL shortener.

## API

### `shorten(url: str) -> str`
- Returns a 6-character alphanumeric short code for the given URL.
- **Deterministic**: the same URL always produces the same short code.
- Raises `ValueError` if the URL is invalid.

### `resolve(short_code: str) -> str | None`
- Returns the original URL for a short code, or `None` if not found.

### `delete(short_code: str) -> bool`
- Removes the mapping. Returns `True` if it existed, `False` otherwise.

### `list_urls() -> dict[str, str]`
- Returns all current mappings as `{short_code: url}`.

## Validation Rules
- URLs **must** have a scheme (e.g. `http://` or `https://`). No scheme = invalid.
- Empty strings are invalid.
- Invalid URLs must raise `ValueError`.

## Short Code Format
- Exactly 6 characters, alphanumeric (`[a-zA-Z0-9]`).
- Unique per URL.
- Deterministic: same input URL → same code every time.

## Thread Safety
- All functions must be safe to call concurrently from multiple threads.

## Storage
- In-memory dictionary is sufficient. No persistence required.
