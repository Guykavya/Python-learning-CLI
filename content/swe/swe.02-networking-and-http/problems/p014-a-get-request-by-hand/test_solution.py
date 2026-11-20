import json
import socket
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    """Quiet HTTP/1.1 handler base for the tests (loopback only)."""
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):
        pass

    def read_body(self):
        return self.rfile.read(int(self.headers.get("Content-Length", 0)))

    def reply(self, status, body=b"", headers=None, content_type="text/plain"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        if content_type:
            self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)


class Quiet(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        pass


@contextmanager
def serve(handler_class):
    server = Quiet(("127.0.0.1", 0), handler_class)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        yield "127.0.0.1", server.server_address[1]
    finally:
        server.shutdown()
        server.server_close()



from solution import http_get

SEEN = []


class H(Handler):
    def do_GET(self):
        SEEN.append((self.requestline, dict(self.headers)))
        if self.path.startswith("/missing"):
            self.reply(404, "not found", {"X-Test": "  spaced  "})
        elif self.path.startswith("/utf8"):
            self.reply(200, "héllo".encode("utf-8"), content_type="text/plain; charset=utf-8")
        elif self.path.startswith("/big"):
            self.reply(200, b"x" * 100_000, content_type="application/octet-stream")
        else:
            self.reply(200, "hi")


def test_200_and_the_body():
    SEEN.clear()
    with serve(H) as (host, port):
        status, headers, body = http_get(host, port, "/hello")
    assert status == 200 and isinstance(status, int), "The status must be an int."
    assert body == b"hi", f"Body should be b'hi', got {body!r}."
    assert headers["content-type"] == "text/plain" and headers["content-length"] == "2", (
        "Header names are lower-case, values stripped.")


def test_404_and_a_custom_header():
    with serve(H) as (host, port):
        status, headers, body = http_get(host, port, "/missing")
    assert status == 404 and body == b"not found"
    assert headers["x-test"] == "spaced", "Strip the spaces around header values."


def test_the_request_you_send():
    SEEN.clear()
    with serve(H) as (host, port):
        http_get(host, port, "/search?q=a%20b")
    line, headers = SEEN[0]
    assert line == "GET /search?q=a%20b HTTP/1.1", f"The request line was {line!r}: send the path unchanged."
    assert headers.get("Host") == f"127.0.0.1:{port}", "Host must be 'host:port'."
    assert headers.get("Connection", "").lower() == "close", "Ask the server to close with 'Connection: close'."


def test_body_is_bytes_not_text():
    with serve(H) as (host, port):
        status, headers, body = http_get(host, port, "/utf8")
    assert body == "héllo".encode("utf-8") and isinstance(body, bytes), "Return the body as bytes."


def test_a_response_that_arrives_in_many_pieces():
    with serve(H) as (host, port):
        status, headers, body = http_get(host, port, "/big")
    assert len(body) == 100_000, f"Got {len(body)} bytes of 100000: loop on recv until the connection closes."
