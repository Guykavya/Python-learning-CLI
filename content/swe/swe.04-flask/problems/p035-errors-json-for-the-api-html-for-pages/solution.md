## Approach

```python
from werkzeug.exceptions import HTTPException


def error_response(status, name, allow=None):
    if request.path.startswith("/api/"):
        response = jsonify(error={"code": name.lower().replace(" ", "_"), "message": name})
        response.status_code = status
    else:
        response = app.make_response((render_template_string(PAGE, status=status, name=name), status))
    if allow:
        response.headers["Allow"] = allow
    return response


@app.errorhandler(HTTPException)
def http_error(error):
    allow = error.get_response().headers.get("Allow")
    return error_response(error.code, error.name, allow)


@app.errorhandler(Exception)
def unexpected_error(error):
    app.logger.exception("unhandled exception on %s", request.path)
    return error_response(500, "Internal Server Error")
```

Example: `GET /api/missing` raises `NotFound` inside the router; Flask finds the handler for `HTTPException` (the nearest class in the exception's ancestry), which answers JSON because the path starts with `/api/`. `GET /boom` raises `RuntimeError`; only the `Exception` handler matches; it logs the full traceback (including `hunter2`) to the **log**, and tells the client only `500 Internal Server Error`.

Why the strict "no leaks" rule? Error pages with tracebacks give an attacker file paths, library versions, SQL, and sometimes secrets. The log is for you; the response is for the client.

Why JSON under `/api/`? A JavaScript client that calls `response.json()` on an HTML error page throws a parse error that hides the real problem (a 404).

## Complexity

`O(1)` per error.

## Another way

Put the API in a **blueprint** and use `app_errorhandler` plus a check of `request.blueprint`, or use `Accept` header negotiation (`request.accept_mimetypes.best == "application/json"`) instead of the path. In production an error-tracking service (Sentry) receives the exception in the `Exception` handler.

## Not covered

Custom exception classes for your domain (`class OutOfStock(Exception)`) with their own handlers (section 19.2).
