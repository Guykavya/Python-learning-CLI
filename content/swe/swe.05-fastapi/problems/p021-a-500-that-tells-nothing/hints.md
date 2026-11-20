## Hint 1

Which handler catches "any exception nobody else handles"? Register one for the base class `Exception` (section 8.2 shows the decorator). `HTTPException` and `RequestValidationError` already have their own handlers inside FastAPI, and the most specific handler wins, so they are not affected.

## Hint 2

Split what goes where. The **log** gets: the id, `request.method`, `request.url.path`, and the exception (`exc_info=exc`, because `logger.exception()` only works inside an `except` block). The **response** gets: only the id. Call `new_id()` inside the handler, once per crash.

## Hint 3

```text
create_app(new_id=None):
    if new_id is None: new_id = lambda: secrets.token_hex(8)
    app = FastAPI()

    @app.exception_handler(Exception)
    async def unhandled(request, exc):
        rid = new_id()
        logger.error("Unhandled error %s on %s %s", rid, request.method, request.url.path, exc_info=exc)
        body = {"error": {"code": "internal_error", "message": "Internal server error", "request_id": rid}}
        return JSONResponse(body, status_code=500, headers={"X-Request-ID": rid})
    ... endpoints ...
    return app
```
