## Approach

```python
@app.post("/notes", status_code=status.HTTP_201_CREATED)
def create_note(data: NoteIn, response: Response):
    if data.text in NOTES.values():
        raise HTTPException(status.HTTP_409_CONFLICT, "Note already exists")
    note_id = max(NOTES, default=0) + 1
    NOTES[note_id] = data.text
    response.headers["Location"] = f"/notes/{note_id}"
    return {"id": note_id, "text": data.text}


@app.get("/notes/{note_id}")
def get_note(note_id: int):
    if note_id not in NOTES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Note not found")
    return {"id": note_id, "text": NOTES[note_id]}


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int):
    if note_id not in NOTES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Note not found")
    del NOTES[note_id]
```

Each code tells the client something different, so a client can react without reading the text:

- **201 Created** + `Location`: "it worked, and here is the URL of the new thing". A client can follow `Location` without building URLs itself.
- **409 Conflict**: "your request is fine, but it clashes with the current state" (the note exists). It is not a 422 (the JSON was valid) and not a 400.
- **204 No Content**: "done, nothing to show". HTTP forbids a body on a 204; FastAPI sends none when the function returns `None`.
- **404 Not Found**: the id names nothing.

`raise` stops the function at once, so the duplicate never reaches `NOTES` and never gets a `Location` header. (The `Response` parameter's headers are only used for the successful answer anyway.)

## Complexity

`text in NOTES.values()` is O(n); `max(NOTES)` is O(n). A real database would use a unique index and a sequence, both O(log n).

## Another way

Return a response object yourself: `return JSONResponse({"id": note_id, "text": data.text}, status_code=201, headers={"Location": f"/notes/{note_id}"})`. It works, but section 7.6 warns that returning a response object skips `response_model` filtering, so prefer the decorator plus the `Response` parameter.
