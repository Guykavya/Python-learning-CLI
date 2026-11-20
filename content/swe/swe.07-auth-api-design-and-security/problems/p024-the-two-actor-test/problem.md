# The two-actor test

Chapter section 8.4 (the two-actor test). One logged-in user cannot reveal an IDOR bug: every object they fetch is theirs. The test needs **two actors**: arrange as A, act as B (and as an anonymous caller), assert that B gets `404` or `401`, that the body holds none of A's data, and, for writes, that **A's data is unchanged afterwards**.

You write the **test**, not the app. In `solution.py` write

```python
def check_isolation(make_client) -> list[str]:
```

`make_client()` returns a fresh `fastapi.testclient.TestClient` for a notes API (below). Use only that client. Your function returns a list of **problem descriptions**: an empty list `[]` means "the rules hold", otherwise one short sentence per problem found. It must not raise.

The API (tokens: `t-asha` is Asha, `t-ravi` is Ravi; send `Authorization: Bearer <token>`; no header means anonymous):

| Request | Meaning |
|---|---|
| `POST /notes` `{"text": ...}` | creates a note for the caller; `201` with `{"id", "text"}` |
| `GET /notes` | the caller's own notes |
| `GET /notes/{id}` | a note of the caller, otherwise `404` |
| `PATCH /notes/{id}` `{"text": ...}` | change a note of the caller, otherwise `404` |
| `DELETE /notes/{id}` | delete a note of the caller, otherwise `404` |

The rules to check (chapter 8.4): other users and anonymous callers must not **read** Asha's note; Ravi must not **update** or **delete** it and the note must be **unchanged / still there** afterwards; Ravi's **list** must not show it. And the owner must still be able to read their own note, because a server that says 404 to everybody passes every denial check.

## How the tests grade you

The tests run your function against **five apps** and look only at what it returns:

1. the secure app: you must return `[]`;
2. an app where `GET /notes/{id}` has no owner check (read hole);
3. an app where `PATCH /notes/{id}` changes the note without an owner check **and then answers 404** (update hole; a test that only looks at the status code does not see it);
4. an app where `GET /notes` lists everybody's notes (list hole);
5. an app that answers 404 to everything: you must report a problem.

"Always run a new security test against the broken version once: a test that cannot fail proves nothing."

<details><summary>The secure app (to experiment with in your own file)</summary>

```python
import sqlite3

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

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
```

The tests use `build_notes_app(None)` for the secure app and `build_notes_app("read")`, `"update"`, `"list"`, `"deny_all"` for the others.

</details>

## Example

```python
problems = check_isolation(make_client)
# secure app            -> []
# the read-hole app     -> ["Ravi got status 200 reading Asha's note (expected 401 or 404)", ...]
```
