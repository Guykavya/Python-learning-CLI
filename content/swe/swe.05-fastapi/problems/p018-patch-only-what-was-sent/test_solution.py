from datetime import date

import pytest
from fastapi.testclient import TestClient

from solution import TASKS, TaskPatch, app

START = {"id": 1, "title": "write report", "done": False, "due": date(2026, 12, 1)}


@pytest.fixture
def client():
    TASKS.clear()
    TASKS[1] = dict(START)
    TASKS[2] = {"id": 2, "title": "call bank", "done": True, "due": None}
    with TestClient(app) as c:
        yield c


def test_taskpatch_fields_are_all_optional():
    empty = TaskPatch()
    for name in ("title", "done", "due"):
        assert name in TaskPatch.model_fields, f"TaskPatch needs a field {name!r}."
        assert getattr(empty, name) is None, f"TaskPatch.{name} must default to None, so a client can leave it out."


def test_sending_one_field_changes_only_that_field(client):
    r = client.patch("/tasks/1", json={"done": True})
    assert r.status_code == 200, f"PATCH should answer 200, got {r.status_code}: {r.text}"
    assert r.json() == {"id": 1, "title": "write report", "done": True, "due": "2026-12-01"}, (
        f"Only 'done' was sent, so title and due must stay as they were. Got {r.json()}. "
        "If title/due became null you used model_dump() without exclude_unset=True.")


def test_omitting_due_keeps_the_date(client):
    r = client.patch("/tasks/1", json={"title": "write the report"})
    assert r.json()["due"] == "2026-12-01", (
        f"'due' was not sent, so the date must be kept; got {r.json()['due']!r}. Use model_dump(exclude_unset=True).")
    assert r.json()["title"] == "write the report"


def test_sending_due_null_clears_the_date(client):
    r = client.patch("/tasks/1", json={"due": None})
    assert r.status_code == 200, f"{{\"due\": null}} is a valid PATCH body; got {r.status_code}: {r.text}"
    assert r.json()["due"] is None, (
        f"The client sent due=null on purpose to remove the date; got {r.json()['due']!r}. "
        "Do not drop None values (exclude_none=True would drop them); drop only fields that were not sent.")
    assert r.json()["done"] is False and r.json()["title"] == "write report", "Only 'due' was sent; the other fields must not change."


def test_setting_a_new_date(client):
    r = client.patch("/tasks/2", json={"due": "2027-01-15"})
    assert r.json() == {"id": 2, "title": "call bank", "done": True, "due": "2027-01-15"}, f"Got {r.json()}"


def test_several_fields_at_once(client):
    r = client.patch("/tasks/1", json={"title": "new", "done": True, "due": None})
    assert r.json() == {"id": 1, "title": "new", "done": True, "due": None}, f"All three fields were sent; got {r.json()}"


def test_empty_body_changes_nothing(client):
    r = client.patch("/tasks/1", json={})
    assert r.status_code == 200, f"An empty PATCH is allowed and changes nothing; got {r.status_code}"
    assert r.json() == {"id": 1, "title": "write report", "done": False, "due": "2026-12-01"}, (
        f"Nothing was sent, so nothing may change; got {r.json()}")


def test_the_change_is_stored(client):
    client.patch("/tasks/1", json={"done": True})
    client.patch("/tasks/1", json={"due": None})
    r = client.get("/tasks/1")
    assert r.json() == {"id": 1, "title": "write report", "done": True, "due": None}, (
        f"GET after two PATCHes should show both changes; got {r.json()}. Update the dict in TASKS, not a copy.")


def test_unknown_task_is_404(client):
    r = client.patch("/tasks/9", json={"done": True})
    assert r.status_code == 404, f"Task 9 does not exist: expected 404, got {r.status_code}"
    assert r.json() == {"detail": "Task not found"}, f"Got {r.json()}"
    assert 9 not in TASKS, "A PATCH must not create a task that did not exist."


def test_a_bad_date_is_still_validated(client):
    r = client.patch("/tasks/1", json={"due": "next week"})
    assert r.status_code == 422, f"'next week' is not a date: expected 422, got {r.status_code}"
    assert [e["loc"] for e in r.json()["detail"]] == [["body", "due"]], f"The error belongs at ['body', 'due']; got {r.json()['detail']}"
    assert TASKS[1]["due"] == date(2026, 12, 1), "A rejected request must not change the stored task."
