## Approach

```python
def envelope(status, code, message, details=None, headers=None):
    body = {"error": {"code": code, "message": message, "details": details or []}}
    return JSONResponse(body, status_code=status, headers=headers)


@app.exception_handler(NotFound)
async def not_found(request: Request, exc: NotFound):
    return envelope(404, "not_found", f"{exc.resource} {exc.item_id} not found")


@app.exception_handler(StarletteHTTPException)
async def http_error(request: Request, exc: StarletteHTTPException):
    return envelope(exc.status_code, "http_error", str(exc.detail), headers=getattr(exc, "headers", None))


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    details = [{"loc": list(e["loc"]), "type": e["type"], "message": e["msg"]} for e in exc.errors()]
    return envelope(422, "validation_failed", "Request data is invalid", details)
```

How FastAPI picks a handler: when an exception escapes an endpoint (or the router), it looks up the exception's class, then its parent classes, in the registered handlers. So:

- `NotFound("Task", 7)` finds the `NotFound` handler.
- `HTTPException(409, ...)` from `fastapi` is a **subclass** of Starlette's `HTTPException`, so the Starlette handler catches it. The router's own 404 for `/nowhere` and 405 for a wrong method are raised as Starlette's class, so registering for the FastAPI subclass would miss them.
- A bad body or path is raised as `RequestValidationError` before the endpoint runs (section 6.1).

Example: `POST /tasks {"priority": 9}` gives two errors from Pydantic, in field order: `title` is missing, `priority` is above 5. They become `[{"loc": ["body", "title"], "type": "missing", ...}, {"loc": ["body", "priority"], "type": "less_than_equal", ...}]`. The `loc` stays complete, so a front end can still put each message next to the right form field.

`details or []` makes `details` always a list, so a client can always loop over it.

## Complexity

O(e) per validation error response, e = number of errors.

## Another way

Make `NotFound` carry its own status and code (`class NotFound(AppError): status = 404; code = "not_found"`), give all domain exceptions one base class `AppError`, and register **one** handler for `AppError` that reads `exc.status` and `exc.code`. Adding a new domain error then needs no new handler.
