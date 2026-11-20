# What does this return value send?

Chapter section 5.1. A view may return a string, a tuple, a dict... and Flask turns each into a full HTTP response. Five views, called with the test client:

```python
from flask import Flask

app = Flask(__name__)


@app.route("/1")
def one():
    return "hello"


@app.route("/2")
def two():
    return "created", 201


@app.route("/3")
def three():
    return "teapot", 418, {"Content-Type": "text/plain", "X-Mode": "tea"}


@app.route("/4")
def four():
    return {"ok": True, "n": 3}


@app.route("/5")
def five():
    return "", 204


client = app.test_client()
for number in range(1, 6):
    r = client.get(f"/{number}")
    body = r.get_data(as_text=True).strip()
    print(f"{number}: {r.status_code} | {r.headers.get('Content-Type')} | {body}")
```

Write in `answer.txt` the five lines that this program prints, in the same format: `<number>: <status> | <Content-Type header> | <body>`. For an empty body the line ends after the last `|`. Do not run it.

Watch the exact `Content-Type` text (does it have a charset?) and the exact JSON text of view 4.

## After you answer

1. Why does view 3 show `text/plain` and not `text/html; charset=utf-8`?
2. In view 4, which part of Flask turned the dict into JSON? Why is the text `{"n":3,"ok":true}` and not `{"ok": true, "n": 3}`?
3. View 5 sends a `Content-Type` although the body is empty. Is that a problem?
