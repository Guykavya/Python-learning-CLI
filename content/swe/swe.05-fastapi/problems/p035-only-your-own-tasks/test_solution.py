import pytest
from fastapi.testclient import TestClient

from solution import create_app

ASHA = {"Authorization": "Bearer tok-asha"}
BEN = {"Authorization": "Bearer tok-ben"}
NOT_FOUND = {"detail": "Task not found"}


@pytest.fixture
def client():
    with TestClient(create_app(), raise_server_exceptions=False) as c:
        c.post("/tasks", json={"title": "pay rent"}, headers=ASHA)
        c.post("/tasks", json={"title": "gym"}, headers=ASHA)
        c.post("/tasks", json={"title": "call mum"}, headers=BEN)
        yield c


def test_create_sets_the_owner(client):
    r = client.post("/tasks", json={"title": "read"}, headers=BEN)
    assert r.status_code == 201, f"Got {r.status_code}: {r.text}"
    assert r.json() == {"id": 4, "title": "read", "done": False, "owner": "ben"}, f"Got {r.json()}"


def test_owner_in_the_body_is_ignored(client):
    r = client.post("/tasks", json={"title": "sneaky", "owner": "ben"}, headers=ASHA)
    assert r.json()["owner"] == "asha", (
        f"The owner must come from the logged-in user, never from the body; got {r.json().get('owner')!r}")


def test_list_shows_only_own_tasks(client):
    asha = client.get("/tasks", headers=ASHA).json()
    ben = client.get("/tasks", headers=BEN).json()
    assert [t["id"] for t in asha] == [1, 2], f"asha owns tasks 1 and 2; her list shows {[t.get('id') for t in asha]}"
    assert ben == [{"id": 3, "title": "call mum", "done": False, "owner": "ben"}], (
        f"ben must see only his own task; got {ben}. Filter by owner == the current user.")


def test_reading_own_task(client):
    r = client.get("/tasks/1", headers=ASHA)
    assert r.status_code == 200 and r.json() == {"id": 1, "title": "pay rent", "done": False, "owner": "asha"}, f"Got {r.status_code} {r.text}"


def test_reading_someone_elses_task_is_404(client):
    r = client.get("/tasks/1", headers=BEN)
    assert r.status_code == 404, f"ben must not read asha's task 1; expected 404, got {r.status_code}: {r.text}"
    assert r.json() == NOT_FOUND, f"Got {r.json()}"


def test_foreign_and_missing_look_identical(client):
    foreign = client.get("/tasks/1", headers=BEN)
    missing = client.get("/tasks/999", headers=BEN)
    assert (foreign.status_code, foreign.json()) == (missing.status_code, missing.json()) == (404, NOT_FOUND), (
        f"Someone else's task and a missing task must give the same answer; got {foreign.status_code} {foreign.text} "
        f"and {missing.status_code} {missing.text}. A 403 would reveal that task 1 exists.")


def test_editing_someone_elses_task_is_404_and_changes_nothing(client):
    r = client.patch("/tasks/1", json={"done": True}, headers=BEN)
    assert r.status_code == 404 and r.json() == NOT_FOUND, f"ben must not edit asha's task; got {r.status_code} {r.text}"
    assert client.get("/tasks/1", headers=ASHA).json()["done"] is False, "asha's task must be unchanged after ben's attempt."


def test_deleting_someone_elses_task_is_404_and_keeps_it(client):
    r = client.delete("/tasks/2", headers=BEN)
    assert r.status_code == 404 and r.json() == NOT_FOUND, f"ben must not delete asha's task; got {r.status_code} {r.text}"
    assert client.get("/tasks/2", headers=ASHA).status_code == 200, "asha's task 2 must still exist."


def test_owner_can_edit_and_delete(client):
    r = client.patch("/tasks/1", json={"done": True}, headers=ASHA)
    assert r.status_code == 200 and r.json() == {"id": 1, "title": "pay rent", "done": True, "owner": "asha"}, f"Got {r.status_code} {r.text}"
    r = client.delete("/tasks/1", headers=ASHA)
    assert r.status_code == 204 and r.content == b"", f"Deleting your own task is 204 with no body; got {r.status_code} {r.content!r}"
    assert client.get("/tasks/1", headers=ASHA).status_code == 404, "After DELETE the task is gone."
    assert [t["id"] for t in client.get("/tasks", headers=ASHA).json()] == [2]


def test_missing_task_is_404_for_every_method(client):
    for method in ("get", "patch", "delete"):
        kwargs = {"json": {"done": True}} if method == "patch" else {}
        r = getattr(client, method)("/tasks/999", headers=ASHA, **kwargs)
        assert r.status_code == 404 and r.json() == NOT_FOUND, f"{method.upper()} /tasks/999 must be 404 Task not found; got {r.status_code} {r.text}"


def test_login_is_required(client):
    assert client.get("/tasks").status_code == 401, "Without a token: 401."
    assert client.get("/tasks/1", headers={"Authorization": "Bearer nope"}).status_code == 401, "A bad token: 401."
    assert client.delete("/tasks/1").status_code == 401
    assert client.get("/tasks/1", headers=ASHA).status_code == 200, "The failed attempts must not have changed anything."


def test_ids_are_not_reused(client):
    client.delete("/tasks/3", headers=BEN)
    r = client.post("/tasks", json={"title": "new"}, headers=BEN)
    assert r.json()["id"] == 4, f"After deleting task 3 the next id is still 4 (max + 1), got {r.json().get('id')}"


def test_each_app_starts_empty():
    with TestClient(create_app()) as c:
        assert c.get("/tasks", headers=ASHA).json() == [], "create_app() must make a new, empty task store."
