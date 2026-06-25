"""Integration tests — cross-module flows."""

import pytest
from src.shortener import URLShortener
from src.analytics import Analytics
from src.expiration import cleanup_expired
from src.rate_limiter import RateLimiter, RateLimitExceeded


class TestIntegration:
    def test_shorten_click_analytics(self, shortener, analytics):
        link = shortener.shorten("http://example.com", "c1")
        url = shortener.resolve(link.short_code)
        analytics.record_click(link.short_code, referrer="twitter.com")
        assert url == "http://example.com"
        assert analytics.get_click_count(link.short_code) == 1
        clicks = analytics.get_clicks(link.short_code)
        assert clicks[0].referrer == "twitter.com"

    def test_bulk_shorten_with_rate_limit(self, storage, clock):
        rl = RateLimiter(max_requests=2, window_seconds=60, clock=clock)
        shortener = URLShortener(storage=storage, rate_limiter=rl, clock=clock)
        shortener.shorten("http://a.com", "c1")
        shortener.shorten("http://b.com", "c1")
        with pytest.raises(RateLimitExceeded):
            shortener.shorten("http://c.com", "c1")

    def test_expire_then_cleanup(self, storage, clock):
        from src.models import Link
        storage.save_link(Link(short_code="old", original_url="http://old.com", client_id="c", created_at=clock(), expires_at=clock.now + 10))
        clock.advance(11)
        removed = cleanup_expired(storage, clock=clock)
        assert removed == 1
        assert storage.get_link("old") is None

    def test_full_lifecycle(self, shortener, analytics, clock):
        # Create
        link = shortener.shorten("http://lifecycle.com", "c1", ttl_seconds=100)
        # Use
        assert shortener.resolve(link.short_code) == "http://lifecycle.com"
        analytics.record_click(link.short_code)
        assert analytics.get_click_count(link.short_code) == 1
        # Expire
        clock.advance(101)
        assert shortener.resolve(link.short_code) is None

    def test_multiple_clients_isolated(self, shortener_no_limit, analytics, clock):
        l1 = shortener_no_limit.shorten("http://a.com", "client-a")
        l2 = shortener_no_limit.shorten("http://b.com", "client-b")
        analytics.record_click(l1.short_code)
        assert shortener_no_limit.list_urls("client-a") == [l1]
        assert analytics.get_click_count(l2.short_code) == 0

    def test_delete_stops_resolution(self, shortener):
        link = shortener.shorten("http://example.com", "c1")
        shortener.delete(link.short_code)
        assert shortener.resolve(link.short_code) is None
