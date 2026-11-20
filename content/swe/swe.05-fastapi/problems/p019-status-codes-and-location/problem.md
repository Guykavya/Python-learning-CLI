# Status codes and `Location`

Chapter sections 7.6 (status codes, the `Response` parameter) and 8.1 (`HTTPException`). The meaning of the codes is in swe.02 section 10.

A notes API stores notes in a module-level dict `NOTES` (id → text). Write three endpoints that answer with the **right status code** for each outcome:

| Request | Outcome | Status | Body | Extra |
|---|---|---|---|---|
| `POST /notes` body `{"text": "..."}` | created | **201** | `{"id": 1, "text": "..."}` | header `Location: /notes/1` |
| `POST /notes` with a text that already exists | duplicate | **409** | `{"detail": "Note already exists"}` | nothing is stored |
| `GET /notes/{note_id}` | found | 200 | `{"id": 1, "text": "..."}` | |
| `GET /notes/{note_id}` | missing | **404** | `{"detail": "Note not found"}` | |
| `DELETE /notes/{note_id}` | deleted | **204** | **empty** (zero bytes) | |
| `DELETE /notes/{note_id}` | missing | **404** | `{"detail": "Note not found"}` | |

Rules:

- The body model is `NoteIn` with one field `text: str`.
- A new note gets the id `max(NOTES, default=0) + 1` (so ids start at 1).
- Set the `Location` header with the `Response` parameter (section 7.6): it tells the client where the new note lives.
- Raise `HTTPException` (from `fastapi`) for 404 and 409.
- For 204: declare `status_code=204` on the decorator and return nothing. A 204 must not have a body.

## Example

```text
POST   /notes {"text": "buy milk"}   -> 201 {"id": 1, "text": "buy milk"}   Location: /notes/1
POST   /notes {"text": "buy milk"}   -> 409 {"detail": "Note already exists"}
GET    /notes/1                      -> 200 {"id": 1, "text": "buy milk"}
DELETE /notes/1                      -> 204 (no body)
GET    /notes/1                      -> 404 {"detail": "Note not found"}
DELETE /notes/1                      -> 404 {"detail": "Note not found"}
```

The tests import `app` and `NOTES` and empty `NOTES` before each test.
