"""TTL and expiration management."""

import time

from src.models import Link
from src.storage import Storage


def is_expired(link: Link, clock=None) -> bool:
    _clock = clock or time.time
    if link.expires_at is None:
        return False
    return _clock() >= link.expires_at


def cleanup_expired(storage: Storage, clock=None) -> int:
    _clock = clock or time.time
    now = _clock()
    expired = storage.get_links_expiring_before(now)
    count = 0
    for link in expired:
        storage.delete_link(link.short_code)
        count += 1
    return count
