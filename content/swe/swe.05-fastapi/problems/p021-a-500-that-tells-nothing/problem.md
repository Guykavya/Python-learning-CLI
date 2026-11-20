# A 500 that tells nothing

Chapter sections 8.2 (exception handlers) and 8.4 (unhandled exceptions are 500s). Logging with `logging` is core Python.

When code crashes, two people need two different things:

- The **client** must learn *nothing* about the inside: no exception name, no message (it may contain a password or a SQL query), no traceback. Only "something went wrong" and an id to quote when reporting it.
- The **developer** needs *everything*: the full traceback, which request it was, and the same id, so the support ticket "error 3f9c1a..." can be found in the log.

Write `create_app(new_id=None)` that returns a FastAPI app with a **catch-all handler** for `Exception`:

1. Make a request id: `rid = new_id()`. When `new_id` is `None`, use a default that makes a fresh random id each call (for example `lambda: secrets.token_hex(8)`). The tests pass their own `new_id` to get predictable ids.
2. Log at level **ERROR** on the logger **`logging.getLogger("tasks_api")`** a message that contains the request id, the method and the path, **with the traceback attached**. Inside an exception handler you are not in an `except` block, so pass the exception yourself: `logger.error("...", ..., exc_info=exc)`.
3. Answer **500** with exactly this JSON and a header `X-Request-ID: <rid>`:

```json
{"error": {"code": "internal_error", "message": "Internal server error", "request_id": "<rid>"}}
```

Everything that is *not* a crash must stay as before: an `HTTPException(404)` is still a normal 404 `{"detail": ...}`, and a bad parameter is still a 422.

The starter has three endpoints:

- `GET /tasks/{task_id}`: 200 for id 1, `HTTPException(404, "Task not found")` otherwise.
- `GET /report`: raises `RuntimeError("database refused login: password=hunter2")`, a realistic message that must never reach a client.
- `GET /ratio?a=..&b=..`: returns `a / b`, so `b=0` raises `ZeroDivisionError`.

## Example

```text
create_app(new_id=lambda: "req-42")
GET /report  -> 500 {"error": {"code": "internal_error", "message": "Internal server error", "request_id": "req-42"}}
                X-Request-ID: req-42
log (tasks_api, ERROR): "Unhandled error req-42 on GET /report"  + the RuntimeError traceback
GET /tasks/9 -> 404 {"detail": "Task not found"}      (unchanged)
```

The tests use `TestClient(app, raise_server_exceptions=False)` (section 8.4) to see the 500 a real user would get, and pytest's `caplog` fixture to read the log records.
