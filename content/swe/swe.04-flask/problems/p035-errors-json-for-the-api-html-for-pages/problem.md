# Errors: JSON for the API, HTML for pages

Chapter section 19. A browser expects an HTML error page; an API client expects JSON with the right status. And **nobody** should see a traceback or a secret. In `solution.py` the starter has the factory and these routes:

| Route | Does |
|---|---|
| `GET /` | `home` |
| `GET /api/items` | `{"items": []}` (GET only) |
| `GET /boom` and `GET /api/boom` | raise `RuntimeError("db password is hunter2")` |
| `GET /api/forbidden` | `abort(403)` |

Register error handlers (`app.register_error_handler`) so that:

1. **Every HTTP error** (404, 405, 403, ...) raised anywhere is answered like this:
   - path starts with `/api/` → status as given, `Content-Type: application/json`, body `{"error": {"code": "<name lower-cased, spaces to underscores>", "message": "<the standard name>"}}`, for example `{"error": {"code": "not_found", "message": "Not Found"}}`.
   - any other path → an **HTML** page with an `<h1>` like `404 Not Found`, and a link back to `/`.
   - A **405** keeps its `Allow` header, in both cases.
2. **Any other exception** (an unexpected bug) → status **500**, in the same two shapes (code `internal_server_error`, message `Internal Server Error`). The answer must **not contain** the exception text, the word `Traceback` or the exception name: write the details to the **log** (`app.logger.exception`), never to the client.

## Example

```text
GET /api/missing      -> 404 application/json {"error": {"code": "not_found", "message": "Not Found"}}
GET /missing          -> 404 text/html <h1>404 Not Found</h1> ...
POST /api/items       -> 405 JSON, Allow: GET, HEAD, OPTIONS
GET /api/boom         -> 500 JSON, no 'hunter2' anywhere
```
