## Approach

```python
class RequestContext:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        incoming = dict(scope["headers"]).get(b"x-request-id", b"").decode("latin-1")
        rid = incoming if VALID_ID.match(incoming) else uuid.uuid4().hex
        token = request_id_var.set(rid)
        started, status = time.perf_counter(), 500

        async def send_with_id(message):
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                message.setdefault("headers", []).append((b"x-request-id", rid.encode()))
            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
        except Exception:
            log.exception("unhandled error")
            response = JSONResponse({"error": "internal error", "request_id": rid}, status_code=500)
            await response(scope, receive, send_with_id)
        finally:
            if scope["path"] not in QUIET_PATHS:
                log.info("request finished", extra={"fields": {
                    "method": scope["method"], "path": scope["path"], "status": status,
                    "duration_ms": round((time.perf_counter() - started) * 1000, 1)}})
            request_id_var.reset(token)
```

A pure ASGI middleware (not `BaseHTTPMiddleware`) is used on purpose, as in the chapter: it sees the status when the response starts, and it keeps the context variable correct across the whole request. The validation of the incoming id is what keeps a hostile client from writing newlines or a megabyte into your logs.

## Complexity

O(1) work per request: one regular expression match, one header, one log line.

## Another way

`BaseHTTPMiddleware` (`@app.middleware("http")`) is shorter but has known limits with background tasks and context variables. The `asgi-correlation-id` package does the same job. Both approaches follow the rule of chapter 8.2: create the id at the edge, validate it, carry it in a context variable, return it.
