import pytest
from fastapi.testclient import TestClient

from solution import build_app


@pytest.fixture
def client():
    with TestClient(build_app({1: "original", 2: "second"})) as c:
        yield c


def put(client, note_id, text, etag=None):
    headers = {} if etag is None else {"If-Match": etag}
    return client.put(f"/notes/{note_id}", json={"note": text}, headers=headers)


def test_get_returns_the_note_and_an_etag(client):
    r = client.get("/notes/1")
    assert r.status_code == 200 and r.json() == {"id": 1, "note": "original"}, f"GET must return the note as JSON; got {r.status_code} {r.text}"
    tag = r.headers.get("etag")
    assert tag and tag.startswith('"') and tag.endswith('"') and len(tag) > 2, f"The ETag header is a quoted text like \"abc\"; got {tag!r}"


def test_etag_is_stable_while_nothing_changes(client):
    assert client.get("/notes/1").headers["etag"] == client.get("/notes/1").headers["etag"], (
        "Two reads of an unchanged note must give the same ETag (do not use a random value or a timestamp of the request)")


def test_unknown_note_is_404(client):
    assert client.get("/notes/99").status_code == 404, "GET of a missing note is 404"
    assert put(client, 99, "x", '"abc"').status_code == 404, "PUT of a missing note is 404, even with an If-Match header"
    assert put(client, 99, "x").status_code == 404, "A missing note is 404 before the 428 check"


def test_put_without_if_match_is_428(client):
    r = put(client, 1, "changed")
    assert r.status_code == 428, f"No If-Match header: 428 Precondition Required, got {r.status_code}"
    assert client.get("/notes/1").json()["note"] == "original", "A refused PUT must not change the note"


def test_put_with_the_current_etag_works_and_returns_a_new_etag(client):
    old = client.get("/notes/1").headers["etag"]
    r = put(client, 1, "alice was here", old)
    assert r.status_code == 200 and r.json() == {"id": 1, "note": "alice was here"}, f"A PUT with the current ETag must succeed; got {r.status_code} {r.text}"
    new = r.headers.get("etag")
    assert new and new != old, "The PUT response must carry the NEW ETag (different from the old one)"
    again = client.get("/notes/1")
    assert again.json()["note"] == "alice was here" and again.headers["etag"] == new, "GET after the update must show the new text and the same new ETag"


def test_stale_etag_is_412_and_changes_nothing(client):
    alice = client.get("/notes/1").headers["etag"]
    bob = client.get("/notes/1").headers["etag"]                 # both read version 1
    assert put(client, 1, "alice", alice).status_code == 200
    r = put(client, 1, "bob", bob)
    assert r.status_code == 412, f"Bob's ETag is stale (the note changed): expected 412, got {r.status_code}"
    assert client.get("/notes/1").json()["note"] == "alice", "A refused PUT must not overwrite alice's text (lost update!)"


def test_reload_and_retry_works(client):
    alice = client.get("/notes/1").headers["etag"]
    bob = alice
    put(client, 1, "alice", alice)
    assert put(client, 1, "bob", bob).status_code == 412
    fresh = client.get("/notes/1").headers["etag"]
    assert put(client, 1, "alice + bob", fresh).status_code == 200, "After reloading, bob's PUT with the fresh ETag must pass"
    assert client.get("/notes/1").json()["note"] == "alice + bob"


def test_every_update_makes_every_older_etag_useless(client):
    seen = [client.get("/notes/1").headers["etag"]]
    for i in range(3):
        r = put(client, 1, f"edit {i}", seen[-1])
        assert r.status_code == 200
        seen.append(r.headers["etag"])
    assert len(set(seen)) == 4, f"Each version needs its own ETag; got {seen}"
    for old in seen[:-1]:
        assert put(client, 1, "late", old).status_code == 412, "An ETag of an older version must never be accepted again"


def test_used_etag_cannot_be_used_twice(client):
    tag = client.get("/notes/1").headers["etag"]
    assert put(client, 1, "first", tag).status_code == 200
    assert put(client, 1, "second", tag).status_code == 412, "The same If-Match twice: the second PUT is a lost update, 412"


@pytest.mark.parametrize("junk", ['"nonsense"', "abc", "*x", '"1"', ""])
def test_garbage_if_match_is_412_not_500(client, junk):
    r = put(client, 1, "x", junk)
    assert r.status_code == 412, f"If-Match {junk!r} is not the current ETag: 412, got {r.status_code}"


def test_notes_are_independent(client):
    t1 = client.get("/notes/1").headers["etag"]
    t2 = client.get("/notes/2").headers["etag"]
    assert put(client, 1, "one changed", t1).status_code == 200
    assert put(client, 2, "two changed", t2).status_code == 200, "Changing note 1 must not invalidate the ETag of note 2"
    assert client.get("/notes/2").json()["note"] == "two changed"


def test_body_must_have_a_text_note(client):
    tag = client.get("/notes/1").headers["etag"]
    r = client.put("/notes/1", json={"wrong": 1}, headers={"If-Match": tag})
    assert r.status_code == 422, f"A body without a 'note' text is a validation error (422); got {r.status_code}"
