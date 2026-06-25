# URL Shortener — Multi-Module Project

## Overview
Build a URL shortener as a multi-module Python project. The system supports creating short links, custom aliases, click analytics, rate limiting, and link expiration.

## Project Structure
You must create ALL of the following files:

```
src/
  __init__.py     # Package marker
  models.py       # Data classes (Link, ClickEvent, RateLimitEntry)
  storage.py      # Abstract storage interface + InMemoryStorage implementation
  validation.py   # URL validation, alias validation
  shortener.py    # Core shortener service (depends on models, storage, validation)
  analytics.py    # Click tracking (count, timestamps, referrer)
  rate_limiter.py # Sliding window rate limiter (per-client)
  expiration.py   # TTL management, cleanup of expired links
```

## Module Specifications

### models.py
- `Link` dataclass: `short_code`, `original_url`, `client_id`, `created_at` (float), `expires_at` (Optional[float], default None), `click_count` (int, default 0), `is_active` (bool, default True)
- `ClickEvent` dataclass: `short_code`, `timestamp` (float), `referrer` (Optional[str], default None), `client_ip` (Optional[str], default None)
- `RateLimitEntry` dataclass: `client_id`, `timestamps` (list, default empty)

### storage.py
- Abstract base class `Storage` with methods: `save_link(link)`, `get_link(short_code)`, `delete_link(short_code) -> bool`, `list_links(client_id=None)`, `save_click(click)`, `get_clicks(short_code)`, `get_links_expiring_before(timestamp)`
- `InMemoryStorage(Storage)` — concrete implementation, thread-safe with `threading.RLock`

### validation.py
- `validate_url(url)` — must have http/https/ftp scheme, non-empty, max 2048 chars. Raises ValueError.
- `validate_alias(alias)` — 3-20 chars, alphanumeric + hyphens only, can't start/end with hyphen. Raises ValueError.

### shortener.py
- `URLShortener` class, constructor takes `storage`, optional `rate_limiter`, optional `clock` (callable returning float, defaults to `time.time`)
- `shorten(url, client_id, alias=None, ttl_seconds=None) -> Link` — validates URL, checks rate limit, generates/uses code, saves link
- `resolve(short_code) -> str | None` — returns original URL or None if expired/deleted/missing
- `delete(short_code) -> bool`
- `list_urls(client_id=None) -> list[Link]` — excludes expired and inactive links
- `bulk_shorten(urls: list[dict], client_id) -> list[Link]` — atomic: all succeed or rollback on failure. Each dict has keys: `url`, optional `alias`, optional `ttl_seconds`
- Code generation: Short code = first 8 characters of `hashlib.sha256((url + (alias or "")).encode()).hexdigest()`. Note: `client_id` is NOT part of the hash — the same URL always produces the same code regardless of which client shortened it. Deterministic (same input → same code).
- Custom alias: if `alias` provided, use it as the short_code directly (after validation)
- Alias collision: raises `ValueError` with message containing "already taken"

### analytics.py
- `Analytics` class, constructor takes `storage` and optional `clock`
- `record_click(short_code, referrer=None, client_ip=None)` — saves ClickEvent AND increments link's `click_count` field (both must happen)
- `get_click_count(short_code) -> int` — must count stored ClickEvents (not `link.click_count`). For nonexistent short codes, returns 0.
- `get_clicks(short_code, since=None) -> list[ClickEvent]` — filter by timestamp >= since
- `get_top_links(n=10) -> list[tuple[str, int]]` — top N links by click count, sorted descending

### rate_limiter.py
- `RateLimitExceeded(Exception)` — custom exception
- `RateLimiter` class, constructor takes `max_requests` (int), `window_seconds` (float), optional `clock`
- `check_rate_limit(client_id) -> bool` — True if under limit
- `record_request(client_id)` — records a timestamp for the client
- Sliding window: only counts requests within the last `window_seconds`
- Thread-safe with RLock
- Integration: `URLShortener.shorten()` checks rate limit before creating, raises `RateLimitExceeded` if over

### expiration.py
- `is_expired(link, clock=None) -> bool` — True if link.expires_at is not None and current time >= expires_at
- `cleanup_expired(storage, clock=None) -> int` — deletes all expired links from storage, returns count removed

## Key Behaviors
1. **Deterministic codes**: Same URL (with same alias) always produces the same short code. If code already exists, return existing link.
2. **Rate limiting integrated**: `shorten()` calls `check_rate_limit` then `record_request` on the rate limiter (if one is configured). `bulk_shorten` does NOT check rate limits (it's an admin/batch operation).
3. **Expiration checking**: `resolve()` returns None for expired links. `list_urls()` excludes expired links.
4. **Bulk atomicity**: If any URL in `bulk_shorten` fails (e.g., alias collision), all previously created links in that batch are rolled back.

## Running Tests
```bash
pip install pytest
PYTHONPATH=. pytest tests/ -v
```

Tests are provided in the `tests/` directory. Your implementation must pass all of them.
