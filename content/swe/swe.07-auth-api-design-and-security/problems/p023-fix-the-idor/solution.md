## Approach

```python
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
                     (note.text, note_id, user_id))
    db.commit()
    if cur.rowcount == 0:
        raise HTTPException(404, "note not found")
    return {"id": note_id, "text": note.text}


@app.delete("/notes/{note_id}")
def delete_note(note_id: int, user_id: int = Depends(current_user)):
    cur = db.execute("DELETE FROM notes WHERE id = ? AND owner_id = ?", (note_id, user_id))
    db.commit()
    if cur.rowcount == 0:
        raise HTTPException(404, "note not found")
    return {"deleted": note_id}
```

Why this is the best fix: the owner is part of the query, so another user's row is never loaded, changed or deleted. There is no moment where the data is fetched first and checked later, and a developer cannot forget the check on one branch. Both "not yours" and "missing" reach the same `404` line, so the answer does not reveal which ids exist (chapter 7.5 and 8.3).

## Complexity

One indexed query per request: O(1) with the primary key on `id`.

## Another way

Fetch the note by id, then ask a policy function (`can(user, "read", note)`, problem p021) and answer 404 when it says no. This is needed when the rule is more than "owner" (support staff may read everything). Keep the 404, and make sure the update and delete use the same check.
