import sqlite3

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

TOKENS = {"t-asha": 1, "t-ravi": 2}


class NoteIn(BaseModel):
    text: str


def build_app() -> FastAPI:
    db = sqlite3.connect(":memory:", check_same_thread=False)
    db.row_factory = sqlite3.Row
    db.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL, text TEXT NOT NULL)")
    app = FastAPI()

    def current_user(authorization: str = Header(default="")) -> int:
        user_id = TOKENS.get(authorization.removeprefix("Bearer "))
        if user_id is None:
            raise HTTPException(401, "login required", headers={"WWW-Authenticate": "Bearer"})
        return user_id

    @app.post("/notes", status_code=201)
    def create_note(note: NoteIn, user_id: int = Depends(current_user)):
        cur = db.execute("INSERT INTO notes (owner_id, text) VALUES (?, ?)", (user_id, note.text))
        db.commit()
        return {"id": cur.lastrowid, "text": note.text}

    @app.get("/notes")
    def list_notes(user_id: int = Depends(current_user)):
        rows = db.execute("SELECT id, text FROM notes WHERE owner_id = ? ORDER BY id", (user_id,)).fetchall()
        return [dict(r) for r in rows]

    @app.get("/notes/{note_id}")
    def get_note(note_id: int, user_id: int = Depends(current_user)):
        row = db.execute("SELECT id, text FROM notes WHERE id = ? AND owner_id = ?",
                         (note_id, user_id)).fetchone()          # scoped to the caller
        if row is None:
            raise HTTPException(404, "note not found")
        return dict(row)

    @app.patch("/notes/{note_id}")
    def update_note(note_id: int, note: NoteIn, user_id: int = Depends(current_user)):
        cur = db.execute("UPDATE notes SET text = ? WHERE id = ? AND owner_id = ?",
                         (note.text, note_id, user_id))             # scoped to the caller
        db.commit()
        if cur.rowcount == 0:
            raise HTTPException(404, "note not found")
        return {"id": note_id, "text": note.text}

    @app.delete("/notes/{note_id}")
    def delete_note(note_id: int, user_id: int = Depends(current_user)):
        cur = db.execute("DELETE FROM notes WHERE id = ? AND owner_id = ?", (note_id, user_id))      # scoped to the caller
        db.commit()
        if cur.rowcount == 0:
            raise HTTPException(404, "note not found")
        return {"deleted": note_id}

    return app
