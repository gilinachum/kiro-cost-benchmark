"""Core URL shortener service."""

import hashlib
import time
from typing import List, Optional

from src.models import Link
from src.storage import Storage
from src.validation import validate_url, validate_alias
from src.rate_limiter import RateLimiter, RateLimitExceeded
from src.expiration import is_expired


class URLShortener:
    def __init__(self, storage: Storage, rate_limiter: Optional[RateLimiter] = None, clock=None):
        self._storage = storage
        self._rate_limiter = rate_limiter
        self._clock = clock or time.time

    def _generate_code(self, url: str, alias: Optional[str] = None) -> str:
        seed = url + (alias or "")
        return hashlib.sha256(seed.encode()).hexdigest()[:8]

    def shorten(self, url: str, client_id: str, alias: Optional[str] = None, ttl_seconds: Optional[float] = None) -> Link:
        validate_url(url)

        if self._rate_limiter:
            if not self._rate_limiter.check_rate_limit(client_id):
                raise RateLimitExceeded(f"Rate limit exceeded for client {client_id}")
            self._rate_limiter.record_request(client_id)

        if alias:
            validate_alias(alias)
            short_code = alias
        else:
            short_code = self._generate_code(url, alias)

        existing = self._storage.get_link(short_code)
        if existing:
            if alias:
                raise ValueError(f"Alias '{alias}' is already taken")
            return existing

        now = self._clock()
        expires_at = now + ttl_seconds if ttl_seconds else None

        link = Link(
            short_code=short_code,
            original_url=url,
            client_id=client_id,
            created_at=now,
            expires_at=expires_at,
        )
        self._storage.save_link(link)
        return link

    def resolve(self, short_code: str) -> Optional[str]:
        link = self._storage.get_link(short_code)
        if link is None or not link.is_active:
            return None
        if is_expired(link, clock=self._clock):
            return None
        return link.original_url

    def delete(self, short_code: str) -> bool:
        return self._storage.delete_link(short_code)

    def list_urls(self, client_id: Optional[str] = None) -> List[Link]:
        links = self._storage.list_links(client_id)
        return [l for l in links if l.is_active and not is_expired(l, clock=self._clock)]

    def bulk_shorten(self, urls: list, client_id: str) -> List[Link]:
        # Validate all first
        for item in urls:
            validate_url(item["url"])
            if "alias" in item and item["alias"]:
                validate_alias(item["alias"])

        # Check for collisions before creating
        results = []
        for item in urls:
            url = item["url"]
            alias = item.get("alias")
            ttl = item.get("ttl_seconds")

            if alias:
                short_code = alias
            else:
                short_code = self._generate_code(url, alias)

            existing = self._storage.get_link(short_code)
            if existing:
                if alias:
                    # Rollback
                    for created in results:
                        self._storage.delete_link(created.short_code)
                    raise ValueError(f"Alias '{alias}' is already taken")
                results.append(existing)
                continue

            now = self._clock()
            expires_at = now + ttl if ttl else None
            link = Link(
                short_code=short_code,
                original_url=url,
                client_id=client_id,
                created_at=now,
                expires_at=expires_at,
            )
            self._storage.save_link(link)
            results.append(link)

        return results
