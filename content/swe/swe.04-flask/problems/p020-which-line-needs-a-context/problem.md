# Which line needs a context?

Chapter sections 10.1 to 10.4. `request`, `session`, `g` and `current_app` are not real globals: they work only while the right **context** is pushed. Ten small functions run in a script (no server). Each one is called inside `try/except RuntimeError`.

```python
from flask import Flask, current_app, g, request, session, url_for

app = Flask(__name__)
app.config["SECRET_KEY"] = "k"


@app.route("/hi")
def hi():
    return "hi"


def run(number, action):
    try:
        action()
    except RuntimeError:
        print(f"{number}: RuntimeError")
    else:
        print(f"{number}: ok")


def line1():
    app.config["SECRET_KEY"]


def line2():
    current_app.name


def line3():
    with app.app_context():
        current_app.name


def line4():
    with app.app_context():
        request.path


def line5():
    with app.test_request_context("/hi?x=1"):
        request.args["x"]


def line6():
    url_for("hi")


def line7():
    with app.app_context():
        url_for("hi")


def line8():
    with app.app_context():
        g.counter = 1
        g.counter


def line9():
    with app.app_context():
        session.get("user")


def line10():
    with app.test_request_context("/hi"):
        url_for("hi")


for n, f in enumerate([line1, line2, line3, line4, line5, line6, line7, line8, line9, line10], 1):
    run(n, f)
```

Write in `answer.txt` the ten lines the program prints (`1: ok` or `1: RuntimeError`, and so on). Do not run it.

## After you answer

1. Which two kinds of context exist, and what does each one add (`current_app`, `g` on one side; `request`, `session` on the other)?
2. Line 7: an app context exists, so why can `url_for` still not build a URL? What config value changes that?
3. Where do background threads, scripts and `flask shell` get a context from?
