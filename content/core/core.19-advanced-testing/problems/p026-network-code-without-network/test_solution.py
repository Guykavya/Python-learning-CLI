import io
import socket
import urllib.error

import pytest

import solution
from solution import default_get, fetch_title

URL = "http://example.test/page"


class NetworkBlocked(AssertionError):
    pass


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Guard: any attempt to open a real socket or resolve a name is recorded and fails the test."""
    attempts = []

    def blocked(*args, **kwargs):
        attempts.append(args)
        raise NetworkBlocked("a real network call was attempted in a unit test")

    class BlockedSocket:
        def __init__(self, *args, **kwargs):
            blocked(*args)

    monkeypatch.setattr(socket, "socket", BlockedSocket)
    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.setattr(socket, "getaddrinfo", blocked)
    return attempts


def test_guard_blocks_the_real_default(no_network):
    with pytest.raises(NetworkBlocked):
        default_get(URL)
    assert no_network, (
        "default_get must go through urllib.request.urlopen; with the guard it must hit the blocked socket.")


def test_title_from_injected_client(no_network):
    calls = []

    def fake_get(url):
        calls.append(url)
        return 200, '{"title": "Hello", "id": 1}'

    assert fetch_title(URL, http_get=fake_get) == "Hello", "Return the value of the 'title' key."
    assert calls == [URL], "Call http_get exactly once, with the url."
    assert no_network == [], "No socket may be opened when a client is injected."


def test_404_gives_none():
    assert fetch_title(URL, http_get=lambda u: (404, "")) is None, "A 404 means 'no such page': return None."


@pytest.mark.parametrize("status", [201, 301, 500, 503])
def test_other_status_raises(status):
    with pytest.raises(RuntimeError, match=f"HTTP {status} for {URL}"):
        fetch_title(URL, http_get=lambda u: (status, "{}"))


def test_bad_json_raises_value_error():
    with pytest.raises(ValueError, match="bad JSON from"):
        fetch_title(URL, http_get=lambda u: (200, "<html>oops"))


def test_default_is_looked_up_at_call_time(monkeypatch):
    monkeypatch.setattr(solution, "default_get", lambda url: (200, '{"title": "patched"}'))
    assert fetch_title(URL) == "patched", (
        "When http_get is None, use the module-level default_get at call time "
        "(not as a default value in the signature, which is frozen at definition time).")


class FakeResponse:
    status = 200

    def __init__(self, body):
        self.body = body

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_default_get_reads_status_and_decodes_utf8(monkeypatch, no_network):
    seen = {}

    def fake_urlopen(url, *args, **kwargs):
        seen["url"] = url
        seen["kwargs"] = kwargs
        return FakeResponse("caf\u00e9".encode("utf-8"))

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    assert default_get(URL) == (200, "caf\u00e9"), (
        "default_get returns (status, body decoded as UTF-8). "
        "Call urllib.request.urlopen (not 'from urllib.request import urlopen').")
    assert seen["url"] == URL
    assert no_network == []


def test_default_get_turns_http_errors_into_a_status(monkeypatch):
    def fake_urlopen(url, *args, **kwargs):
        raise urllib.error.HTTPError(url, 404, "Not Found", {}, io.BytesIO(b""))

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    assert default_get(URL) == (404, ""), "An HTTPError is data: return (error.code, '') instead of raising."
