"""Click analytics tracking."""

import time
from typing import List, Optional, Tuple

from src.models import ClickEvent
from src.storage import Storage


class Analytics:
    def __init__(self, storage: Storage, clock=None):
        self._storage = storage
        self._clock = clock or time.time

    def record_click(self, short_code: str, referrer: Optional[str] = None, client_ip: Optional[str] = None) -> None:
        click = ClickEvent(
            short_code=short_code,
            timestamp=self._clock(),
            referrer=referrer,
            client_ip=client_ip,
        )
        self._storage.save_click(click)
        link = self._storage.get_link(short_code)
        if link:
            link.click_count += 1
            self._storage.save_link(link)

    def get_click_count(self, short_code: str) -> int:
        return len(self._storage.get_clicks(short_code))

    def get_clicks(self, short_code: str, since: Optional[float] = None) -> List[ClickEvent]:
        clicks = self._storage.get_clicks(short_code)
        if since is not None:
            clicks = [c for c in clicks if c.timestamp >= since]
        return clicks

    def get_top_links(self, n: int = 10) -> List[Tuple[str, int]]:
        all_links = self._storage.list_links()
        counted = [(l.short_code, len(self._storage.get_clicks(l.short_code))) for l in all_links]
        counted.sort(key=lambda x: x[1], reverse=True)
        return counted[:n]
