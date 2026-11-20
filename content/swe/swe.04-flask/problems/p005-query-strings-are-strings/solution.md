## Approach

Let `type=int` handle the parsing and `max`/`min` handle the range.

```python
from flask import Flask, jsonify, request


def create_app():
    app = Flask(__name__)

    @app.get("/items")
    def items():
        page = max(1, request.args.get("page", 1, type=int))
        per_page = min(100, max(1, request.args.get("per_page", 20, type=int)))
        return jsonify(page=page, per_page=per_page, offset=(page - 1) * per_page)

    return app
```

Example: `?per_page=500` gives `int("500") = 500`, `max(1, 500) = 500`, `min(100, 500) = 100`. `?page=abc` gives the default `1` because `int("abc")` fails inside `get`. `?page=2.5` also fails (`int("2.5")` is an error), so the default applies.

Clamping is a **security** rule too: without the upper limit, `?per_page=1000000` would make your server load a million rows for one request.

## Complexity

`O(1)`.

## Another way

Write a small helper `int_arg(name, default, low, high)` and use it in every view, so the clamping rules live in one place.
