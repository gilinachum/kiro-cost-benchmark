"""Tests for storage layer."""

import threading
from src.storage import InMemoryStorage
from src.models import Link, ClickEvent


class TestInMemoryStorage:
    def test_save_and_get_link(self, storage):
        link = Link(short_code="abc", original_url="http://x.com", client_id="c1", created_at=1.0)
        storage.save_link(link)
        assert storage.get_link("abc") == link

    def test_get_nonexistent(self, storage):
        assert storage.get_link("nope") is None

    def test_delete_link(self, storage):
        link = Link(short_code="abc", original_url="http://x.com", client_id="c1", created_at=1.0)
        storage.save_link(link)
        assert storage.delete_link("abc") is True
        assert storage.get_link("abc") is None

    def test_delete_nonexistent(self, storage):
        assert storage.delete_link("nope") is False

    def test_list_links_all(self, storage):
        for i in range(3):
            storage.save_link(Link(short_code=f"s{i}", original_url=f"http://{i}.com", client_id="c1", created_at=float(i)))
        assert len(storage.list_links()) == 3

    def test_list_links_by_client(self, storage):
        storage.save_link(Link(short_code="a", original_url="http://a.com", client_id="c1", created_at=1.0))
        storage.save_link(Link(short_code="b", original_url="http://b.com", client_id="c2", created_at=2.0))
        assert len(storage.list_links(client_id="c1")) == 1

    def test_save_and_get_clicks(self, storage):
        click = ClickEvent(short_code="abc", timestamp=100.0, referrer="google.com")
        storage.save_click(click)
        clicks = storage.get_clicks("abc")
        assert len(clicks) == 1
        assert clicks[0].referrer == "google.com"

    def test_thread_safety(self, storage):
        errors = []

        def writer(n):
            try:
                for i in range(50):
                    storage.save_link(Link(short_code=f"t{n}_{i}", original_url="http://x.com", client_id="c", created_at=0.0))
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=writer, args=(n,)) for n in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert not errors
        assert len(storage.list_links()) == 200
