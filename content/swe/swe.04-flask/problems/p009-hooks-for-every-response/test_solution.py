import re

import pytest

from solution import create_app


@pytest.fixture
def client():
    return create_app({"TESTING": True}).test_client()


def test_generated_id(client):
    r = client.get("/whoami")
    body = r.get_data(as_text=True)
    assert re.fullmatch(r"[0-9a-f]{32}", body), f"Without a header the id is uuid4().hex (32 hex chars); the view returned {body!r}."
    assert r.headers["X-Request-ID"] == body, "The header and g.request_id must be the same value."


def test_ids_differ_between_requests(client):
    a = client.get("/whoami").get_data(as_text=True)
    b = client.get("/whoami").get_data(as_text=True)
    assert a != b, "Each request needs its own new id."


def test_valid_incoming_id_is_reused(client):
    r = client.get("/whoami", headers={"X-Request-ID": "abc-123_XYZ"})
    assert r.get_data(as_text=True) == "abc-123_XYZ"
    assert r.headers["X-Request-ID"] == "abc-123_XYZ"


@pytest.mark.parametrize("bad", ["bad id!", "has space", "x" * 65, "<script>", "a/b"])
def test_invalid_incoming_id_is_replaced(client, bad):
    r = client.get("/whoami", headers={"X-Request-ID": bad})
    body = r.get_data(as_text=True)
    assert body != bad and re.fullmatch(r"[0-9a-f]{32}", body), f"{bad!r} is not a valid id (1-64 of A-Za-z0-9_-): generate a new one."
    assert r.headers["X-Request-ID"] == body


def test_security_headers(client):
    r = client.get("/whoami")
    assert r.headers["X-Content-Type-Options"] == "nosniff", "Add X-Content-Type-Options: nosniff in after_request."
    assert r.headers["X-Frame-Options"] == "DENY", "Add X-Frame-Options: DENY in after_request."


def test_error_pages_get_the_headers_too(client):
    r = client.get("/missing", headers={"X-Request-ID": "trace-9"})
    assert r.status_code == 404
    assert r.headers.get("X-Request-ID") == "trace-9", "after_request also runs for 404 pages; before_request ran too, so g has the id."
    assert r.headers.get("X-Frame-Options") == "DENY"
    r = client.post("/whoami")
    assert r.status_code == 405 and r.headers.get("X-Content-Type-Options") == "nosniff", "405 responses need the headers as well."


def test_after_request_returns_the_response(client):
    r = client.get("/whoami")
    assert r.status_code == 200 and r.get_data(as_text=True), "The after_request function must return the response object."
