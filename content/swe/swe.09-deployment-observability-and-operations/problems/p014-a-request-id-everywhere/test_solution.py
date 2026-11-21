import logging
import re

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from solution import RequestContext, request_id_var


@pytest.fixture
def app():
    app = FastAPI()
    app.add_middleware(RequestContext)

    @app.get("/who")
    def who():
        return {"id": request_id_var.get()}

    @app.get("/orders/{order_id}")
    def order(order_id: int):
        return {"id": order_id}

    @app.get("/boom")
    def boom():
        raise RuntimeError("simulated bug while building the invoice")

    @app.get("/healthz")
    def healthz():
        return {"status": "alive"}

    return app


@pytest.fixture
def client(app, caplog):
    caplog.set_level(logging.INFO, logger="pagebound")

    def tag(record):                                           # what is the request id at the moment the record is written?
        record.rid = request_id_var.get()
        return True

    caplog.handler.addFilter(tag)
    with TestClient(app) as c:
        yield c


def finished(caplog):
    return [r for r in caplog.records if r.getMessage() == "request finished"]


def test_generated_id_is_echoed(client):
    r = client.get("/orders/1")
    rid = r.headers.get("x-request-id", "")
    assert re.fullmatch(r"[0-9a-f]{32}", rid), f"Without an incoming id, make uuid.uuid4().hex (32 hex characters) and return it in X-Request-ID; got {rid!r}"
    assert client.get("/orders/1").headers["x-request-id"] != rid, "Every request gets its own id."


def test_valid_incoming_id_is_reused(client):
    assert client.get("/orders/1", headers={"X-Request-ID": "trace-me-0001"}).headers["x-request-id"] == "trace-me-0001", \
        "A valid incoming id (8 to 64 of A-Za-z0-9._-) is kept, so the id is the same from the first hop."


@pytest.mark.parametrize("bad", ["short", "bad id with spaces", "x" * 65, "semi;colon-id", "tab\there"])
def test_invalid_incoming_id_is_replaced(client, bad):
    got = client.get("/orders/1", headers={"X-Request-ID": bad}).headers["x-request-id"]
    assert got != bad and re.fullmatch(r"[0-9a-f]{32}", got), f"{bad!r} is not a valid id: replace it by a generated one, got {got!r}"


def test_the_id_is_visible_inside_the_handler(client):
    assert client.get("/who", headers={"X-Request-ID": "inside-the-app-1"}).json() == {"id": "inside-the-app-1"}, \
        "The handler must see the id in request_id_var (set it before calling the app)."


def test_the_variable_is_reset_afterwards():
    import asyncio

    async def inner_app(scope, receive, send):
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    async def scenario():
        request_id_var.set("outer-context-id")                  # whatever was set before the request must come back
        sent = []

        async def send(message):
            sent.append(message)

        async def receive():
            return {"type": "http.request"}

        scope = {"type": "http", "method": "GET", "path": "/x", "headers": [(b"x-request-id", b"inside-the-app-1")]}
        await RequestContext(inner_app)(scope, receive, send)
        return request_id_var.get(), sent

    value, sent = asyncio.run(scenario())
    assert (b"x-request-id", b"inside-the-app-1") in sent[0]["headers"], "The id header is added to the response start message."
    assert value == "outer-context-id", \
        "After the request the variable must have its previous value again: keep the token that set() returns and call request_id_var.reset(token)."


def test_unhandled_error_gives_the_client_only_the_id(client, caplog):
    r = client.get("/boom", headers={"X-Request-ID": "trace-me-0002"})
    assert r.status_code == 500
    assert r.json() == {"error": "internal error", "request_id": "trace-me-0002"}, f"Body must be exactly the error text and the id; got {r.text}"
    assert "simulated bug" not in r.text, "Internal details must not reach the client."
    assert r.headers["x-request-id"] == "trace-me-0002", "The error response carries the id header too."
    errors = [rec for rec in caplog.records if rec.levelno == logging.ERROR]
    assert len(errors) == 1 and errors[0].getMessage() == "unhandled error", "Log the exception once with log.exception('unhandled error')."
    assert errors[0].exc_info and "simulated bug" in str(errors[0].exc_info[1]), "The traceback must be in the log (exc_info)."
    assert errors[0].rid == "trace-me-0002", "The ERROR record must be written while the request id is set."


def test_one_access_line_per_request(client, caplog):
    client.get("/orders/7", headers={"X-Request-ID": "trace-me-0003"})
    lines = finished(caplog)
    assert len(lines) == 1, f"Exactly one 'request finished' record per request; got {len(lines)}"
    fields = lines[0].fields
    assert (fields["method"], fields["path"], fields["status"]) == ("GET", "/orders/7", 200), f"Fields method, path and status; got {fields}"
    assert isinstance(fields["duration_ms"], float) and fields["duration_ms"] >= 0, "duration_ms is a number of milliseconds."
    assert round(fields["duration_ms"], 1) == fields["duration_ms"], "Round duration_ms to one decimal."
    assert lines[0].rid == "trace-me-0003", "Write the line BEFORE resetting the variable, so it carries the request's id."


def test_status_is_the_status_that_was_sent(client, caplog):
    client.get("/nothing-here")
    client.get("/boom")
    statuses = [r.fields["status"] for r in finished(caplog)]
    assert statuses == [404, 500], f"A 404 is logged as 404 and an unhandled error as 500; got {statuses}"


def test_health_probes_are_not_logged(client, caplog):
    client.get("/healthz")
    assert finished(caplog) == [], "Do not log the paths in QUIET_PATHS."
    assert client.get("/healthz").headers["x-request-id"], "...but they still get a request id."


def test_non_http_scopes_pass_through(app):
    with TestClient(app) as c:                                  # entering the context runs the lifespan scope
        assert c.get("/orders/1").status_code == 200
