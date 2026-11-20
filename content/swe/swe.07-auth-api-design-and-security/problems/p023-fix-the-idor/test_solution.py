import pytest
from fastapi.testclient import TestClient

from solution import build_app

ASHA = {"Authorization": "Bearer t-asha"}
RAVI = {"Authorization": "Bearer t-ravi"}


@pytest.fixture
def client():
    with TestClient(build_app()) as c:
        yield c


@pytest.fixture
def asha_note(client):
    r = client.post("/notes", json={"text": "asha private plan"}, headers=ASHA)
    assert r.status_code == 201, "Setup failed: POST /notes must still work for the owner."
    return r.json()["id"]


def test_owner_can_read_update_and_delete_own_note(client, asha_note):
    assert client.get(f"/notes/{asha_note}", headers=ASHA).json()["text"] == "asha private plan", "The owner must still be able to read their note."
    r = client.patch(f"/notes/{asha_note}", json={"text": "changed"}, headers=ASHA)
    assert r.status_code == 200 and r.json()["text"] == "changed", "The owner must still be able to update their note."
    assert client.get(f"/notes/{asha_note}", headers=ASHA).json()["text"] == "changed"
    assert client.delete(f"/notes/{asha_note}", headers=ASHA).status_code == 200, "The owner must still be able to delete their note."
    assert client.get(f"/notes/{asha_note}", headers=ASHA).status_code == 404


def test_another_user_cannot_read(client, asha_note):
    r = client.get(f"/notes/{asha_note}", headers=RAVI)
    assert r.status_code == 404, f"Ravi read Asha's note (status {r.status_code}). Add AND owner_id = ? to the SELECT and answer 404."
    assert "private" not in r.text, "The body must not contain Asha's text."


def test_another_user_cannot_update_and_nothing_changes(client, asha_note):
    r = client.patch(f"/notes/{asha_note}", json={"text": "hacked"}, headers=RAVI)
    assert r.status_code == 404, f"Ravi updated Asha's note (status {r.status_code}). Scope the UPDATE with AND owner_id = ?."
    assert client.get(f"/notes/{asha_note}", headers=ASHA).json()["text"] == "asha private plan", "Asha's note was changed by Ravi (side effect)."


def test_another_user_cannot_delete_and_the_note_survives(client, asha_note):
    r = client.delete(f"/notes/{asha_note}", headers=RAVI)
    assert r.status_code == 404, f"Ravi deleted Asha's note (status {r.status_code}). Scope the DELETE with AND owner_id = ?."
    assert client.get(f"/notes/{asha_note}", headers=ASHA).status_code == 200, "Asha's note is gone after Ravi's DELETE."


def test_not_yours_looks_exactly_like_missing(client, asha_note):
    missing = client.get("/notes/9999", headers=RAVI)
    theirs = client.get(f"/notes/{asha_note}", headers=RAVI)
    assert (missing.status_code, missing.json()) == (theirs.status_code, theirs.json()), (
        "'Not yours' and 'does not exist' must be indistinguishable (same status and body), or ids can be probed (chapter 7.5).")
    for method in ("patch", "delete"):
        kwargs = {"json": {"text": "x"}} if method == "patch" else {}
        a = getattr(client, method)("/notes/9999", headers=RAVI, **kwargs)
        b = getattr(client, method)(f"/notes/{asha_note}", headers=RAVI, **kwargs)
        assert (a.status_code, a.json()) == (b.status_code, b.json()), f"{method.upper()}: missing and not-yours must look the same."


def test_ravis_own_notes_are_unaffected(client, asha_note):
    mine = client.post("/notes", json={"text": "ravi note"}, headers=RAVI).json()["id"]
    assert client.patch(f"/notes/{mine}", json={"text": "ravi edited"}, headers=RAVI).status_code == 200
    assert client.get(f"/notes/{mine}", headers=RAVI).json()["text"] == "ravi edited"
    assert client.delete(f"/notes/{mine}", headers=RAVI).status_code == 200
    assert client.get(f"/notes/{asha_note}", headers=ASHA).status_code == 200


def test_listing_shows_only_own_notes(client, asha_note):
    client.post("/notes", json={"text": "ravi note"}, headers=RAVI)
    texts = [n["text"] for n in client.get("/notes", headers=RAVI).json()]
    assert texts == ["ravi note"], f"Ravi's list shows {texts}. The list endpoint was already correct: do not break it."


@pytest.mark.parametrize("method,path", [("get", "/notes/1"), ("patch", "/notes/1"), ("delete", "/notes/1")])
def test_anonymous_gets_401(client, asha_note, method, path):
    kwargs = {"json": {"text": "x"}} if method == "patch" else {}
    r = getattr(client, method)(path, **kwargs)
    assert r.status_code == 401, f"No token must give 401, got {r.status_code}."
