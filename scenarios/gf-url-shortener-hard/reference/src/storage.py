"""Abstract storage interface and in-memory implementation."""

from abc import ABC, abstractmethod
from threading import RLock
from typing import List, Optional

from src.models import Link, ClickEvent


class Storage(ABC):
    @abstractmethod
    def save_link(self, link: Link) -> None: ...

    @abstractmethod
    def get_link(self, short_code: str) -> Optional[Link]: ...

    @abstractmethod
    def delete_link(self, short_code: str) -> bool: ...

    @abstractmethod
    def list_links(self, client_id: Optional[str] = None) -> List[Link]: ...

    @abstractmethod
    def save_click(self, click: ClickEvent) -> None: ...

    @abstractmethod
    def get_clicks(self, short_code: str) -> List[ClickEvent]: ...

    @abstractmethod
    def get_links_expiring_before(self, timestamp: float) -> List[Link]: ...


class InMemoryStorage(Storage):
    def __init__(self):
        self._links: dict[str, Link] = {}
        self._clicks: list[ClickEvent] = []
        self._lock = RLock()

    def save_link(self, link: Link) -> None:
        with self._lock:
            self._links[link.short_code] = link

    def get_link(self, short_code: str) -> Optional[Link]:
        with self._lock:
            return self._links.get(short_code)

    def delete_link(self, short_code: str) -> bool:
        with self._lock:
            if short_code in self._links:
                del self._links[short_code]
                return True
            return False

    def list_links(self, client_id: Optional[str] = None) -> List[Link]:
        with self._lock:
            links = list(self._links.values())
            if client_id is not None:
                links = [l for l in links if l.client_id == client_id]
            return links

    def save_click(self, click: ClickEvent) -> None:
        with self._lock:
            self._clicks.append(click)

    def get_clicks(self, short_code: str) -> List[ClickEvent]:
        with self._lock:
            return [c for c in self._clicks if c.short_code == short_code]

    def get_links_expiring_before(self, timestamp: float) -> List[Link]:
        with self._lock:
            return [
                l for l in self._links.values()
                if l.expires_at is not None and l.expires_at <= timestamp
            ]
