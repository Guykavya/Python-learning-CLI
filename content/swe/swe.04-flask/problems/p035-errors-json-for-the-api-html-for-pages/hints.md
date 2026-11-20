## Hint 1

Which exception class do *all* HTTP errors share (404, 405, 403 raised by `abort` or by the router)? And which class do *all other* exceptions share? A handler registered for a class catches its subclasses.

## Hint 2

One small function can build both shapes: it looks at `request.path` and returns `jsonify(...)` with a status code or the HTML page. Werkzeug's exception object has `.code` and `.name` (`"Not Found"`) and `.get_response()` whose headers include `Allow` for a 405. For the unexpected case, `app.logger.exception(...)` writes the traceback to the log.

## Hint 3

```text
def error_response(status, name, allow=None): JSON if path starts with /api/ else HTML; copy Allow
@app.errorhandler(HTTPException): return error_response(e.code, e.name, e.get_response().headers.get("Allow"))
@app.errorhandler(Exception):     app.logger.exception(...); return error_response(500, "Internal Server Error")
```
