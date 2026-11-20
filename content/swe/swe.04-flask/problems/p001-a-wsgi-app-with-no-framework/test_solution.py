from wsgiref.util import setup_testing_defaults

from solution import app


def call(path, query=""):
    environ = {"REQUEST_METHOD": "GET", "PATH_INFO": path, "QUERY_STRING": query}
    setup_testing_defaults(environ)
    seen = {}

    def start_response(status, headers, exc_info=None):
        seen["status"] = status
        seen["headers"] = headers

    chunks = app(environ, start_response)
    assert "status" in seen, "Call start_response(status, headers) before you return the body."
    body = b"".join(chunks)
    return seen["status"], dict(seen["headers"]), body, chunks


def test_hello_with_name():
    status, headers, body, _ = call("/hello", "name=Asha")
    assert status == "200 OK", f"status must be the string '200 OK', got {status!r}"
    assert body == b"Hello, Asha", f"body should be b'Hello, Asha', got {body!r}"


def test_hello_default_name():
    _, _, body, _ = call("/hello")
    assert body == b"Hello, world", "Without ?name= the greeting is 'Hello, world'."


def test_query_is_url_decoded():
    _, _, body, _ = call("/hello", "name=Asha%20K")
    assert body == b"Hello, Asha K", "Decode the query string with urllib.parse.parse_qs (it turns %20 into a space)."


def test_other_query_parameters_are_ignored():
    _, _, body, _ = call("/hello", "x=1&name=Ravi&y=2")
    assert body == b"Hello, Ravi"


def test_unknown_path_is_404():
    status, _, body, _ = call("/nothing")
    assert status == "404 Not Found", f"unknown paths answer '404 Not Found', got {status!r}"
    assert body == b"Not Found"


def test_trailing_slash_is_a_different_path():
    status, _, _, _ = call("/hello/")
    assert status.startswith("404"), "A bare WSGI app does no slash handling: '/hello/' is not '/hello'."


def test_body_is_an_iterable_of_bytes():
    _, _, _, chunks = call("/hello", "name=Asha")
    assert not isinstance(chunks, (str, bytes)), "Return a list of bytes ([body]), not a bare str or bytes."
    assert all(isinstance(c, bytes) for c in chunks), "WSGI bodies are bytes: call .encode('utf-8')."


def test_headers():
    _, headers, body, _ = call("/hello", "name=Zoë")
    assert body == "Hello, Zoë".encode("utf-8")
    assert headers.get("Content-Type", "").startswith("text/plain"), "Send a Content-Type header (text/plain; charset=utf-8)."
    assert headers.get("Content-Length") == str(len(body)), (
        f"Content-Length must count BYTES: {len(body)} for this body, got {headers.get('Content-Length')!r}.")
