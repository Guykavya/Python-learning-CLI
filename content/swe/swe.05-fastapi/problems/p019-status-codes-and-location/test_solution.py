import pytest
from fastapi.testclient import TestClient

from solution import NOTES, app


@pytest.fixture
def client():
    NOTES.clear()
    with TestClient(app) as c:
        yield c


def test_create_answers_201_with_the_note(client):
    r = client.post("/notes", json={"text": "buy milk"})
    assert r.status_code == 201, f"Creating a resource answers 201 Created, not {r.status_code}. Set status_code=201 on the decorator."
    assert r.json() == {"id": 1, "text": "buy milk"}, f"Got {r.json()}"
    assert NOTES == {1: "buy milk"}, f"The note must be stored in NOTES; NOTES is {NOTES}"


def test_create_sets_location(client):
    client.post("/notes", json={"text": "a"})
    r = client.post("/notes", json={"text": "b"})
    assert r.headers.get("location") == "/notes/2", (
        f"Location should point at the new note, '/notes/2'; got {r.headers.get('location')!r}. "
        "Set response.headers['Location'] on the Response parameter.")


def test_location_leads_to_the_note(client):
    r = client.post("/notes", json={"text": "call mum"})
    again = client.get(r.headers["location"])
    assert again.status_code == 200 and again.json() == {"id": 1, "text": "call mum"}, (
        f"GET on the Location URL should return the note; got {again.status_code} {again.text}")


def test_duplicate_is_409_and_stores_nothing(client):
    client.post("/notes", json={"text": "buy milk"})
    r = client.post("/notes", json={"text": "buy milk"})
    assert r.status_code == 409, f"A duplicate is a conflict with the current state: 409, not {r.status_code}"
    assert r.json() == {"detail": "Note already exists"}, f"Got {r.json()}"
    assert "location" not in r.headers, "A failed create must not send a Location header (raise before you set it)."
    assert NOTES == {1: "buy milk"}, f"The duplicate must not be stored; NOTES is {NOTES}"


def test_get_missing_is_404(client):
    r = client.get("/notes/7")
    assert r.status_code == 404, f"A missing note is 404, got {r.status_code}"
    assert r.json() == {"detail": "Note not found"}, f"Got {r.json()}"


def test_delete_is_204_with_an_empty_body(client):
    client.post("/notes", json={"text": "x"})
    r = client.delete("/notes/1")
    assert r.status_code == 204, f"A successful DELETE with nothing to return is 204, got {r.status_code}"
    assert r.content == b"", f"A 204 must have an empty body; got {r.content!r}. Return nothing (None) from the function."
    assert NOTES == {}, f"The note must be removed from NOTES; NOTES is {NOTES}"


def test_delete_missing_is_404(client):
    r = client.delete("/notes/1")
    assert r.status_code == 404, f"Deleting a note that does not exist is 404, got {r.status_code}"
    assert r.json() == {"detail": "Note not found"}


def test_get_after_delete_is_404(client):
    client.post("/notes", json={"text": "x"})
    client.delete("/notes/1")
    assert client.get("/notes/1").status_code == 404, "After DELETE the note must be gone."


def test_ids_continue_after_the_highest(client):
    client.post("/notes", json={"text": "a"})
    client.post("/notes", json={"text": "b"})
    client.delete("/notes/1")
    r = client.post("/notes", json={"text": "c"})
    assert r.json()["id"] == 3, f"The next id is max(NOTES) + 1 = 3; got {r.json().get('id')}. len(NOTES) + 1 would reuse id 2."
