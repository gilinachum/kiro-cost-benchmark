"""Sliding window rate limiter."""

import time
from threading import RLock


class RateLimitExceeded(Exception):
    pass


class RateLimiter:
    def __init__(self, max_requests: int = 10, window_seconds: float = 60, clock=None):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._clock = clock or time.time
        self._requests: dict[str, list[float]] = {}
        self._lock = RLock()

    def _cleanup(self, client_id: str) -> None:
        now = self._clock()
        cutoff = now - self.window_seconds
        if client_id in self._requests:
            self._requests[client_id] = [
                t for t in self._requests[client_id] if t > cutoff
            ]

    def check_rate_limit(self, client_id: str) -> bool:
        with self._lock:
            self._cleanup(client_id)
            timestamps = self._requests.get(client_id, [])
            return len(timestamps) < self.max_requests

    def record_request(self, client_id: str) -> None:
        with self._lock:
            self._cleanup(client_id)
            if client_id not in self._requests:
                self._requests[client_id] = []
            self._requests[client_id].append(self._clock())
