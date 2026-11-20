## Hint 1

A handler is an `async def` function with `(request, exc)` decorated with `@app.exception_handler(SomeException)`. Whatever response it returns is sent instead of the default. Which exception class does FastAPI raise for an unknown route: `fastapi.HTTPException` or `starlette.exceptions.HTTPException`? (Section 8.2, "Three things to notice".)

## Hint 2

Write `envelope()` once and call it from all three handlers. For validation, `exc.errors()` is a list of dicts with keys `loc` (a tuple), `type` and `msg`. JSON has no tuples, so use `list(e["loc"])`.

## Hint 3

```text
envelope(status, code, message, details=None, headers=None):
    body = {"error": {"code": code, "message": message, "details": details or []}}
    return JSONResponse(body, status_code=status, headers=headers)

@exception_handler(NotFound)              -> envelope(404, "not_found", f"{exc.resource} {exc.item_id} not found")
@exception_handler(StarletteHTTPException) -> envelope(exc.status_code, "http_error", str(exc.detail),
                                                       headers=getattr(exc, "headers", None))
@exception_handler(RequestValidationError) -> details = [{"loc": list(e["loc"]), "type": e["type"], "message": e["msg"]}
                                                         for e in exc.errors()]
                                              envelope(422, "validation_failed", "Request data is invalid", details)
```
