## Approach

The converter is part of the rule, so the validation happens before your view is called.

```python
from flask import Flask


def create_app():
    app = Flask(__name__)

    @app.route("/user/<username>")
    def user_profile(username):
        return f"User: {username}"

    @app.route("/post/<int:post_id>")
    def show_post(post_id):
        return f"Post {post_id} ({type(post_id).__name__})"

    @app.route("/files/<path:subpath>")
    def show_file(subpath):
        return f"File: {subpath}"

    return app
```

Example: `/post/abc` does not match the rule `/post/<int:post_id>` (the `int` converter's pattern is `\d+`), so no view runs and Flask answers 404. The default converter (`string`) matches any text **without a slash**, which is why `/files/a/b` needs `path`.

## Complexity

Routing is a lookup in Werkzeug's rule map; it does not slow down with your code.

## Another way

`<uuid:token>` and `<float:price>` exist too. For stricter checks (ids above zero) take the `int` and call `abort(404)` in the view.
