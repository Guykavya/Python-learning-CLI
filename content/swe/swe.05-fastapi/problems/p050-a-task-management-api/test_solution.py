import json

import anyio
import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from solution import Settings, create_app

PASSWORD = "password123"


# ---------------------------------------------------------------- helpers and fixtures

def receive_json(ws, seconds=2.0):
    """ws.receive_json(), but fail with a clear message instead of waiting forever."""
    stream = getattr(ws, "_send_rx", None)          # the test session's message stream (Starlette 1.x)
    if stream is None:
        return ws.receive_json()

    async def _get():
        with anyio.fail_after(seconds):
            return await stream.receive()

    try:
        message = ws.portal.call(_get)
    except TimeoutError:
        raise AssertionError(f"No WebSocket message within {seconds} s: did the endpoint broadcast to the team's room?") from None
    if message["type"] == "websocket.close":
        raise AssertionError(f"The server closed the socket (code {message.get('code')}) instead of sending an event.")
    return json.loads(message["text"])


@pytest.fixture
def client():
    settings = Settings(database_url="sqlite+aiosqlite://", secret_key="t" * 40)     # in-memory, fresh per test
    with TestClient(create_app(settings)) as c:
        yield c


@pytest.fixture
def signup(client):
    def _signup(name):
        email = f"{name}@example.com"
        r = client.post("/auth/register", json={"email": email, "name": name, "password": PASSWORD})
        assert r.status_code == 201, f"POST /auth/register must answer 201, got {r.status_code} {r.text[:200]}"
        r = client.post("/auth/login", json={"email": email, "password": PASSWORD})
        assert r.status_code == 200, f"POST /auth/login with the right password must answer 200, got {r.status_code} {r.text[:200]}"
        token = r.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}, token
    return _signup


@pytest.fixture
def team(client, signup):
    """Asha owns team 'Core', Ben is a member, Cara is an outsider. Returns (team_id, asha, ben, cara)."""
    asha, ben, cara = signup("asha"), signup("ben"), signup("cara")
    r = client.post("/teams", json={"name": "Core"}, headers=asha[0])
    assert r.status_code == 201, f"POST /teams must answer 201, got {r.status_code} {r.text[:200]}"
    team_id = r.json()["id"]
    r = client.post(f"/teams/{team_id}/members", json={"email": "ben@example.com"}, headers=asha[0])
    assert r.status_code == 201, f"The owner adds a member: expected 201, got {r.status_code} {r.text[:200]}"
    return team_id, asha, ben, cara


def error_of(response):
    body = response.json()
    assert set(body) == {"error"} and {"code", "message"} <= set(body["error"]), (
        f"Every error must use the envelope {{'error': {{'code': ..., 'message': ...}}}}, got {body}")
    return body["error"]


# ---------------------------------------------------------------- users

def test_register_and_login(client):
    r = client.post("/auth/register", json={"email": "A@Example.com", "name": "A", "password": PASSWORD})
    assert r.status_code == 201
    assert set(r.json()) == {"id", "email", "name"}, f"UserOut exposes only id, email, name (never the hash), got {set(r.json())}"
    assert r.json()["email"] == "a@example.com", "Emails are stored in lower case."
    r = client.post("/auth/register", json={"email": "a@example.com", "name": "B", "password": PASSWORD})
    assert r.status_code == 409 and error_of(r)["code"] == "conflict", "A second account with the same email is 409 'conflict'."
    r = client.post("/auth/login", json={"email": "a@example.com", "password": "wrong-password"})
    assert r.status_code == 401 and error_of(r)["code"] == "unauthorized"
    r = client.post("/auth/login", json={"email": "A@EXAMPLE.COM", "password": PASSWORD})
    assert r.status_code == 200 and r.json()["token_type"] == "bearer" and r.json()["access_token"].count(".") == 2, (
        "Login returns {'access_token': <a JWT>, 'token_type': 'bearer'}; the email is matched case-insensitively.")


def test_missing_or_bad_token_is_401_with_the_envelope(client):
    for headers in ({}, {"Authorization": "Bearer garbage"}):
        r = client.get("/teams", headers=headers)
        assert r.status_code == 401, f"GET /teams with {headers or 'no header'} must be 401, got {r.status_code}"
        assert error_of(r)["code"] == "unauthorized"
        assert r.headers.get("www-authenticate") == "Bearer", (
            "Keep the WWW-Authenticate: Bearer header: pass exc.headers on in your HTTPException handler.")


# ---------------------------------------------------------------- the full flow

def test_full_flow(client, team):
    team_id, asha, ben, cara = team
    assert [t["name"] for t in client.get("/teams", headers=ben[0]).json()] == ["Core"], "GET /teams lists the teams I belong to."
    assert client.get("/teams", headers=cara[0]).json() == [], "Cara belongs to no team."
    url = f"/teams/{team_id}/tasks"
    created = [client.post(url, json={"title": f"task {i}"}, headers=ben[0]) for i in range(5)]
    assert all(r.status_code == 201 for r in created), "Members create tasks: 201."
    first = created[0].json()
    assert first["status"] == "todo" and first["team_id"] == team_id and first["assignee_id"] is None
    page = client.get(url, params={"limit": 2, "offset": 2}, headers=asha[0]).json()
    assert page["total"] == 5 and [t["title"] for t in page["items"]] == ["task 2", "task 3"], (
        f"limit=2&offset=2 must give tasks 2 and 3 of 5 (ordered by id), got {page}")
    task_id = page["items"][0]["id"]
    assert client.get(f"{url}/{task_id}", headers=ben[0]).json()["title"] == "task 2", "GET one task by id."
    r = client.patch(f"{url}/{task_id}", json={"status": "done"}, headers=asha[0])
    assert r.status_code == 200 and r.json()["status"] == "done" and r.json()["title"] == "task 2", (
        "PATCH changes only the fields that were sent (model_dump(exclude_unset=True)).")
    assert client.get(url, params={"status": "done"}, headers=asha[0]).json()["total"] == 1, "?status=done filters."
    r = client.patch(f"{url}/{task_id}", json={"assignee_id": 999}, headers=asha[0])
    assert r.status_code == 422, "An assignee who is not a member of the team is refused with 422."
    assert client.delete(f"{url}/{task_id}", headers=asha[0]).status_code == 204, "The owner may delete any task."
    assert client.get(f"{url}/{task_id}", headers=asha[0]).status_code == 404, "A deleted task is gone."


def test_delete_rules_and_owner_rules(client, team):
    team_id, asha, ben, cara = team
    url = f"/teams/{team_id}/tasks"
    ashas = client.post(url, json={"title": "a"}, headers=asha[0]).json()["id"]
    bens = client.post(url, json={"title": "b"}, headers=ben[0]).json()["id"]
    r = client.delete(f"{url}/{ashas}", headers=ben[0])
    assert r.status_code == 403 and error_of(r)["code"] == "forbidden", "A member may not delete someone else's task: 403."
    assert client.delete(f"{url}/{bens}", headers=ben[0]).status_code == 204, "The creator may delete their task."
    r = client.post(f"/teams/{team_id}/members", json={"email": "cara@example.com"}, headers=ben[0])
    assert r.status_code == 403, "Only the owner adds members: a plain member gets 403."


# ---------------------------------------------------------------- privacy

def test_outsider_gets_404_everywhere(client, team):
    team_id, asha, ben, cara = team
    url = f"/teams/{team_id}/tasks"
    task_id = client.post(url, json={"title": "secret"}, headers=asha[0]).json()["id"]
    attempts = [
        ("GET", url, None), ("POST", url, {"title": "x"}), ("GET", f"{url}/{task_id}", None),
        ("PATCH", f"{url}/{task_id}", {"title": "hacked"}), ("DELETE", f"{url}/{task_id}", None),
        ("POST", f"/teams/{team_id}/members", {"email": "cara@example.com"}),
    ]
    for method, path, body in attempts:
        r = client.request(method, path, json=body, headers=cara[0])
        assert r.status_code == 404, (
            f"{method} {path} by an outsider must be 404 (not 403, not 200): a team is invisible to non-members. Got {r.status_code}")
        assert error_of(r)["code"] == "not_found"
    assert client.get(f"{url}/{task_id}", headers=asha[0]).json()["title"] == "secret", "The outsider changed nothing."


def test_task_ids_do_not_cross_teams(client, team):
    team_id, asha, ben, cara = team
    task_id = client.post(f"/teams/{team_id}/tasks", json={"title": "secret"}, headers=asha[0]).json()["id"]
    other = client.post("/teams", json={"name": "Cara's"}, headers=cara[0]).json()["id"]
    for method, body in (("GET", None), ("PATCH", {"title": "hacked"}), ("DELETE", None)):
        r = client.request(method, f"/teams/{other}/tasks/{task_id}", json=body, headers=cara[0])
        assert r.status_code == 404, (
            f"{method} of another team's task through Cara's own team must be 404: look the task up with "
            "Task.id == task_id AND Task.team_id == team_id.")


# ---------------------------------------------------------------- errors and 422 shapes

def test_validation_errors_use_the_envelope(client, team):
    team_id, asha, ben, cara = team
    cases = [
        ("POST", "/auth/register", {"email": "x@example.com", "name": "X", "password": "short"}, None,
         ["body", "password"], "string_too_short"),
        ("POST", "/auth/register", {"email": "not-an-email", "name": "X", "password": PASSWORD}, None,
         ["body", "email"], "string_pattern_mismatch"),
        ("POST", f"/teams/{team_id}/tasks", {}, None, ["body", "title"], "missing"),
        ("GET", f"/teams/{team_id}/tasks", None, {"limit": 0}, ["query", "limit"], "greater_than_equal"),
        ("GET", "/teams/abc/tasks", None, None, ["path", "team_id"], "int_parsing"),
    ]
    for method, path, body, params, loc, kind in cases:
        r = client.request(method, path, json=body, params=params, headers=asha[0])
        assert r.status_code == 422, f"{method} {path} {body or params}: expected 422, got {r.status_code}"
        error = error_of(r)
        assert error["code"] == "validation_failed", f"422 errors use code 'validation_failed', got {error['code']!r}"
        details = error.get("details")
        assert isinstance(details, list) and details, "A validation error carries 'details': a list with one item per problem."
        found = [(d.get("loc"), d.get("type")) for d in details]
        assert (loc, kind) in found, (
            f"{method} {path}: expected a detail with loc {loc} and type {kind!r}, got {found}. "
            "Build details from exc.errors(): {'loc': list(e['loc']), 'type': e['type'], 'msg': e['msg']}.")


def test_unknown_routes_use_the_envelope(client):
    r = client.get("/no/such/route")
    assert r.status_code == 404 and error_of(r) == {"code": "not_found", "message": "Not Found"}, (
        "Register the handler for starlette's HTTPException so the router's own 404 uses the envelope too.")


# ---------------------------------------------------------------- real time

def test_websocket_receives_task_events(client, team):
    team_id, asha, ben, cara = team
    with client.websocket_connect(f"/ws/teams/{team_id}?token={asha[1]}") as ws:
        task = client.post(f"/teams/{team_id}/tasks", json={"title": "ship"}, headers=ben[0]).json()
        assert receive_json(ws) == {"event": "task.created", "task": task}, (
            "After POST, the team's sockets receive {'event': 'task.created', 'task': <the same JSON as the response>}.")
        client.patch(f"/teams/{team_id}/tasks/{task['id']}", json={"status": "doing"}, headers=ben[0])
        event = receive_json(ws)
        assert event["event"] == "task.updated" and event["task"]["status"] == "doing"
        client.delete(f"/teams/{team_id}/tasks/{task['id']}", headers=ben[0])
        assert receive_json(ws) == {"event": "task.deleted", "task_id": task["id"]}


def test_websocket_rejects_outsiders_and_bad_tokens(client, team):
    team_id, asha, ben, cara = team
    for token in (cara[1], "garbage", ""):
        with pytest.raises(WebSocketDisconnect) as info:
            with client.websocket_connect(f"/ws/teams/{team_id}?token={token}"):
                pass
        assert info.value.code == 1008, (
            f"token={token[:12]!r}: close with code 1008 BEFORE accept(), got {info.value.code}")


def test_events_stay_in_their_team(client, team, signup):
    team_id, asha, ben, cara = team
    other = client.post("/teams", json={"name": "Other"}, headers=cara[0]).json()["id"]
    with client.websocket_connect(f"/ws/teams/{other}?token={cara[1]}") as ws:
        client.post(f"/teams/{team_id}/tasks", json={"title": "core only"}, headers=asha[0])
        mine = client.post(f"/teams/{other}/tasks", json={"title": "mine"}, headers=cara[0]).json()
        event = receive_json(ws)
        assert event == {"event": "task.created", "task": mine}, (
            f"Cara's socket received {event}; events of team Core must not reach team Other's room.")


# ---------------------------------------------------------------- documentation

def test_openapi_lists_every_route(client):
    spec = client.get("/openapi.json").json()
    found = {f"{method.upper()} {path}" for path, ops in spec["paths"].items() for method in ops}
    expected = {
        "POST /auth/register", "POST /auth/login", "GET /health",
        "GET /teams", "POST /teams", "POST /teams/{team_id}/members",
        "GET /teams/{team_id}/tasks", "POST /teams/{team_id}/tasks",
        "GET /teams/{team_id}/tasks/{task_id}", "PATCH /teams/{team_id}/tasks/{task_id}",
        "DELETE /teams/{team_id}/tasks/{task_id}",
    }
    missing = sorted(expected - found)
    assert not missing, f"These routes are missing from the OpenAPI document: {missing}"
    post = spec["paths"]["/teams/{team_id}/tasks"]["post"]
    assert "201" in post["responses"], "POST /teams/{team_id}/tasks must document status 201 (status_code=201)."
    assert "password_hash" not in json.dumps(spec["components"]["schemas"].get("UserOut", {})), "UserOut must not contain the hash."


def test_missing_secret_stops_startup(monkeypatch):
    monkeypatch.delenv("APP_SECRET_KEY", raising=False)
    with pytest.raises(Exception) as info:
        create_app()
    assert "APP_SECRET_KEY" in str(info.value), (
        f"create_app() without settings reads the environment; a missing APP_SECRET_KEY must stop it with an error naming it, got {info.value!r}")
