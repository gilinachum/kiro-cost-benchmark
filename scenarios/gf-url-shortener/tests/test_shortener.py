import threading
import pytest
import shortener


class TestShorten:
    def test_basic_roundtrip(self):
        code = shortener.shorten("https://example.com")
        assert shortener.resolve(code) == "https://example.com"

    def test_deterministic_same_url(self):
        code1 = shortener.shorten("https://example.com")
        code2 = shortener.shorten("https://example.com")
        assert code1 == code2

    def test_different_urls_different_codes(self):
        code1 = shortener.shorten("https://example.com")
        code2 = shortener.shorten("https://other.com")
        assert code1 != code2

    def test_code_format_length(self):
        code = shortener.shorten("https://example.com")
        assert len(code) == 6

    def test_code_format_alphanumeric(self):
        code = shortener.shorten("https://example.com")
        assert code.isalnum()

    def test_code_format_multiple_urls(self):
        urls = [f"https://example.com/{i}" for i in range(20)]
        for url in urls:
            code = shortener.shorten(url)
            assert len(code) == 6
            assert code.isalnum()


class TestValidation:
    def test_no_scheme_raises(self):
        with pytest.raises(ValueError):
            shortener.shorten("example.com")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            shortener.shorten("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError):
            shortener.shorten("   ")

    def test_ftp_scheme_accepted(self):
        code = shortener.shorten("ftp://files.example.com/data")
        assert len(code) == 6


class TestResolve:
    def test_resolve_nonexistent(self):
        assert shortener.resolve("abcdef") is None

    def test_resolve_after_shorten(self):
        code = shortener.shorten("https://example.com")
        assert shortener.resolve(code) == "https://example.com"


class TestDelete:
    def test_delete_existing(self):
        code = shortener.shorten("https://example.com")
        assert shortener.delete(code) is True
        assert shortener.resolve(code) is None

    def test_delete_nonexistent(self):
        assert shortener.delete("zzzzzz") is False

    def test_delete_then_reshorten(self):
        code1 = shortener.shorten("https://example.com")
        shortener.delete(code1)
        code2 = shortener.shorten("https://example.com")
        assert code1 == code2  # deterministic


class TestListUrls:
    def test_empty_initially(self):
        assert shortener.list_urls() == {}

    def test_list_after_shortening(self):
        code = shortener.shorten("https://example.com")
        result = shortener.list_urls()
        assert result == {code: "https://example.com"}

    def test_list_after_delete(self):
        code = shortener.shorten("https://example.com")
        shortener.delete(code)
        assert shortener.list_urls() == {}


class TestThreadSafety:
    def test_concurrent_shortens(self):
        urls = [f"https://example.com/{i}" for i in range(100)]
        results = {}
        errors = []

        def worker(url):
            try:
                results[url] = shortener.shorten(url)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(u,)) for u in urls]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        assert len(set(results.values())) == 100  # all unique codes
