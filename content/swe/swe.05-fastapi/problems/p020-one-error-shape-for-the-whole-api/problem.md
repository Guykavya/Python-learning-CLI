# One error shape for the whole API

Chapter sections 8.1 and 8.2 (exception handlers), and 6.2 (the 422 body).

Out of the box FastAPI answers errors in different shapes: `{"detail": "..."}` for an `HTTPException`, `{"detail": [ ... ]}` for a 422, and a plain-text 500 for an exception it does not know. A client then needs three different parsers. Make **every** error of this API look the same:

```json
{"error": {"code": "...", "message": "...", "details": [...]}}
```

`details` is **always present**: a list, empty when there is nothing more to say.

The starter already has the endpoints, a domain exception and an `envelope()` helper to fill in. Register **three exception handlers**:

| Exception | Status | `code` | `message` | `details` |
|---|---|---|---|---|
| `NotFound(resource, item_id)` (our own class) | 404 | `"not_found"` | `"Task 7 not found"` (`f"{resource} {item_id} not found"`) | `[]` |
| `HTTPException`, **Starlette's** class (catches FastAPI's too, and the automatic 404/405) | `exc.status_code` | `"http_error"` | `str(exc.detail)` | `[]` |
| `RequestValidationError` | **422** (keep it) | `"validation_failed"` | `"Request data is invalid"` | one item per error: `{"loc": [...], "type": "...", "message": "..."}` |

Two more rules:

- The validation `details` keep the **full `loc`** list (`["body", "priority"]`), the Pydantic `type` (`"missing"`, `"less_than_equal"`, ...) and the human `msg` under the key `"message"`, in the same order as `exc.errors()`.
- If an `HTTPException` carries `headers` (for example `WWW-Authenticate` on a 401), the enveloped response must still send them: pass `headers=getattr(exc, "headers", None)` to the `JSONResponse`.

`NotFound` is **not** an `HTTPException`: it belongs to the business logic, which should not know about HTTP. The handler is where it becomes a 404.

## Example

```text
GET  /tasks/7                         -> 404 {"error": {"code": "not_found", "message": "Task 7 not found", "details": []}}
GET  /nowhere                         -> 404 {"error": {"code": "http_error", "message": "Not Found", "details": []}}
GET  /secret                          -> 401 {"error": {"code": "http_error", "message": "Login required", "details": []}}
                                             + header WWW-Authenticate: Bearer
POST /tasks {"priority": 9}           -> 422 {"error": {"code": "validation_failed", "message": "Request data is invalid",
                                                "details": [{"loc": ["body", "title"], "type": "missing", "message": "Field required"},
                                                            {"loc": ["body", "priority"], "type": "less_than_equal", "message": "..."}]}}
```

The tests import `app` and `NotFound`, and send requests with `TestClient(app, raise_server_exceptions=False)` so that an exception you do not handle shows up as a 500 instead of crashing the test.
