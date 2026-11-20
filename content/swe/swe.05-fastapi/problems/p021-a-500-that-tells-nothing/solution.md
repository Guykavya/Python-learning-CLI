## Approach

```python
def create_app(new_id=None):
    if new_id is None:
        new_id = lambda: secrets.token_hex(8)          # a fresh random id each time
    app = FastAPI()

    @app.exception_handler(Exception)
    async def unhandled(request: Request, exc: Exception):
        rid = new_id()
        # Not inside an except block, so hand the exception to the logger ourselves.
        logger.error("Unhandled error %s on %s %s", rid, request.method, request.url.path, exc_info=exc)
        body = {"error": {"code": "internal_error", "message": "Internal server error", "request_id": rid}}
        return JSONResponse(body, status_code=500, headers={"X-Request-ID": rid})
    ...
```

Why each piece:

- **`Exception` handler.** FastAPI keeps it apart from the others: it is the last line of defence, used only when nothing more specific matched. `HTTPException` (404) and `RequestValidationError` (422) keep their own handlers, so planned answers stay unchanged.
- **`exc_info=exc`.** `logger.exception(...)` reads "the exception currently being handled" from `sys.exc_info()`. By the time FastAPI calls your handler, there is no active `except` block, so it would log the message without a traceback. Passing the exception object attaches its traceback explicitly.
- **The id in both places.** The user quotes `req-42`; the developer searches the log for `req-42` and finds the traceback, the method and the path. Nothing else crosses the boundary.
- **Injected `new_id`.** Random ids are right for production but cannot be asserted in a test; injecting the generator makes the test exact (the same idea as the injected clock in section 9.6).

Example: `GET /report` raises `RuntimeError("database refused login: password=hunter2")`. The client sees `{"error": {"code": "internal_error", ..., "request_id": "req-42"}}`. The log line is `Unhandled error req-42 on GET /report` followed by the traceback that ends in `RuntimeError: database refused login: password=hunter2`. (Logs are also sensitive: in a real system, scrub secrets before they reach the log too.)

`raise_server_exceptions=False`: Starlette sends your handler's response and then **re-raises** the exception so that servers and test clients can see it. `TestClient` by default turns that into a failing test; with `False` it returns the response, which is what a user would receive.

## Complexity

O(1) per request, plus the cost of formatting the traceback in the log.

## Another way

Give **every** request an id in a middleware (section 13.1) and store it in `request.state.request_id`; the error handler then reuses that id instead of making a new one, so the id of a crash matches the id in the access log line of the same request. Problem p036 builds that middleware.
