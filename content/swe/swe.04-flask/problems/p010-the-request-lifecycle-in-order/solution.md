## Approach

Follow the lifecycle for each request.

```text
/ok: 200 -> before, view ok, after 200, teardown none
/missing: 404 -> before, handler 404, after 404, teardown none
/value: 400 -> before, view value, handler ValueError, after 400, teardown none
/crash: 500 -> before, view crash, after 500, teardown RuntimeError
```

- **/ok.** The straight line: before, view, after, teardown.
- **/missing.** The URL matching failure is stored on the request and raised when Flask tries to run the view; `before_request` has already run. The handler for 404 builds the response; `after_request` still sees it (status 404).
- **/value.** The view raises; Flask looks for a handler for `ValueError` and finds one; it returns a normal response (400), so the request ends *cleanly*: teardown gets `None`.
- **/crash.** No handler for `RuntimeError`, so Flask logs the traceback and builds a generic 500 response. `after_request` runs on that response. The exception is still passed to `teardown_request`, so cleanup code can roll back.

Real output of the program, run with Flask 3.1.3.

## Complexity

Not applicable; this is a reading exercise.

## Another way

Run the same app with `PROPAGATE_EXCEPTIONS = True` (the default in testing): the `RuntimeError` then leaves `client.get` as a Python exception, which is what you want while developing tests.

## Not covered

If a `before_request` hook **returns a value**, the view and the later `before_request` hooks are skipped, but `after_request` and teardown still run (section 5.6).
