"""URL and alias validation."""

import re
from urllib.parse import urlparse


def validate_url(url: str) -> None:
    if not url or not url.strip():
        raise ValueError("URL must not be empty")
    if len(url) > 2048:
        raise ValueError("URL must not exceed 2048 characters")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https", "ftp"):
        raise ValueError(f"URL scheme must be http, https, or ftp, got '{parsed.scheme}'")
    if not parsed.netloc:
        raise ValueError("URL must have a valid host")


def validate_alias(alias: str) -> None:
    if len(alias) < 3 or len(alias) > 20:
        raise ValueError("Alias must be between 3 and 20 characters")
    if not re.match(r'^[a-zA-Z0-9-]+$', alias):
        raise ValueError("Alias must contain only alphanumeric characters and hyphens")
    if alias.startswith('-') or alias.endswith('-'):
        raise ValueError("Alias must not start or end with a hyphen")
