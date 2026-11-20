## Approach

Declare both methods, branch on `request.method`, validate, escape.

```python
from flask import Flask, request
from markupsafe import escape


def create_app():
    app = Flask(__name__)

    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            if not name:
                return "Name is required", 400
            return f"Thanks, {escape(name)}!"
        return '<form method="post"><input name="name"><button>Send</button></form>'

    return app
```

Example: `PUT /contact` never reaches the function. Flask's router sees that the path exists with other methods and answers 405 itself, adding `Allow: GET, HEAD, OPTIONS, POST`. Flask also adds `HEAD` (same as GET without a body) and `OPTIONS` automatically.

## Complexity

`O(size of the form)`.

## Another way

Two view functions on the same URL: `@app.get("/contact")` for the form and `@app.post("/contact")` for the handler. It reads cleaner when the two parts are long.
