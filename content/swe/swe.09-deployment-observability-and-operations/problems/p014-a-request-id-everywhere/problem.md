# A request id everywhere

Chapter sections 5.1 (the `RequestContext` middleware), 8.2 (the request ID) and 8.4 (trace one failing request). Write the **pure ASGI middleware** that gives every request an id and makes the id the thread through the logs.

## What to write

`request_id_var`, `VALID_ID`, `QUIET_PATHS` and `log = logging.getLogger("pagebound")` are given in the starter. Write `RequestContext.__call__`:

```python
class RequestContext:
    def __init__(self, app): ...
    async def __call__(self, scope, receive, send): ...
```

For a request of type `"http"` (anything else, such as `"lifespan"`, goes straight to the app):

1. **The id.** Read the `X-Request-ID` request header. If it matches `VALID_ID` (`^[A-Za-z0-9._-]{8,64}$`), reuse it; otherwise make a new one with `uuid.uuid4().hex` (32 hex characters). Never trust a client-supplied id blindly: a value with spaces, newlines or 10,000 characters must not reach the logs.
2. **The context variable.** Set `request_id_var` to the id for the whole request, so that any `log.info(...)` in the application can include it, and **reset** it at the end (use the token that `set` returns).
3. **The response header.** Add `X-Request-ID: <id>` to every response (on the `http.response.start` message), also to error responses.
4. **Unhandled errors.** If the application raises an exception, log it with `log.exception("unhandled error")` (full traceback, at level ERROR) and answer **500** with the JSON body `{"error": "internal error", "request_id": "<id>"}`. The client gets **only** the id: no exception text, no traceback.
5. **One log line per request**: after the response, `log.info("request finished", extra={"fields": {"method": ..., "path": ..., "status": ..., "duration_ms": ...}})`, where `duration_ms` is the time taken in milliseconds, rounded to one decimal. `status` is the status that was sent (`500` for an unhandled error). **Do not log** the paths in `QUIET_PATHS` (health probes and metrics scrapes would bury the real events). Write this line **before** resetting the variable, so that it carries the request's id.

Use `fastapi.responses.JSONResponse` for the error answer: `await response(scope, receive, send_with_id)`.

## Example

```python
app.add_middleware(RequestContext)
# GET /orders/7 with the header X-Request-ID: trace-me-0001
#   -> response header x-request-id: trace-me-0001
#   -> log record "request finished" with fields {"method": "GET", "path": "/orders/7", "status": 200, "duration_ms": 1.2}
# GET /boom (the app raises RuntimeError("simulated bug"))
#   -> status 500, body {"error": "internal error", "request_id": "<id>"}
#   -> an ERROR record "unhandled error" with the traceback, then the "request finished" record with status 500
```

The tests build a small FastAPI app around your middleware and read the records with `caplog`.
