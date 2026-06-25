"""Tests for data models."""

from src.models import Link, ClickEvent, RateLimitEntry


class TestLink:
    def test_create_link_required_fields(self):
        link = Link(short_code="abc123", original_url="http://example.com", client_id="c1", created_at=100.0)
        assert link.short_code == "abc123"
        assert link.original_url == "http://example.com"
        assert link.client_id == "c1"
        assert link.created_at == 100.0

    def test_link_defaults(self):
        link = Link(short_code="x", original_url="http://x.com", client_id="c", created_at=0.0)
        assert link.expires_at is None
        assert link.click_count == 0
        assert link.is_active is True

    def test_click_event_defaults(self):
        ev = ClickEvent(short_code="abc", timestamp=500.0)
        assert ev.referrer is None
        assert ev.client_ip is None

    def test_rate_limit_entry_defaults(self):
        entry = RateLimitEntry(client_id="c1")
        assert entry.timestamps == []
