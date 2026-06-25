"""Tests for rate limiter."""

import pytest
from src.rate_limiter import RateLimiter, RateLimitExceeded


class TestRateLimiter:
    def test_allows_under_limit(self, clock):
        rl = RateLimiter(max_requests=3, window_seconds=60, clock=clock)
        assert rl.check_rate_limit("c1") is True

    def test_allows_up_to_max(self, clock):
        rl = RateLimiter(max_requests=3, window_seconds=60, clock=clock)
        for _ in range(3):
            rl.record_request("c1")
        assert rl.check_rate_limit("c1") is False

    def test_denies_over_limit(self, clock):
        rl = RateLimiter(max_requests=2, window_seconds=60, clock=clock)
        rl.record_request("c1")
        rl.record_request("c1")
        assert rl.check_rate_limit("c1") is False

    def test_window_slides(self, clock):
        rl = RateLimiter(max_requests=2, window_seconds=60, clock=clock)
        rl.record_request("c1")
        rl.record_request("c1")
        assert rl.check_rate_limit("c1") is False
        clock.advance(61)
        assert rl.check_rate_limit("c1") is True

    def test_different_clients_independent(self, clock):
        rl = RateLimiter(max_requests=1, window_seconds=60, clock=clock)
        rl.record_request("c1")
        assert rl.check_rate_limit("c1") is False
        assert rl.check_rate_limit("c2") is True

    def test_partial_window_expiry(self, clock):
        rl = RateLimiter(max_requests=3, window_seconds=60, clock=clock)
        rl.record_request("c1")
        clock.advance(30)
        rl.record_request("c1")
        rl.record_request("c1")
        assert rl.check_rate_limit("c1") is False
        clock.advance(31)  # first request expires
        assert rl.check_rate_limit("c1") is True

    def test_record_and_check_cycle(self, clock):
        rl = RateLimiter(max_requests=1, window_seconds=10, clock=clock)
        assert rl.check_rate_limit("c1") is True
        rl.record_request("c1")
        assert rl.check_rate_limit("c1") is False
        clock.advance(11)
        assert rl.check_rate_limit("c1") is True

    def test_zero_requests_in_window(self, clock):
        rl = RateLimiter(max_requests=5, window_seconds=60, clock=clock)
        # No requests yet
        assert rl.check_rate_limit("new_client") is True

    def test_multiple_windows(self, clock):
        rl = RateLimiter(max_requests=2, window_seconds=10, clock=clock)
        rl.record_request("c1")
        rl.record_request("c1")
        clock.advance(11)
        rl.record_request("c1")
        rl.record_request("c1")
        assert rl.check_rate_limit("c1") is False
        clock.advance(11)
        assert rl.check_rate_limit("c1") is True
