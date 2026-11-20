import pytest
from fastapi.testclient import TestClient

from solution import create_app

HINT = ("a 500 here is the MissingGreenlet trap: the query did not load task.tags, so reading or appending to it "
        "tried a lazy load without await. Add selectinload(Task.tags) to the query.")


@pytest.fixture
def client(tmp_path):
    app = create_app("sqlite+aiosqlite:///" + (tmp_path / "tags.db").as_posix())
    with TestClient(app, raise_server_exceptions=False) as c:
        c.post("/tasks", json={"title": "write", "tags": ["home", "urgent"]})
        c.post("/tasks", json={"title": "read"})
        yield c


def test_create_still_works(client):
    r = client.post("/tasks", json={"title": "plan", "tags": ["work"]})
    assert r.status_code == 201 and r.json() == {"id": 3, "title": "plan", "tags": [{"name": "work"}]}, f"Got {r.status_code} {r.text}"


def test_list_includes_the_tags(client):
    r = client.get("/tasks")
    assert r.status_code == 200, f"GET /tasks answered {r.status_code}: {HINT}"
    assert r.json() == [
        {"id": 1, "title": "write", "tags": [{"name": "home"}, {"name": "urgent"}]},
        {"id": 2, "title": "read", "tags": []},
    ], f"Every task must come with its tags (an empty list when it has none); got {r.json()}"


def test_one_task_includes_its_tags(client):
    r = client.get("/tasks/1")
    assert r.status_code == 200, f"GET /tasks/1 answered {r.status_code}: {HINT} session.get(..., options=[...]) takes it too."
    assert r.json() == {"id": 1, "title": "write", "tags": [{"name": "home"}, {"name": "urgent"}]}, f"Got {r.json()}"


def test_missing_task_is_still_404(client):
    r = client.get("/tasks/9")
    assert r.status_code == 404 and r.json() == {"detail": "Task not found"}, f"Got {r.status_code} {r.text}"
    r = client.post("/tasks/9/tags", json={"name": "x"})
    assert r.status_code == 404, f"Adding a tag to a missing task is 404, got {r.status_code}"


def test_add_a_tag(client):
    r = client.post("/tasks/2/tags", json={"name": "later"})
    assert r.status_code == 201, f"POST /tasks/2/tags answered {r.status_code}: task.tags.append(...) also needs the tags loaded. {HINT}"
    assert r.json() == {"id": 2, "title": "read", "tags": [{"name": "later"}]}, f"Got {r.json()}"
    r = client.post("/tasks/1/tags", json={"name": "later"})
    assert [t["name"] for t in r.json()["tags"]] == ["home", "urgent", "later"], (
        f"The new tag is added to the existing ones, not instead of them; got {r.json()}")


def test_added_tag_is_stored(client):
    client.post("/tasks/2/tags", json={"name": "later"})
    r = client.get("/tasks/2")
    assert r.status_code == 200 and r.json()["tags"] == [{"name": "later"}], f"The tag must be committed; got {r.status_code} {r.text}"
