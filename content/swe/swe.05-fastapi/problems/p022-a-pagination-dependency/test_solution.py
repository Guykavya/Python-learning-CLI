import pytest
from fastapi.testclient import TestClient

from solution import Page, app, page_params


@pytest.fixture
def client():
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()


def test_defaults(client):
    body = client.get("/tasks").json()
    assert body["limit"] == 10 and body["offset"] == 0, f"Defaults are limit=10, offset=0; got {body.get('limit')}, {body.get('offset')}"
    assert body["items"] == [f"task {i}" for i in range(1, 11)], f"Without parameters return the first 10 tasks; got {body['items']}"
    assert body["total"] == 25, f"total is the length of the whole list (25), not of the page; got {body['total']}"


def test_limit_and_offset(client):
    assert client.get("/users?limit=3&offset=10").json() == {"items": ["user 11", "user 12"], "total": 12, "limit": 3, "offset": 10}, (
        "users[10:13] has only two items left; slice with data[offset:offset + limit].")


def test_offset_past_the_end_is_empty(client):
    assert client.get("/tags?offset=50").json() == {"items": [], "total": 5, "limit": 10, "offset": 50}, (
        "An offset past the end is not an error: it gives an empty page.")


@pytest.mark.parametrize("path", ["/tasks", "/users", "/tags"])
def test_every_endpoint_paginates(client, path):
    body = client.get(path + "?limit=2&offset=1").json()
    assert len(body["items"]) == 2 and body["limit"] == 2 and body["offset"] == 1, (
        f"{path} must use the Pagination dependency too; got {body}")


@pytest.mark.parametrize("query, loc, kind", [
    ("limit=0", ["query", "limit"], "greater_than_equal"),
    ("limit=101", ["query", "limit"], "less_than_equal"),
    ("offset=-1", ["query", "offset"], "greater_than_equal"),
    ("limit=ten", ["query", "limit"], "int_parsing"),
])
@pytest.mark.parametrize("path", ["/tasks", "/users", "/tags"])
def test_bad_values_are_422(client, path, query, loc, kind):
    r = client.get(f"{path}?{query}")
    assert r.status_code == 422, f"{path}?{query} must be rejected with 422, got {r.status_code}"
    got = [(e["loc"], e["type"]) for e in r.json()["detail"]]
    assert got == [(loc, kind)], (
        f"{path}?{query}: expected one error at {loc} of type {kind!r}, got {got}. "
        "Put the rules on page_params with Annotated[int, Query(ge=..., le=...)].")


def test_limit_100_is_allowed(client):
    assert client.get("/tasks?limit=100").json()["limit"] == 100, "100 is the largest allowed limit (le=100, not lt=100)."


def test_one_source_of_truth(client):
    app.dependency_overrides[page_params] = lambda: Page(limit=1, offset=2)
    for path, first in (("/tasks", "task 3"), ("/users", "user 3"), ("/tags", "urgent")):
        body = client.get(path).json()
        assert body["items"] == [first] and body["limit"] == 1, (
            f"After overriding page_params, {path} returned {body}. Every endpoint must get its page from "
            "Depends(page_params) (through the Pagination alias), not read limit/offset itself.")
