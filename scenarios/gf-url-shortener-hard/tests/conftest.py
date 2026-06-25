"""Shared test fixtures."""

import pytest
import time

from src.storage import InMemoryStorage
from src.shortener import URLShortener
from src.rate_limiter import RateLimiter
from src.analytics import Analytics


@pytest.fixture
def storage():
    return InMemoryStorage()


@pytest.fixture
def clock():
    """Mockable clock that returns a mutable current time."""
    class MockClock:
        def __init__(self):
            self.now = 1000000.0

        def __call__(self):
            return self.now

        def advance(self, seconds):
            self.now += seconds

    return MockClock()


@pytest.fixture
def rate_limiter(clock):
    return RateLimiter(max_requests=5, window_seconds=60, clock=clock)


@pytest.fixture
def shortener(storage, rate_limiter, clock):
    return URLShortener(storage=storage, rate_limiter=rate_limiter, clock=clock)


@pytest.fixture
def shortener_no_limit(storage, clock):
    return URLShortener(storage=storage, clock=clock)


@pytest.fixture
def analytics(storage, clock):
    return Analytics(storage=storage, clock=clock)
