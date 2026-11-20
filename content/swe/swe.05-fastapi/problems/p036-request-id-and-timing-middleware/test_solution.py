import re

import pytest
from fastapi.testclient import TestClient

from solution import app

HEX32 = re.compile(r"[0-9a-f]{32}")
TIMING = re.compile(r"app;dur=\d+\.\d")


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_a_valid_incoming_id_is_reused(client):
    r = client.get("/ping", headers={"X-Request-ID": "order-42"})
    assert r.headers.get("x-request-id") == "order-42", (
        f"A valid incoming X-Request-ID must be echoed back unchanged, got {r.headers.get('x-request-id')!r}. "
        "Did you add the header in a middleware (@app.middleware('http'))?")
    assert r.json() == {"request_id": "order-42"}, (
        "The endpoint must see the same id: set request.state.request_id BEFORE await call_next(request).")


def test_a_missing_id_is_generated(client):
    first = client.get("/ping")
    second = client.get("/ping")
    rid = first.headers.get("x-request-id", "")
    assert HEX32.fullmatch(rid), f"Without an incoming id, create uuid.uuid4().hex (32 hex characters), got {rid!r}"
    assert first.json()["request_id"] == rid, "The endpoint and the response header must show the same generated id."
    assert second.headers["x-request-id"] != rid, "Every request needs a NEW id: generate it inside the middleware, not once at import."


@pytest.mark.parametrize("bad", ["<script>", "has space", "x" * 65, "a;b", "a/b"])
def test_an_invalid_incoming_id_is_replaced(client, bad):
    r = client.get("/ping", headers={"X-Request-ID": bad})
    rid = r.headers.get("x-request-id", "")
    assert rid != bad, f"The invalid id {bad!r} was echoed back: check it with VALID_ID.fullmatch before reusing it."
    assert HEX32.fullmatch(rid), f"An invalid id must be replaced by uuid.uuid4().hex, got {rid!r}"


def test_exactly_64_characters_is_still_valid(client):
    rid = "a" * 64
    assert client.get("/ping", headers={"X-Request-ID": rid}).headers.get("x-request-id") == rid, (
        "64 characters is the limit, not over it: {1,64} in the pattern.")


def test_server_timing_header(client):
    value = client.get("/ping").headers.get("server-timing", "")
    assert TIMING.fullmatch(value), (
        f"Server-Timing must look like 'app;dur=0.4' (milliseconds, one decimal: f'{{ms:.1f}}'), got {value!r}")


def test_unknown_paths_get_the_headers_too(client):
    r = client.get("/nowhere", headers={"X-Request-ID": "lost-1"})
    assert r.status_code == 404
    assert r.headers.get("x-request-id") == "lost-1", (
        "A 404 must carry the request id too: middleware wraps the router, so add the headers to whatever call_next returns.")
    assert TIMING.fullmatch(r.headers.get("server-timing", "")), "A 404 must carry Server-Timing too."
