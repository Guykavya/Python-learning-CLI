## Hint 1

Where does each status code come from? The success code is a property of the **route** (`status_code=` on the decorator). The failure codes come from **raising** `HTTPException(code, detail)`. A header on a successful answer is set on the `Response` parameter that FastAPI passes in.

## Hint 2

For the duplicate check, `data.text in NOTES.values()` is enough. Check it **before** you store anything or set the header. For `DELETE`, put `status_code=204` on the decorator and let the function end without `return` (it returns `None`).

## Hint 3

```text
@app.post("/notes", status_code=201)
create_note(data, response):
    if data.text in NOTES.values(): raise HTTPException(409, "Note already exists")
    note_id = max(NOTES, default=0) + 1
    NOTES[note_id] = data.text
    response.headers["Location"] = f"/notes/{note_id}"
    return {"id": note_id, "text": data.text}

get_note:    if missing -> HTTPException(404, "Note not found"); return {"id", "text"}
@app.delete(..., status_code=204)
delete_note: if missing -> 404; del NOTES[note_id]
```
