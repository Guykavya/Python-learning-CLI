import inspect

from fastapi.testclient import TestClient

from solution import create_app, get_session


def url_for(path):
    return "sqlite+aiosqlite:///" + path.as_posix()


def test_get_session_is_an_async_generator():
    assert inspect.isasyncgenfunction(get_session), (
        "get_session must be 'async def' with 'yield' inside 'async with ...sessionmaker() as session'.")


def test_create_list_and_get(tmp_path):
    app = create_app(url_for(tmp_path / "one.db"))
    with TestClient(app) as client:
        r = client.post("/tasks", json={"title": "write tests"})
        assert r.status_code == 201, f"Creating a task answers 201, got {r.status_code}: {r.text}"
        assert r.json() == {"id": 1, "title": "write tests", "done": False}, f"Got {r.json()}"
        assert client.post("/tasks", json={"title": "ship", "done": True}).json() == {"id": 2, "title": "ship", "done": True}
        assert client.get("/tasks").json() == [
            {"id": 1, "title": "write tests", "done": False},
            {"id": 2, "title": "ship", "done": True},
        ], "GET /tasks lists every stored task ordered by id."
        assert client.get("/tasks/2").json() == {"id": 2, "title": "ship", "done": True}


def test_missing_task_is_404(tmp_path):
    with TestClient(create_app(url_for(tmp_path / "t.db"))) as client:
        r = client.get("/tasks/9")
    assert r.status_code == 404 and r.json() == {"detail": "Task not found"}, (
        f"Got {r.status_code} {r.text}. session.get(Task, id) returns None when the row is missing.")


def test_validation(tmp_path):
    with TestClient(create_app(url_for(tmp_path / "t.db"))) as client:
        r = client.post("/tasks", json={"title": ""})
        assert r.status_code == 422
        assert [(e["loc"], e["type"]) for e in r.json()["detail"]] == [(["body", "title"], "string_too_short")]
        assert client.get("/tasks").json() == [], "A rejected request must not store anything."


def test_each_app_has_its_own_database(tmp_path):
    first = create_app(url_for(tmp_path / "first.db"))
    with TestClient(first) as client:
        client.post("/tasks", json={"title": "only in the first"})
    second = create_app(url_for(tmp_path / "second.db"))
    with TestClient(second) as client:
        assert client.get("/tasks").json() == [], (
            "A second app with another URL must see an empty database. If it sees the first app's task, the engine "
            "is shared (created at import time or stored in a module variable) instead of made from database_url.")


def test_nothing_touches_the_database_before_startup(tmp_path):
    db = tmp_path / "lazy.db"
    app = create_app(url_for(db))
    assert not db.exists(), (
        "create_app() already created the database file. Create the engine and the tables inside the lifespan, "
        "so they happen when the app starts.")
    with TestClient(app) as client:
        assert client.get("/tasks").json() == [], "At startup the lifespan must create the tables."
    assert db.exists()


def test_the_app_can_start_twice(tmp_path):
    app = create_app(url_for(tmp_path / "again.db"))
    with TestClient(app) as client:
        client.post("/tasks", json={"title": "before restart"})
    with TestClient(app) as client:          # shutdown disposed the engine; startup must build a new one
        r = client.get("/tasks")
        assert r.status_code == 200, f"After a restart the app must work again, got {r.status_code}: {r.text}"
        assert [t["title"] for t in r.json()] == ["before restart"], "The data is in the file, so it survives a restart."
        assert client.post("/tasks", json={"title": "after"}).json()["id"] == 2
