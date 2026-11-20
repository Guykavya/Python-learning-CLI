# The request lifecycle, in order

Chapter sections 5.5, 5.6 and 19. An app records what happens in a list called `log`. The test client sends four requests; before each one the list is cleared, and after it the program prints the status and the list.

```python
from flask import Flask

app = Flask(__name__)
app.config["PROPAGATE_EXCEPTIONS"] = False     # unhandled errors become 500 pages, as in production
log = []


@app.before_request
def before():
    log.append("before")


@app.after_request
def after(response):
    log.append(f"after {response.status_code}")
    return response


@app.teardown_request
def teardown(exc):
    log.append("teardown " + (type(exc).__name__ if exc else "none"))


@app.errorhandler(404)
def not_found(error):
    log.append("handler 404")
    return "no such page", 404


@app.errorhandler(ValueError)
def bad_value(error):
    log.append("handler ValueError")
    return "bad value", 400


@app.get("/ok")
def ok():
    log.append("view ok")
    return "fine"


@app.get("/value")
def value():
    log.append("view value")
    raise ValueError("oops")


@app.get("/crash")
def crash():
    log.append("view crash")
    raise RuntimeError("boom")


client = app.test_client()
for path in ["/ok", "/missing", "/value", "/crash"]:
    log.clear()
    r = client.get(path)
    print(f"{path}: {r.status_code} -> {', '.join(log)}")
```

Write in `answer.txt` the four lines the program prints (format: `<path>: <status> -> <entries joined by ", ">`). Do not run it. (The real run also writes a traceback for `/crash` to the error stream; ignore it, it is not part of the printed output.)

## After you answer

1. Does `before_request` run for the request `/missing` that matches no route? Why is that useful (or dangerous)?
2. For `/value` the exception was handled by an error handler. Does the teardown function still receive the exception? What about `/crash`?
3. `after_request` ran in all four requests. Name a case in which it does **not** run.
