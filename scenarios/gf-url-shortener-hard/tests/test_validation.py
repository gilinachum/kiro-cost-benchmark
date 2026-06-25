"""Tests for validation."""

import pytest
from src.validation import validate_url, validate_alias


class TestValidateUrl:
    def test_valid_http(self):
        validate_url("http://example.com")

    def test_valid_https(self):
        validate_url("https://example.com/path?q=1")

    def test_valid_ftp(self):
        validate_url("ftp://files.example.com/doc.pdf")

    def test_empty_url(self):
        with pytest.raises(ValueError, match="empty"):
            validate_url("")

    def test_no_scheme(self):
        with pytest.raises(ValueError):
            validate_url("example.com")

    def test_invalid_scheme(self):
        with pytest.raises(ValueError, match="scheme"):
            validate_url("mailto:x@y.com")

    def test_too_long(self):
        with pytest.raises(ValueError, match="2048"):
            validate_url("http://example.com/" + "a" * 2048)


class TestValidateAlias:
    def test_valid_alias(self):
        validate_alias("my-link")

    def test_too_short(self):
        with pytest.raises(ValueError, match="3 and 20"):
            validate_alias("ab")

    def test_too_long(self):
        with pytest.raises(ValueError, match="3 and 20"):
            validate_alias("a" * 21)

    def test_invalid_chars(self):
        with pytest.raises(ValueError, match="alphanumeric"):
            validate_alias("my_link!")

    def test_starts_with_hyphen(self):
        with pytest.raises(ValueError, match="hyphen"):
            validate_alias("-mylink")

    def test_ends_with_hyphen(self):
        with pytest.raises(ValueError, match="hyphen"):
            validate_alias("mylink-")
