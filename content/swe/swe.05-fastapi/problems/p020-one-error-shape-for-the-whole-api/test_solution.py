import pytest
from fastapi.testclient import TestClient

from solution import NotFound, app


@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def error_of(r):
    assert r.headers.get("content-type", "").startswith("application/json"), (
        f"Errors must be JSON; got content-type {r.headers.get('content-type')!r} and body {r.text!r}. "
        "A plain-text 500 means an exception had no handler.")
    body = r.json()
    assert set(body) == {"error"}, f"The body must have exactly one key 'error'; got keys {sorted(body)}"
    assert set(body["error"]) == {"code", "message", "details"}, (
        f"'error' must have exactly code, message and details; got {sorted(body['error'])}. details is always present.")
    return body["error"]


def test_success_is_unchanged(client):
    r = client.get("/tasks/1")
    assert r.status_code == 200 and r.json() == {"id": 1, "title": "write chapter"}, "Handlers must not touch successful responses."


def test_domain_not_found_becomes_404(client):
    r = client.get("/tasks/7")
    assert r.status_code == 404, f"NotFound must become a 404 (got {r.status_code}). Register a handler for NotFound."
    assert error_of(r) == {"code": "not_found", "message": "Task 7 not found", "details": []}, f"Got {r.json()}"


def test_notfound_is_not_an_http_exception():
    from starlette.exceptions import HTTPException
    assert not issubclass(NotFound, HTTPException), "Keep NotFound a plain Exception: the business logic should not know about HTTP."


def test_http_exception_is_enveloped(client):
    r = client.delete("/tasks/1")
    assert r.status_code == 409, f"The status of the HTTPException must be kept (409), got {r.status_code}"
    assert error_of(r) == {"code": "http_error", "message": "Task is locked", "details": []}, f"Got {r.json()}"


def test_unknown_route_is_enveloped(client):
    r = client.get("/nowhere")
    assert r.status_code == 404
    assert error_of(r) == {"code": "http_error", "message": "Not Found", "details": []}, (
        f"Got {r.json()}. The automatic 404 is raised as Starlette's HTTPException: register the handler for "
        "starlette.exceptions.HTTPException, not fastapi.HTTPException.")


def test_wrong_method_is_enveloped(client):
    r = client.put("/secret")
    assert r.status_code == 405, f"PUT on a GET route is 405, got {r.status_code}"
    assert error_of(r)["code"] == "http_error" and error_of(r)["message"] == "Method Not Allowed", f"Got {r.json()}"


def test_http_exception_headers_are_kept(client):
    r = client.get("/secret")
    assert r.status_code == 401
    assert error_of(r)["message"] == "Login required"
    assert r.headers.get("www-authenticate") == "Bearer", (
        "The HTTPException carried headers={'WWW-Authenticate': 'Bearer'}; pass headers=getattr(exc, 'headers', None) "
        f"to the JSONResponse. Got headers {dict(r.headers)}")


def test_validation_error_keeps_loc_and_type(client):
    r = client.post("/tasks", json={"priority": 9})
    assert r.status_code == 422, f"Keep the status 422 for validation errors, got {r.status_code}"
    err = error_of(r)
    assert err["code"] == "validation_failed" and err["message"] == "Request data is invalid", f"Got {err}"
    got = [(d.get("loc"), d.get("type")) for d in err["details"]]
    assert got == [(["body", "title"], "missing"), (["body", "priority"], "less_than_equal")], (
        f"details must list each error with its full loc and its Pydantic type, in order; got {got}. "
        "Use list(e['loc']) and e['type'] from exc.errors().")
    for d in err["details"]:
        assert set(d) == {"loc", "type", "message"}, f"Each detail has loc, type and message; got {sorted(d)}"
        assert isinstance(d["message"], str) and d["message"], "message is the human text e['msg']."


def test_validation_error_in_the_path(client):
    r = client.get("/tasks/abc")
    err = error_of(r)
    assert r.status_code == 422
    assert [(d["loc"], d["type"]) for d in err["details"]] == [(["path", "task_id"], "int_parsing")], f"Got {err['details']}"


def test_valid_body_still_works(client):
    r = client.post("/tasks", json={"title": "x", "priority": 2})
    assert r.status_code == 201 and r.json()["title"] == "x"
