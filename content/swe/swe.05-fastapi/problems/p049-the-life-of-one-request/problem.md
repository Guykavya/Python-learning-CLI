# The life of one request

Chapter sections 6.1 (the request lifecycle), 9.5 (dependencies with `yield`), 13.1 (middleware) and 14 (background tasks). Four pieces of code take part in one request: a middleware, a dependency with `yield` (like a database session), the endpoint, and a background task. Each one appends a line to `log` when it runs. The program makes two requests: one that succeeds and one whose endpoint raises `HTTPException(404)`, and prints the log of each.

```python
from typing import Annotated

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request
from fastapi.testclient import TestClient

app = FastAPI()
log = []


@app.middleware("http")
async def outer(request: Request, call_next):
    log.append("middleware: before")
    response = await call_next(request)
    log.append(f"middleware: after, status {response.status_code}")
    return response


def get_db():
    log.append("dependency: open")
    try:
        yield "db"
        log.append("dependency: commit")
    except HTTPException:
        log.append("dependency: rollback")
        raise
    finally:
        log.append("dependency: close")


def write_audit(path):
    log.append(f"background: audit {path}")


DB = Annotated[str, Depends(get_db)]


@app.get("/ok")
def ok(db: DB, background: BackgroundTasks):
    log.append("endpoint: ok")
    background.add_task(write_audit, "/ok")
    return {"ok": True}


@app.get("/fail")
def fail(db: DB, background: BackgroundTasks):
    log.append("endpoint: fail")
    background.add_task(write_audit, "/fail")
    raise HTTPException(404, "Task not found")


client = TestClient(app)
for path in ("/ok", "/fail"):
    log.clear()
    r = client.get(path)
    print(f"GET {path} -> {r.status_code}")
    for number, line in enumerate(log, 1):
        print(f"  {number}. {line}")
```

Write your answer in `answer.txt`: the lines the program prints, exactly in its format (`GET /ok -> 200`, then the numbered log lines indented by two spaces, then the same for `/fail`). Some lines you might expect may **not** appear at all. Do not run it.

Questions to settle while tracing:

- When does the middleware's code after `await call_next(request)` run: before or after the response body is sent and the background tasks run?
- When does the code after `yield` in the dependency run for a successful request, compared with the background task?
- What happens to the background task that `/fail` added before it raised?

## After you answer

1. In `/ok` the dependency commits **after** the background task ran. Why can this be a problem if the background task reads the database expecting the committed data? What would you change?
2. Why does the middleware see status 404 for `/fail`, although the endpoint never returned a response?
3. The task added by `/fail` never runs. Is that a bug or a sensible rule? Think of a "send confirmation email" task.
