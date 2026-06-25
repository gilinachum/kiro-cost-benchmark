"""URL Shortener — Reference Implementation."""

import hashlib
import threading
from typing import Dict, Optional
from urllib.parse import urlparse

_lock = threading.Lock()
_url_to_code: Dict[str, str] = {}
_code_to_url: Dict[str, str] = {}

_ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def _generate_code(url: str) -> str:
    """Generate a deterministic 6-char alphanumeric code from a URL."""
    digest = hashlib.sha256(url.encode()).digest()
    code = []
    for i in range(6):
        code.append(_ALPHABET[digest[i] % len(_ALPHABET)])
    return "".join(code)


def _validate_url(url: str) -> None:
    stripped = url.strip()
    if not stripped:
        raise ValueError("URL must not be empty")
    parsed = urlparse(stripped)
    if not parsed.scheme:
        raise ValueError(f"Invalid URL (no scheme): {url}")


def shorten(url: str) -> str:
    _validate_url(url)
    with _lock:
        if url in _url_to_code:
            return _url_to_code[url]
        code = _generate_code(url)
        _url_to_code[url] = code
        _code_to_url[code] = url
        return code


def resolve(short_code: str) -> Optional[str]:
    with _lock:
        return _code_to_url.get(short_code)


def delete(short_code: str) -> bool:
    with _lock:
        if short_code in _code_to_url:
            url = _code_to_url.pop(short_code)
            _url_to_code.pop(url, None)
            return True
        return False


def list_urls() -> Dict[str, str]:
    with _lock:
        return dict(_code_to_url)
