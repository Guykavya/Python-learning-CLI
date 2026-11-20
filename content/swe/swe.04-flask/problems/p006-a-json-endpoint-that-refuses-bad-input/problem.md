# A JSON endpoint that refuses bad input

Chapter section 4.3. A JSON API must tell clients **exactly what is wrong**. In `solution.py` write `create_app(test_config=None)` with `POST /api/notes` (and `GET /api/notes/<int:note_id>`, used for the `Location` header). Keep the notes in a list inside the factory. `test_config`, when given, is a dict merged into `app.config`.

The checks, in this order:

| Situation | Answer |
|---|---|
| The request is **not JSON** (`Content-Type` is not `application/json`) | **415**, JSON body `{"error": "<message>"}` |
| The body **cannot be parsed** as JSON | **400**, JSON `{"error": "<message>"}` |
| The JSON is valid but **not an object** (a list, a number) | **400**, JSON `{"error": "<message>"}` |
| `title` missing, not a string, blank, or longer than 100 characters; or `body` present but not a string | **422**, JSON `{"error": "validation failed", "fields": {"title": "<why>"}}` listing **every** bad field |
| Success | **201**, the note as JSON `{"id", "title", "body"}` and a `Location: /api/notes/<id>` header |

`title` is stored stripped; `body` defaults to `""`. Ids start at 1.

Use `request.is_json` and `request.get_json(silent=True)`; the plain `get_json()` would answer with Flask's own HTML error pages.

## Example

```text
POST /api/notes  Content-Type: text/plain      -> 415 {"error": "..."}
POST /api/notes  {"title": "Milk"               -> 400 {"error": "..."}   (broken JSON)
POST /api/notes  {"body": 5}                    -> 422 {"error": "validation failed", "fields": {"title": "...", "body": "..."}}
POST /api/notes  {"title": "Milk"}              -> 201 Location: /api/notes/1
```
