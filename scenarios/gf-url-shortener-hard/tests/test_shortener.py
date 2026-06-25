"""Tests for the core shortener service."""

import pytest
from src.shortener import URLShortener
from src.rate_limiter import RateLimitExceeded


class TestShortener:
    def test_shorten_basic(self, shortener):
        link = shortener.shorten("http://example.com", "c1")
        assert link.short_code
        assert link.original_url == "http://example.com"
        assert link.client_id == "c1"
        assert len(link.short_code) == 8

    def test_resolve(self, shortener):
        link = shortener.shorten("http://example.com", "c1")
        assert shortener.resolve(link.short_code) == "http://example.com"

    def test_resolve_nonexistent(self, shortener):
        assert shortener.resolve("noexist") is None

    def test_delete(self, shortener):
        link = shortener.shorten("http://example.com", "c1")
        assert shortener.delete(link.short_code) is True
        assert shortener.resolve(link.short_code) is None

    def test_delete_nonexistent(self, shortener):
        assert shortener.delete("noexist") is False

    def test_list_urls(self, shortener):
        shortener.shorten("http://a.com", "c1")
        shortener.shorten("http://b.com", "c1")
        shortener.shorten("http://c.com", "c2")
        assert len(shortener.list_urls("c1")) == 2
        assert len(shortener.list_urls()) == 3

    def test_custom_alias(self, shortener):
        link = shortener.shorten("http://example.com", "c1", alias="my-alias")
        assert link.short_code == "my-alias"

    def test_alias_collision(self, shortener):
        shortener.shorten("http://a.com", "c1", alias="taken")
        with pytest.raises(ValueError, match="already taken"):
            shortener.shorten("http://b.com", "c1", alias="taken")

    def test_deterministic_codes(self, shortener_no_limit, storage, clock):
        link1 = shortener_no_limit.shorten("http://example.com", "c1")
        # Same URL should return same link
        link2 = shortener_no_limit.shorten("http://example.com", "c2")
        assert link1.short_code == link2.short_code

    def test_different_urls_different_codes(self, shortener):
        l1 = shortener.shorten("http://a.com", "c1")
        l2 = shortener.shorten("http://b.com", "c1")
        assert l1.short_code != l2.short_code

    def test_ttl(self, shortener, clock):
        link = shortener.shorten("http://example.com", "c1", ttl_seconds=300)
        assert link.expires_at == clock.now + 300

    def test_bulk_shorten(self, shortener_no_limit):
        urls = [
            {"url": "http://a.com"},
            {"url": "http://b.com"},
            {"url": "http://c.com"},
        ]
        results = shortener_no_limit.bulk_shorten(urls, "c1")
        assert len(results) == 3

    def test_bulk_shorten_rollback_on_collision(self, shortener_no_limit):
        shortener_no_limit.shorten("http://x.com", "c1", alias="existing")
        urls = [
            {"url": "http://a.com"},
            {"url": "http://b.com", "alias": "existing"},
        ]
        with pytest.raises(ValueError):
            shortener_no_limit.bulk_shorten(urls, "c1")
        # First one should be rolled back
        codes = [l.short_code for l in shortener_no_limit.list_urls()]
        # Only "existing" should remain
        assert len(shortener_no_limit.list_urls()) == 1

    def test_invalid_url_raises(self, shortener):
        with pytest.raises(ValueError):
            shortener.shorten("not-a-url", "c1")

    def test_rate_limit_integration(self, shortener):
        for i in range(5):
            shortener.shorten(f"http://example{i}.com", "c1")
        with pytest.raises(RateLimitExceeded):
            shortener.shorten("http://toomany.com", "c1")
