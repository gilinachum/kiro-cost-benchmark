"""Data models for the URL shortener."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Link:
    short_code: str
    original_url: str
    client_id: str
    created_at: float
    expires_at: Optional[float] = None
    click_count: int = 0
    is_active: bool = True


@dataclass
class ClickEvent:
    short_code: str
    timestamp: float
    referrer: Optional[str] = None
    client_ip: Optional[str] = None


@dataclass
class RateLimitEntry:
    client_id: str
    timestamps: list = field(default_factory=list)
