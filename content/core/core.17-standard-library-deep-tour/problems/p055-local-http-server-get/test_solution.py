import json
import socket
import threading
from http.server import HTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from solution import get_json, post_json, start_server, stop_server


@pytest.fixture(autouse=True)
def no_proxy(monkeypatch):
    # A proxy setting on your computer must never send these local requests elsewhere.
    for name in ("http_proxy", "HTTP_PROXY", "https_proxy", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("no_proxy", "127.0.0.1,localhost")
    monkeypatch.setenv("NO_PROXY", "127.0.0.1,localhost")


@pytest.fixture
def running():
    store = {"lang": "python", "n": 3}
    server, thread, base = start_server(store)
    try:
        yield server, thread, base, store
    finally:
        if thread.is_alive():
            server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def raw(url, data=None, method="GET"):
    """Plain urllib call used to look at the server's answers directly."""
    req = Request(url, data=data, method=method)
    try:
        with urlopen(req, timeout=5) as resp:
            return resp.status, resp.headers.get("Content-Type"), resp.read()
    except HTTPError as err:
        with err:
            return err.code, err.headers.get("Content-Type"), err.read()


def test_start_server_shape(running):
    server, thread, base, _ = running
    assert isinstance(server, HTTPServer), "start_server must return an http.server.HTTPServer first."
    host, port = server.server_address[:2]
    assert host == "127.0.0.1", "Bind to 127.0.0.1 only (this computer), never to '' or 0.0.0.0."
    assert port != 0, "Port 0 asks the OS for a free port; read the real one from server.server_address[1]."
    assert base == f"http://127.0.0.1:{port}", "The base URL is http://127.0.0.1:<port> with no trailing '/'."
    assert thread.daemon and thread.is_alive(), "serve_forever must run in a STARTED daemon thread."


def test_get_existing_raw(running):
    _, _, base, _ = running
    status, ctype, body = raw(base + "/items/lang")
    assert status == 200, "GET /items/lang must answer 200."
    assert ctype == "application/json", "Send the header Content-Type: application/json."
    assert json.loads(body) == {"key": "lang", "value": "python"}, "The body is the JSON {'key': key, 'value': value}."


def test_get_json(running):
    _, _, base, _ = running
    assert get_json(base + "/items/lang") == (200, {"key": "lang", "value": "python"}), (
        "get_json returns (status, decoded JSON body)."
    )
    assert get_json(base + "/items/n") == (200, {"key": "n", "value": 3}), "Values keep their JSON type (3 stays an int)."


def test_get_missing_is_404_not_exception(running):
    _, _, base, _ = running
    assert get_json(base + "/items/nope") == (404, {"error": "not found"}), (
        "A missing key answers 404 with {'error': 'not found'}. urlopen RAISES HTTPError for 404: catch it in get_json "
        "and return (err.code, JSON of err.read())."
    )


def test_unknown_paths(running):
    _, _, base, _ = running
    assert get_json(base + "/") == (404, {"error": "not found"}), "Any other path: 404."
    assert get_json(base + "/items/") == (404, {"error": "not found"}), "'/items/' has no key: 404."
    assert get_json(base + "/health") == (200, {"status": "ok"}), "GET /health answers {'status': 'ok'}."


def test_query_string_ignored(running):
    _, _, base, _ = running
    assert get_json(base + "/items/lang?x=1&y=2") == (200, {"key": "lang", "value": "python"}), (
        "self.path includes the query string: use urlsplit(self.path).path before finding the key."
    )


def test_post_stores_value(running):
    _, _, base, store = running
    assert post_json(base + "/items/year", {"value": 2025}) == (201, {"key": "year", "value": 2025}), (
        "POST answers 201 Created with the stored key and value."
    )
    assert store["year"] == 2025, "The value must be stored in server.store: the same dict that was given to start_server."
    assert get_json(base + "/items/year") == (200, {"key": "year", "value": 2025}), "A stored value can be read back."


def test_post_overwrite_and_nested(running):
    _, _, base, store = running
    post_json(base + "/items/lang", {"value": {"name": "Python", "tags": ["fast", "fun"]}})
    assert store["lang"] == {"name": "Python", "tags": ["fast", "fun"]}, "POST overwrites, and any JSON value is allowed."


def test_post_bad_requests(running):
    _, _, base, store = running
    status, ctype, body = raw(base + "/items/x", data=b"not json", method="POST")
    assert (status, json.loads(body)) == (400, {"error": "bad request"}), "A body that is not JSON: 400 {'error': 'bad request'}."
    assert ctype == "application/json", "Error answers are JSON too."
    assert post_json(base + "/items/x", {"val": 1}) == (400, {"error": "bad request"}), "A JSON body without 'value': 400."
    assert post_json(base + "/items/x", [1, 2]) == (400, {"error": "bad request"}), "A JSON list is not an object with 'value': 400."
    assert "x" not in store, "A bad request must not store anything."


def test_percent_encoded_key(running):
    _, _, base, store = running
    assert post_json(base + "/items/my%20key", {"value": "v"})[0] == 201, "POST to /items/my%20key must work."
    assert "my key" in store, "Decode the key with urllib.parse.unquote: %20 is a space."


def test_client_timeout():
    # A socket that accepts connections but never answers: without a timeout the client would wait forever.
    silent = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    silent.bind(("127.0.0.1", 0))
    silent.listen(1)
    url = f"http://127.0.0.1:{silent.getsockname()[1]}/items/x"
    outcome = []

    def call():
        try:
            outcome.append(("returned", get_json(url, timeout=0.5)))
        except Exception as exc:  # noqa: BLE001 - we inspect it below
            outcome.append(("raised", exc))

    worker = threading.Thread(target=call, daemon=True)
    try:
        worker.start()
        worker.join(timeout=6)
        assert not worker.is_alive(), "get_json kept waiting for a server that never answers: pass timeout=timeout to urlopen."
    finally:
        silent.close()
    kind, value = outcome[0]
    assert kind == "raised" and isinstance(value, OSError), (
        "A timeout must surface as an exception (TimeoutError / URLError), not as a normal result."
    )


def test_stop_server():
    server, thread, base = start_server({"a": 1})
    try:
        assert get_json(base + "/items/a")[0] == 200, "The server must work before it is stopped."
        stop_server(server, thread)
        assert not thread.is_alive(), "After stop_server the serving thread must have finished: call server.shutdown() and join the thread."
        with pytest.raises(OSError):
            get_json(base + "/items/a", timeout=5)
    finally:
        if thread.is_alive():
            server.shutdown()
        server.server_close()
        thread.join(timeout=5)
