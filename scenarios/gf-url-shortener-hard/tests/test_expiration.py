"""Tests for expiration."""

import pytest
from src.expiration import is_expired, cleanup_expired
from src.models import Link


class TestExpiration:
    def test_not_expired_no_ttl(self, clock):
        link = Link(short_code="a", original_url="http://x.com", client_id="c", created_at=clock())
        assert is_expired(link, clock=clock) is False

    def test_not_expired_future(self, clock):
        link = Link(short_code="a", original_url="http://x.com", client_id="c", created_at=clock(), expires_at=clock.now + 100)
        assert is_expired(link, clock=clock) is False

    def test_expired(self, clock):
        link = Link(short_code="a", original_url="http://x.com", client_id="c", created_at=clock(), expires_at=clock.now - 1)
        assert is_expired(link, clock=clock) is True

    def test_expired_exact_boundary(self, clock):
        link = Link(short_code="a", original_url="http://x.com", client_id="c", created_at=clock(), expires_at=clock.now)
        assert is_expired(link, clock=clock) is True

    def test_resolve_returns_none_for_expired(self, shortener, clock):
        link = shortener.shorten("http://example.com", "c1", ttl_seconds=10)
        clock.advance(11)
        assert shortener.resolve(link.short_code) is None

    def test_cleanup_expired(self, storage, clock):
        storage.save_link(Link(short_code="a", original_url="http://a.com", client_id="c", created_at=clock(), expires_at=clock.now - 10))
        storage.save_link(Link(short_code="b", original_url="http://b.com", client_id="c", created_at=clock(), expires_at=clock.now + 100))
        removed = cleanup_expired(storage, clock=clock)
        assert removed == 1
        assert storage.get_link("a") is None
        assert storage.get_link("b") is not None

    def test_list_urls_excludes_expired(self, shortener, clock):
        shortener.shorten("http://a.com", "c1", ttl_seconds=5)
        shortener.shorten("http://b.com", "c1")
        clock.advance(6)
        urls = shortener.list_urls("c1")
        assert len(urls) == 1
        assert urls[0].original_url == "http://b.com"
