import pytest
from fastapi.testclient import TestClient

from solution import check_isolation

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel
import sqlite3

TOKENS = {"t-asha": 1, "t-ravi": 2}


class NoteIn(BaseModel):
    text: str


def build_notes_app(hole=None) -> FastAPI:
    """hole is None for the secure app, or "read", "update", "list", "deny_all" for a broken copy."""
    db = sqlite3.connect(":memory:", check_same_thread=False)
    db.row_factory = sqlite3.Row
    db.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL, text TEXT NOT NULL)")
    app = FastAPI()

    def current_user(authorization: str = Header(default="")) -> int:
        user_id = TOKENS.get(authorization.removeprefix("Bearer "))
        if user_id is None:
            raise HTTPException(401, "login required")
        return user_id

    @app.post("/notes", status_code=201)
    def create_note(note: NoteIn, user_id: int = Depends(current_user)):
        if hole == "deny_all":
            raise HTTPException(404, "note not found")
        cur = db.execute("INSERT INTO notes (owner_id, text) VALUES (?, ?)", (user_id, note.text))
        db.commit()
        return {"id": cur.lastrowid, "text": note.text}

    @app.get("/notes")
    def list_notes(user_id: int = Depends(current_user)):
        if hole == "list":
            rows = db.execute("SELECT id, text FROM notes ORDER BY id").fetchall()          # the hole: everybody's notes
        else:
            rows = db.execute("SELECT id, text FROM notes WHERE owner_id = ? ORDER BY id", (user_id,)).fetchall()
        return [dict(r) for r in rows]

    @app.get("/notes/{note_id}")
    def get_note(note_id: int, user_id: int = Depends(current_user)):
        if hole == "read":
            row = db.execute("SELECT id, text FROM notes WHERE id = ?", (note_id,)).fetchone()   # the hole: no owner
        else:
            row = db.execute("SELECT id, text FROM notes WHERE id = ? AND owner_id = ?", (note_id, user_id)).fetchone()
        if row is None or hole == "deny_all":
            raise HTTPException(404, "note not found")
        return dict(row)

    @app.patch("/notes/{note_id}")
    def update_note(note_id: int, note: NoteIn, user_id: int = Depends(current_user)):
        if hole == "update":
            # the hole: the UPDATE has no owner, and the answer is 404 afterwards, so a status-only test is fooled
            db.execute("UPDATE notes SET text = ? WHERE id = ?", (note.text, note_id))
            db.commit()
            owns = db.execute("SELECT 1 FROM notes WHERE id = ? AND owner_id = ?", (note_id, user_id)).fetchone()
            if owns is None:
                raise HTTPException(404, "note not found")
            return {"id": note_id, "text": note.text}
        cur = db.execute("UPDATE notes SET text = ? WHERE id = ? AND owner_id = ?", (note.text, note_id, user_id))
        db.commit()
        if cur.rowcount == 0 or hole == "deny_all":
            raise HTTPException(404, "note not found")
        return {"id": note_id, "text": note.text}

    @app.delete("/notes/{note_id}")
    def delete_note(note_id: int, user_id: int = Depends(current_user)):
        cur = db.execute("DELETE FROM notes WHERE id = ? AND owner_id = ?", (note_id, user_id))
        db.commit()
        if cur.rowcount == 0:
            raise HTTPException(404, "note not found")
        return {"deleted": note_id}

    return app


def make_client_for(hole):
    def make_client():
        return TestClient(build_notes_app(hole))
    return make_client


def test_the_secure_app_gives_no_problems():
    found = check_isolation(make_client_for(None))
    assert found == [], f"The secure app has no hole, but your test reported {found}. A false alarm makes a test nobody trusts."


def test_a_read_hole_is_found():
    found = check_isolation(make_client_for("read"))
    assert found, "The app lets Ravi read Asha's note by id, and your test did not notice. After creating the note as Asha, GET it as Ravi and as an anonymous caller."


def test_an_update_hole_is_found_even_though_it_answers_404():
    found = check_isolation(make_client_for("update"))
    assert found, (
        "In this app Ravi's PATCH answers 404 but still changes Asha's text. A test that looks only at the status passes it. "
        "After the attack, read the note again as Asha and compare the text (the side effect).")


def test_a_list_hole_is_found():
    found = check_isolation(make_client_for("list"))
    assert found, "In this app GET /notes shows every user's notes. Call the list as Ravi and look for Asha's text."


def test_an_app_that_denies_everything_is_not_secure():
    found = check_isolation(make_client_for("deny_all"))
    assert found, "A server that answers 404 to everybody passes every denial check. Also check that the owner can still read their own note."


def test_the_result_is_a_list_of_strings():
    for hole in (None, "read", "update", "list"):
        found = check_isolation(make_client_for(hole))
        assert isinstance(found, list) and all(isinstance(p, str) and p for p in found), "Return a list of non-empty strings, one per problem."


def test_each_hole_is_reported_by_itself():
    # the same checker must give an independent answer on a fresh app each time
    first = check_isolation(make_client_for("read"))
    second = check_isolation(make_client_for("read"))
    assert bool(first) and bool(second), "Use only the client you are given; do not keep state between calls."
    assert check_isolation(make_client_for(None)) == [], "A secure app checked after a broken one must still give []."
