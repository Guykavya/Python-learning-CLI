import http.client
import json
import socket
import threading
import time

import httpx
import pytest

from solution import NotesClient, NotesServer, RequestFailed


def call(server, method, path, body=None, headers=None, conn=None):
    own = conn is None
    conn = conn or http.client.HTTPConnection("127.0.0.1", server.port, timeout=5)
    try:
        data = body if isinstance(body, (bytes, type(None))) else json.dumps(body).encode("utf-8")
        conn.request(method, path, body=data, headers=headers or {})
        r = conn.getresponse()
        raw = r.read()
        return r.status, {k.lower(): v for k, v in r.getheaders()}, (json.loads(raw) if raw else None)
    finally:
        if own:
            conn.close()


def test_server_basics():
    with NotesServer() as s:
        assert s.port > 0 and s.base == f"http://127.0.0.1:{s.port}"
        status, headers, body = call(s, "GET", "/notes")
        assert status == 200 and body == {"notes": []}
        assert headers["content-type"].startswith("application/json")


def test_create_list_get_over_one_keep_alive_connection():
    with NotesServer() as s:
        conn = http.client.HTTPConnection("127.0.0.1", s.port, timeout=5)
        try:
            st, h, body = call(s, "POST", "/notes", {"text": "buy tea"}, {"Content-Type": "application/json"}, conn)
            assert st == 201 and body == {"id": 1, "text": "buy tea"} and h["location"] == "/notes/1"
            st, h, body = call(s, "POST", "/notes", {"text": "second"}, conn=conn)
            assert body["id"] == 2
            st, h, body = call(s, "GET", "/notes", conn=conn)
            assert body == {"notes": [{"id": 1, "text": "buy tea"}, {"id": 2, "text": "second"}]}
            st, h, body = call(s, "GET", "/notes/2", conn=conn)
            assert st == 200 and body == {"id": 2, "text": "second"}
        finally:
            conn.close()
        assert s.connections == 1, f"All four requests used one connection, but the server counted {s.connections}: keep it alive."
        assert s.requests == 4


def test_content_length_counts_bytes():
    with NotesServer() as s:
        text = "héllo 😀 नमस्ते"
        st, h, body = call(s, "POST", "/notes", {"text": text})
        assert body["text"] == text
        st, h, body = call(s, "GET", "/notes/1")
        assert body["text"] == text, "Unicode must survive: Content-Length counts BYTES in both directions."


@pytest.mark.parametrize("payload", [b"{not json", b"[1, 2]", b'"text"', b"{}", b'{"text": ""}', b'{"text": "   "}', b'{"text": 5}', b"", b"null"])
def test_bad_bodies_are_400(payload):
    with NotesServer() as s:
        st, h, body = call(s, "POST", "/notes", payload)
        assert st == 400 and body["error"]["code"] == "bad-request", f"Body {payload!r} must give 400 and an error object."
        assert isinstance(body["error"]["message"], str)
        assert call(s, "GET", "/notes")[2] == {"notes": []}, "A bad POST must not create a note."


def test_404_and_405():
    with NotesServer() as s:
        call(s, "POST", "/notes", {"text": "x"})
        for path in ("/nothing", "/notes/abc", "/notes/", "/"):
            st, h, body = call(s, "GET", path)
            assert st == 404 and body["error"]["code"] == "not-found", f"GET {path} must be 404."
        assert call(s, "GET", "/notes/99")[0] == 404
        st, h, body = call(s, "DELETE", "/notes")
        assert st == 405 and h["allow"] == "GET, POST" and body["error"]["code"] == "method-not-allowed"
        st, h, body = call(s, "POST", "/notes/1", {"text": "y"})
        assert st == 405 and h["allow"] == "GET"
        st, h, body = call(s, "PUT", "/notes", {"text": "y"})
        assert st == 405


def test_malformed_requests_get_400_and_the_server_survives():
    with NotesServer() as s:
        for raw in (b"garbage\r\n\r\n", b"POST /notes HTTP/1.1\r\nHost: x\r\nContent-Length: abc\r\n\r\n",
                    b"POST /notes HTTP/1.1\r\nHost: x\r\nContent-Length: 99999999999\r\n\r\n"):
            with socket.create_connection(("127.0.0.1", s.port), timeout=5) as c:
                c.sendall(raw)
                data = b""
                while True:
                    chunk = c.recv(4096)
                    if not chunk:
                        break
                    data += chunk
            assert data.startswith(b"HTTP/1.1 400"), f"{raw!r} should get a 400 and then the connection is closed. Got {data[:40]!r}"
        assert call(s, "GET", "/notes")[0] == 200, "The server must still work after bad requests."


def test_connection_close_is_honoured():
    with NotesServer() as s:
        with socket.create_connection(("127.0.0.1", s.port), timeout=5) as c:
            c.sendall(b"GET /notes HTTP/1.1\r\nHost: x\r\nConnection: close\r\n\r\n")
            data = b""
            while True:
                chunk = c.recv(4096)
                if not chunk:
                    break
                data += chunk
        assert b"Connection: close" in data and data.startswith(b"HTTP/1.1 200"), "After 'Connection: close' the server closes."


def test_concurrent_clients_get_unique_ids():
    with NotesServer() as s:
        ids = []
        lock = threading.Lock()

        def worker(n):
            conn = http.client.HTTPConnection("127.0.0.1", s.port, timeout=10)
            try:
                for i in range(15):
                    st, h, body = call(s, "POST", "/notes", {"text": f"{n}-{i}"}, conn=conn)
                    with lock:
                        ids.append(body["id"])
            finally:
                conn.close()

        threads = [threading.Thread(target=worker, args=(n,)) for n in range(6)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert sorted(ids) == list(range(1, 91)), "Every note needs its own id: protect the counter with a lock."
        assert s.connections == 6


def test_leaving_the_with_block_stops_the_server():
    with NotesServer() as s:
        port = s.port
    time.sleep(0.5)
    with pytest.raises(OSError):
        socket.create_connection(("127.0.0.1", port), timeout=1).close()


# ---- the client ------------------------------------------------------------------------------------------------

class TopRng:
    def uniform(self, a, b):
        return b


def test_client_against_the_real_server():
    with NotesServer() as s, httpx.Client(base_url=s.base, timeout=5) as http:
        notes = NotesClient(http, sleep=lambda x: None, rng=TopRng())
        assert notes.create("buy tea") == {"id": 1, "text": "buy tea"}
        assert notes.create("write code", idempotency_key="k1")["id"] == 2
        assert notes.list_notes() == [{"id": 1, "text": "buy tea"}, {"id": 2, "text": "write code"}]
        assert notes.get_note(2) == {"id": 2, "text": "write code"}
        with pytest.raises(RequestFailed) as e:
            notes.get_note(99)
        assert e.value.status == 404 and e.value.attempts == 1, "A 404 is not retried."
        with pytest.raises(RequestFailed) as e:
            notes.create("   ")
        assert e.value.status == 400 and e.value.attempts == 1
        assert s.connections == 1, "httpx keeps the connection alive: one TCP connection for all of this."


def flaky(steps):
    seen = []

    def handler(request):
        step = steps[min(len(seen), len(steps) - 1)]
        seen.append(request)
        if isinstance(step, Exception):
            raise step
        return step

    return httpx.Client(base_url="http://notes.test", transport=httpx.MockTransport(handler)), seen


def test_get_survives_two_failures():
    client, seen = flaky([httpx.Response(503), httpx.Response(503), httpx.Response(200, json={"notes": [{"id": 1, "text": "a"}]})])
    waits = []
    assert NotesClient(client, sleep=waits.append, rng=TopRng()).list_notes() == [{"id": 1, "text": "a"}]
    assert len(seen) == 3, "Two failures and a success are three requests."
    assert waits == [0.5, 1.0]


def test_post_is_not_retried_without_a_key():
    client, seen = flaky([httpx.Response(503), httpx.Response(201, json={"id": 1, "text": "x"})])
    with pytest.raises(RequestFailed) as e:
        NotesClient(client, sleep=lambda s: None, rng=TopRng()).create("x")
    assert len(seen) == 1 and e.value.status == 503, "A POST without a key may have been processed: one request only."


def test_post_with_a_key_is_retried_with_the_same_key():
    client, seen = flaky([httpx.Response(503, headers={"Retry-After": "2"}), httpx.Response(201, json={"id": 1, "text": "x"})])
    waits = []
    out = NotesClient(client, sleep=waits.append, rng=TopRng()).create("x", idempotency_key="abc")
    assert out == {"id": 1, "text": "x"} and len(seen) == 2
    assert [r.headers["idempotency-key"] for r in seen] == ["abc", "abc"]
    assert waits == [2.0], "Retry-After wins over the random backoff."


def test_connect_errors_are_retried_even_for_post():
    req = httpx.Request("POST", "http://notes.test/notes")
    client, seen = flaky([httpx.ConnectError("refused", request=req), httpx.Response(201, json={"id": 1, "text": "x"})])
    assert NotesClient(client, sleep=lambda s: None, rng=TopRng()).create("x")["id"] == 1
    assert len(seen) == 2


def test_gives_up_after_four_attempts():
    client, seen = flaky([httpx.Response(502)])
    waits = []
    with pytest.raises(RequestFailed) as e:
        NotesClient(client, sleep=waits.append, rng=TopRng()).get_note(1)
    assert len(seen) == 4 and e.value.attempts == 4 and e.value.status == 502
    assert len(waits) == 3
