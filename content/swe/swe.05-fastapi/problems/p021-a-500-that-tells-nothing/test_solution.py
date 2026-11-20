import logging

import pytest
from fastapi.testclient import TestClient

from solution import create_app


def make_client(ids=None):
    if ids is None:
        return TestClient(create_app(), raise_server_exceptions=False)
    it = iter(ids)
    return TestClient(create_app(new_id=lambda: next(it)), raise_server_exceptions=False)


def json_of(r):
    assert r.headers.get("content-type", "").startswith("application/json"), (
        f"The 500 must be JSON; got {r.headers.get('content-type')!r} with body {r.text!r}. "
        "Register a handler with @app.exception_handler(Exception).")
    return r.json()


def test_crash_gives_the_generic_envelope():
    with make_client(["req-42"]) as client:
        r = client.get("/report")
    assert r.status_code == 500, f"An unhandled exception is still a 500, got {r.status_code}"
    assert json_of(r) == {"error": {"code": "internal_error", "message": "Internal server error", "request_id": "req-42"}}, (
        f"Got {r.text}. Use exactly this envelope and the id from new_id().")
    assert r.headers.get("x-request-id") == "req-42", f"Send the id in an X-Request-ID header too; got {r.headers.get('x-request-id')!r}"


@pytest.mark.parametrize("path", ["/report", "/ratio?a=1&b=0"])
def test_the_client_learns_nothing_inside(path):
    with make_client(["req-1"]) as client:
        r = client.get(path)
    text = r.text
    for secret in ("hunter2", "password", "RuntimeError", "ZeroDivisionError", "division", "Traceback", "File "):
        assert secret not in text, f"The response body leaks {secret!r}: {text!r}. Never put str(exc) or the traceback in a 500."


def test_the_log_has_the_id_the_request_and_the_traceback(caplog):
    caplog.set_level(logging.ERROR, logger="tasks_api")
    with make_client(["req-7"]) as client:
        client.get("/report")
    records = [rec for rec in caplog.records if rec.name == "tasks_api" and rec.levelno >= logging.ERROR]
    assert len(records) == 1, (
        f"Log exactly one ERROR record on the 'tasks_api' logger per crash; found {len(records)}. "
        "Use logging.getLogger('tasks_api').error(...).")
    rec = records[0]
    message = rec.getMessage()
    assert "req-7" in message, f"The log message must contain the request id so support can find it; got {message!r}"
    assert "GET" in message and "/report" in message, f"The log message must name the method and the path; got {message!r}"
    assert rec.exc_info and rec.exc_info[0] is RuntimeError, (
        "The record has no traceback. In an exception handler you are not inside 'except', so logger.exception() "
        "finds nothing: pass exc_info=exc.")
    assert "hunter2" in str(rec.exc_info[1]), "The log keeps the full original exception, message included."


def test_default_ids_are_fresh_each_time():
    with make_client() as client:
        a = json_of(client.get("/report"))["error"]["request_id"]
        b = json_of(client.get("/report"))["error"]["request_id"]
    assert isinstance(a, str) and len(a) >= 8, f"Without new_id, make a random id of at least 8 characters; got {a!r}"
    assert a != b, f"Each crash needs its own id; got {a!r} twice. Call the id function inside the handler, not once at start."


def test_http_errors_are_not_turned_into_500(caplog):
    caplog.set_level(logging.ERROR, logger="tasks_api")
    with make_client(["unused"]) as client:
        r = client.get("/tasks/9")
    assert r.status_code == 404 and r.json() == {"detail": "Task not found"}, (
        f"An HTTPException is a planned answer, not a crash; got {r.status_code} {r.text}")
    assert not [rec for rec in caplog.records if rec.name == "tasks_api"], "Nothing should be logged for a normal 404."


def test_validation_errors_are_untouched():
    with make_client(["unused"]) as client:
        r = client.get("/ratio?a=1&b=x")
    assert r.status_code == 422, f"A bad query is still a 422, got {r.status_code}"


def test_success_is_untouched():
    with make_client(["unused"]) as client:
        assert client.get("/ratio?a=6&b=3").json() == {"ratio": 2.0}
        assert client.get("/tasks/1").status_code == 200
