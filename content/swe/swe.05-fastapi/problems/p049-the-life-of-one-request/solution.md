## Approach

Follow the request in, then follow the response out, and remember what each layer waits for.

```text
GET /ok -> 200
  1. middleware: before
  2. dependency: open
  3. endpoint: ok
  4. middleware: after, status 200
  5. background: audit /ok
  6. dependency: commit
  7. dependency: close
GET /fail -> 404
  1. middleware: before
  2. dependency: open
  3. endpoint: fail
  4. dependency: rollback
  5. dependency: close
  6. middleware: after, status 404
```

**/ok, the way in (1-3).** The middleware is the outermost layer, so it runs first. FastAPI then solves the endpoint's dependencies: `get_db` runs up to `yield`. Then the endpoint runs and schedules the audit task.

**/ok, the way out (4-7).** `call_next` returns as soon as the inner app has *started* the response (status 200 and headers). So the middleware's "after" line comes next, before the body is even sent. The middleware returns the response; the server sends the body; then the background task runs (section 14: "after the response has been sent"). Last, FastAPI finishes the request and closes the dependency's generator: the code after `yield` (commit, then `finally`) runs **after** the background task.

**/fail.** The endpoint raises `HTTPException(404)`. FastAPI throws that exception into the generator at the `yield` (section 9.5), so `except HTTPException` logs the rollback and re-raises, and `finally` logs the close. Only then does FastAPI's exception handler build the 404 response, and that is what `call_next` gives the middleware (line 6). The background task added before the `raise` is **dropped**: the tasks belong to the response the endpoint would have returned, and the error response is a new one without them.

Real output of the program, run with FastAPI 0.162.0 (Starlette 1.10.0) and Pydantic 2.14.3. The program was run five times with identical output: the order is fixed by how the layers wait for each other, not by timing. The relative order of the `yield` cleanup and the background tasks **has changed between FastAPI versions**, which is why the version is pinned here; trust a run on your own version over memory.

Answer to question 1 of "After you answer": a background task that reads the data written in this request may run **before** the commit and miss it (or, with a real database, see the old state). Commit explicitly in the endpoint (`session.commit()` before returning), as the project in section 22 does, or give the task its own session.

## Complexity

Not applicable; this is a reading exercise.

## Another way

FastAPI 0.162 lets you choose the cleanup time of a `yield` dependency: `Depends(get_db, scope="function")` closes it right after the endpoint returns, **before** the response is sent. With that one change, the `/ok` log becomes: middleware before, open, endpoint, **commit, close**, middleware after, background (measured with the same program). Use it when the cleanup must happen before the client sees the answer. You can also log in a pure ASGI middleware (section 1.2) to see the individual `http.response.start` and `http.response.body` messages and confirm where each step happens.
