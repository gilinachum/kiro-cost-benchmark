"""Tests for analytics."""

import pytest
from src.analytics import Analytics
from src.models import Link


class TestAnalytics:
    def test_record_click(self, analytics, storage, clock):
        storage.save_link(Link(short_code="abc", original_url="http://x.com", client_id="c1", created_at=clock()))
        analytics.record_click("abc")
        assert analytics.get_click_count("abc") == 1

    def test_multiple_clicks(self, analytics, storage, clock):
        storage.save_link(Link(short_code="abc", original_url="http://x.com", client_id="c1", created_at=clock()))
        for _ in range(5):
            analytics.record_click("abc")
        assert analytics.get_click_count("abc") == 5

    def test_click_with_referrer(self, analytics, storage, clock):
        storage.save_link(Link(short_code="abc", original_url="http://x.com", client_id="c1", created_at=clock()))
        analytics.record_click("abc", referrer="google.com")
        clicks = analytics.get_clicks("abc")
        assert clicks[0].referrer == "google.com"

    def test_click_with_ip(self, analytics, storage, clock):
        storage.save_link(Link(short_code="abc", original_url="http://x.com", client_id="c1", created_at=clock()))
        analytics.record_click("abc", client_ip="1.2.3.4")
        clicks = analytics.get_clicks("abc")
        assert clicks[0].client_ip == "1.2.3.4"

    def test_get_clicks_since(self, analytics, storage, clock):
        storage.save_link(Link(short_code="abc", original_url="http://x.com", client_id="c1", created_at=clock()))
        analytics.record_click("abc")
        clock.advance(100)
        analytics.record_click("abc")
        clicks = analytics.get_clicks("abc", since=clock.now - 50)
        assert len(clicks) == 1

    def test_get_click_count_no_clicks(self, analytics):
        assert analytics.get_click_count("noexist") == 0

    def test_get_top_links(self, analytics, storage, clock):
        for code in ["a", "b", "c"]:
            storage.save_link(Link(short_code=code, original_url=f"http://{code}.com", client_id="c1", created_at=clock()))
        for _ in range(3):
            analytics.record_click("a")
        analytics.record_click("b")
        for _ in range(5):
            analytics.record_click("c")
        top = analytics.get_top_links(2)
        assert top[0] == ("c", 5)
        assert top[1] == ("a", 3)
        assert len(top) == 2

    def test_get_top_links_empty(self, analytics):
        assert analytics.get_top_links() == []

    def test_click_updates_link_count(self, analytics, storage, clock):
        storage.save_link(Link(short_code="abc", original_url="http://x.com", client_id="c1", created_at=clock()))
        analytics.record_click("abc")
        analytics.record_click("abc")
        link = storage.get_link("abc")
        assert link.click_count == 2
