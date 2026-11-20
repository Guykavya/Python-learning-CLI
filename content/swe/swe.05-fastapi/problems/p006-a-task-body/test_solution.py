import pytest
from fastapi.testclient import TestClient

import solution
from solution import TaskIn, app


@pytest.fixture
def client():
    solution.TASKS.clear()
    with TestClient(app) as c:
        yield c
    solution.TASKS.clear()


def errors(response):
    assert response.status_code == 422, f"Expected a 422, got {response.status_code}: {response.text}"
    return [(e["loc"], e["type"]) for e in response.json()["detail"]]


def test_minimal_task_gets_defaults_and_201(client):
    r = client.post("/tasks", json={"title": "buy milk"})
    assert r.status_code == 201, f"Creating something answers 201 Created (status_code=201 on the decorator), got {r.status_code}."
    assert r.json() == {"id": 1, "title": "buy milk", "priority": 3, "tags": []}, (
        f"Got {r.json()}. Expected the stored task with id 1 and the defaults priority=3, tags=[].")


def test_ids_count_up_and_values_are_converted(client):
    client.post("/tasks", json={"title": "buy milk"})
    r = client.post("/tasks", json={"title": "pay rent", "priority": "1", "tags": ["home", "money"]})
    assert r.status_code == 201, r.text
    assert r.json() == {"id": 2, "title": "pay rent", "priority": 1, "tags": ["home", "money"]}, (
        f"Got {r.json()}. The second task has id 2, and the string '1' becomes the int 1 (lax mode).")


def test_list_returns_stored_tasks(client):
    client.post("/tasks", json={"title": "a"})
    client.post("/tasks", json={"title": "b", "tags": ["x"]})
    r = client.get("/tasks")
    assert r.status_code == 200
    assert [t["title"] for t in r.json()] == ["a", "b"], f"GET /tasks must return the stored tasks in id order, got {r.json()}"
    assert r.json()[1]["tags"] == ["x"]


def test_default_list_is_not_shared():
    first, second = TaskIn(title="a"), TaskIn(title="b")
    first.tags.append("oops")
    assert second.tags == [], "Each TaskIn gets its own copy of the [] default (Pydantic copies it); do not share one list."


@pytest.mark.parametrize("kwargs, loc, kind, why", [
    ({"json": {"priority": 2}}, ["body", "title"], "missing", "title has no default, so it is required"),
    ({"json": {"title": "x", "tags": "home"}}, ["body", "tags"], "list_type", "tags must be a JSON list"),
    ({"json": {"title": "x", "priority": "high"}}, ["body", "priority"], "int_parsing", "priority is an int"),
    ({"data": {"title": "x"}}, ["body"], "model_attributes_type", "form data is not a JSON object"),
    ({"json": [{"title": "x"}]}, ["body"], "model_attributes_type", "a JSON list is not an object with fields"),
])
def test_bad_bodies_are_422_and_store_nothing(client, kwargs, loc, kind, why):
    found = errors(client.post("/tasks", **kwargs))
    assert (loc, kind) in found, f"Expected an error at {loc} of type {kind!r} ({why}); got {found}"
    assert solution.TASKS == {}, "A refused request must not store anything: your function should not even run."


def test_broken_json_is_json_invalid(client):
    r = client.post("/tasks", content=b'{"title": ', headers={"content-type": "application/json"})
    found = errors(r)
    assert found and found[0][1] == "json_invalid", f"Broken JSON gives type json_invalid (section 4.3); got {found}"
