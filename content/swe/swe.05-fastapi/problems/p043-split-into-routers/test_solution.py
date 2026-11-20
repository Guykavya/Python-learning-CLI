import pytest
from fastapi.testclient import TestClient

import solution
from solution import app, require_user, tasks_router

USER = {"X-User": "asha"}


@pytest.fixture
def client():
    solution.TASKS.clear()
    with TestClient(app) as c:
        yield c
    solution.TASKS.clear()


def test_health_needs_no_login(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json() == {"status": "ok"}, f"GET /health must stay public, got {r.status_code}"


@pytest.mark.parametrize("method,url", [("GET", "/api/tasks"), ("GET", "/api/tasks/1"), ("POST", "/api/tasks")])
def test_every_task_route_needs_a_user(client, method, url):
    client.post("/api/tasks", json={"title": "seed"}, headers=USER)
    r = client.request(method, url, json={"title": "x"})
    assert r.status_code == 401, (
        f"{method} {url} without X-User must be 401, got {r.status_code}. "
        "Put dependencies=[Depends(require_user)] on tasks_router so EVERY route in it is protected.")


def test_the_flow_with_a_user(client):
    r = client.post("/api/tasks", json={"title": "write"}, headers=USER)
    assert r.status_code == 201 and r.json() == {"id": 1, "title": "write"}, f"POST /api/tasks: got {r.status_code} {r.text}"
    client.post("/api/tasks", json={"title": "test"}, headers=USER)
    assert client.get("/api/tasks", headers=USER).json() == [{"id": 1, "title": "write"}, {"id": 2, "title": "test"}]
    assert client.get("/api/tasks/2", headers=USER).json() == {"id": 2, "title": "test"}
    assert client.get("/api/tasks/9", headers=USER).status_code == 404


def test_auth_runs_before_body_validation(client):
    r = client.post("/api/tasks", json={"title": ""})
    assert r.status_code == 401, (
        f"Without a user, even a bad body must give 401 (got {r.status_code}): the router dependency is checked first.")
    r = client.post("/api/tasks", json={"title": ""}, headers=USER)
    assert r.status_code == 422, "With a user, an empty title is a 422 (min_length=1)."


def test_old_paths_are_gone(client):
    assert client.get("/tasks", headers=USER).status_code == 404, (
        "/tasks must not exist any more: include tasks_router with prefix='/api' and remove the old @app routes.")


def test_openapi_paths_and_tags():
    spec = app.openapi()
    assert sorted(spec["paths"]) == ["/api/tasks", "/api/tasks/{task_id}", "/health"], (
        f"Final paths are {sorted(spec['paths'])}; expected /health, /api/tasks, /api/tasks/{{task_id}}.")
    for path in ("/api/tasks", "/api/tasks/{task_id}"):
        for method, operation in spec["paths"][path].items():
            assert operation.get("tags") == ["tasks"], f"{method.upper()} {path} must have tags ['tasks'] (set on the router)."
    assert spec["paths"]["/health"]["get"].get("tags") == ["meta"], "GET /health must have the tag 'meta'."


def test_the_check_lives_on_the_router():
    deps = [d.dependency for d in tasks_router.dependencies]
    assert deps == [require_user], (
        f"tasks_router.dependencies holds {deps}; expected [require_user] once, on the router itself.")
    assert tasks_router.prefix == "/tasks", f"tasks_router.prefix must be '/tasks', got {tasks_router.prefix!r}"
