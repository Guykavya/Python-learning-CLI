import httpx
import pytest

from solution import fetch_all


def client_for(pages, status=None):
    """pages: dict url -> body dict (or (status, body)); records the requested URLs."""
    asked = []

    def handler(request):
        url = str(request.url)
        asked.append(url)
        page = pages.get(url)
        if page is None:
            return httpx.Response(404, json={"error": "no such page"})
        if isinstance(page, tuple):
            return httpx.Response(page[0], content=page[1])
        return httpx.Response(200, json=page)

    return httpx.Client(transport=httpx.MockTransport(handler)), asked


BASE = "http://api.test/items"


def test_three_pages_in_order():
    client, asked = client_for({
        BASE + "?page=1": {"items": [1, 2, 3], "next": BASE + "?page=2"},
        BASE + "?page=2": {"items": [4, 5], "next": BASE + "?page=3"},
        BASE + "?page=3": {"items": [6, 7], "next": None},
    })
    assert fetch_all(client, BASE + "?page=1") == [1, 2, 3, 4, 5, 6, 7]
    assert asked == [BASE + "?page=1", BASE + "?page=2", BASE + "?page=3"], "One request per page, in order."


def test_single_page_and_missing_next():
    client, _ = client_for({BASE: {"items": ["a"]}})
    assert fetch_all(client, BASE) == ["a"], "A missing 'next' key is the last page."
    client, _ = client_for({BASE: {"items": [], "next": None}})
    assert fetch_all(client, BASE) == []


def test_relative_next_links():
    client, asked = client_for({
        BASE + "?page=1": {"items": [1], "next": "/items?page=2"},
        BASE + "?page=2": {"items": [2], "next": "?page=3"},
        BASE + "?page=3": {"items": [3], "next": None},
    })
    assert fetch_all(client, BASE + "?page=1") == [1, 2, 3], "Resolve relative links with urljoin against the current URL."


def test_a_loop_is_detected():
    client, asked = client_for({
        BASE + "?page=1": {"items": [1], "next": BASE + "?page=2"},
        BASE + "?page=2": {"items": [2], "next": BASE + "?page=1"},
    })
    with pytest.raises(RuntimeError, match="loop"):
        fetch_all(client, BASE + "?page=1")
    assert len(asked) == 2, "Stop as soon as a URL would be fetched twice."


def test_a_page_that_links_to_itself():
    client, asked = client_for({BASE: {"items": [1], "next": BASE}})
    with pytest.raises(RuntimeError, match="loop"):
        fetch_all(client, BASE)
    assert len(asked) == 1


def test_too_many_pages():
    pages = {f"{BASE}?page={i}": {"items": [i], "next": f"{BASE}?page={i + 1}"} for i in range(1, 50)}
    client, asked = client_for(pages)
    with pytest.raises(RuntimeError, match="too many pages"):
        fetch_all(client, BASE + "?page=1", max_pages=10)
    assert len(asked) == 10


def test_error_status_names_the_status_and_url():
    client, _ = client_for({
        BASE + "?page=1": {"items": [1], "next": BASE + "?page=2"},
        BASE + "?page=2": (503, b"busy"),
    })
    with pytest.raises(RuntimeError) as e:
        fetch_all(client, BASE + "?page=1")
    assert "503" in str(e.value) and "page=2" in str(e.value), "The message must contain the status code and the URL."


def test_bad_bodies():
    client, _ = client_for({BASE: (200, b"<html>not json</html>")})
    with pytest.raises(RuntimeError):
        fetch_all(client, BASE)
    client, _ = client_for({BASE: {"results": [1]}})
    with pytest.raises(RuntimeError):
        fetch_all(client, BASE)
