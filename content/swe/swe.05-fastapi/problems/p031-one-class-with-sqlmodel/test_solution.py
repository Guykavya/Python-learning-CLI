import pytest
from fastapi.testclient import TestClient

from solution import Task, TaskCreate, TaskRead, create_app


@pytest.fixture
def client():
    with TestClient(create_app()) as c:
        yield c


def test_the_classes():
    assert hasattr(Task, "__table__"), "Task must be the table: class Task(TaskBase, table=True)."
    for cls in (TaskCreate, TaskRead):
        assert not hasattr(cls, "__table__"), f"{cls.__name__} is a schema, not a table: no table=True."
    assert "id" not in TaskCreate.model_fields, (
        "TaskCreate must not have an id field: the input model decides what a client may send.")
    assert "id" in TaskRead.model_fields and TaskRead.model_fields["id"].is_required(), (
        "TaskRead must have a required 'id: int', so every response has an id.")
    for cls in (TaskCreate, TaskRead):
        assert {"title", "priority"} <= set(cls.model_fields), f"{cls.__name__} needs title and priority (from TaskBase)."


def test_create(client):
    r = client.post("/tasks", json={"title": "write", "priority": 2})
    assert r.status_code == 201, f"Creating answers 201, got {r.status_code}: {r.text}"
    assert r.json() == {"title": "write", "priority": 2, "id": 1}, f"Got {r.json()}"
    assert client.post("/tasks", json={"title": "read"}).json() == {"title": "read", "priority": 3, "id": 2}, (
        "priority defaults to 3.")


def test_the_client_cannot_choose_the_id(client):
    r = client.post("/tasks", json={"id": 99, "title": "sneaky"})
    assert r.status_code == 201
    assert r.json()["id"] == 1, (
        f"The client sent id 99 and got id {r.json().get('id')}. The body model must be TaskCreate (no id), "
        "so the database chooses the id.")
    assert client.get("/tasks/99").status_code == 404, "No row with id 99 may exist."


def test_the_client_cannot_overwrite_a_row(client):
    client.post("/tasks", json={"title": "original"})
    r = client.post("/tasks", json={"id": 1, "title": "overwritten"})
    assert r.status_code == 201 and r.json()["id"] == 2, f"A second POST makes a new row; got {r.status_code} {r.text}"
    assert client.get("/tasks/1").json()["title"] == "original", "Row 1 must keep its title."


@pytest.mark.parametrize("body, loc, kind", [
    ({"title": "x", "priority": 9}, ["body", "priority"], "less_than_equal"),
    ({"title": "x", "priority": 0}, ["body", "priority"], "greater_than_equal"),
    ({"title": ""}, ["body", "title"], "string_too_short"),
    ({"title": "x" * 101}, ["body", "title"], "string_too_long"),
    ({"priority": 2}, ["body", "title"], "missing"),
])
def test_rules_are_enforced(client, body, loc, kind):
    r = client.post("/tasks", json=body)
    assert r.status_code == 422, (
        f"{body} breaks a rule and must be a 422, got {r.status_code}. A table=True class does not validate; "
        "use TaskCreate (a plain SQLModel with the Field rules) as the body.")
    assert [(e["loc"], e["type"]) for e in r.json()["detail"]] == [(loc, kind)], f"Got {r.json()['detail']}"
    assert client.get("/tasks").json() == [], "Nothing may be stored after a 422."


def test_list_and_get(client):
    client.post("/tasks", json={"title": "a"})
    client.post("/tasks", json={"title": "b", "priority": 5})
    assert client.get("/tasks").json() == [
        {"title": "a", "priority": 3, "id": 1},
        {"title": "b", "priority": 5, "id": 2},
    ]
    assert client.get("/tasks/2").json() == {"title": "b", "priority": 5, "id": 2}
    r = client.get("/tasks/3")
    assert r.status_code == 404 and r.json() == {"detail": "Task not found"}


def test_each_app_has_its_own_database():
    with TestClient(create_app()) as one:
        one.post("/tasks", json={"title": "only here"})
    with TestClient(create_app()) as two:
        assert two.get("/tasks").json() == [], "create_app() must create a new in-memory engine each time."
