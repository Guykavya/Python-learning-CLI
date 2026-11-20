## Approach

```python
auth = Blueprint("auth", __name__, url_prefix="/auth")
blog = Blueprint("blog", __name__)


@auth.post("/logout")
def logout():
    return redirect(url_for("blog.index"))


@auth.errorhandler(404)
def auth_not_found(error):
    return "auth 404", 404

...

def create_app():
    app = Flask(__name__)
    app.register_blueprint(auth)
    app.register_blueprint(blog)

    @app.errorhandler(404)
    def app_not_found(error):
        return "app 404", 404

    return app
```

(The complete file is `reference.py`.)

Example: `GET /auth/profile/ravi` matches the route `auth.profile`; the view calls `abort(404)`; Flask looks for a 404 handler first on the blueprint of the request (`auth`), then on the app. `GET /auth/nothing` matches **no** rule: the request has no blueprint, so only the app-level handler is tried.

This is a known limit: *"a blueprint cannot handle 404 for its URL prefix"*. If you want one 404 page per section, check `request.path.startswith("/auth/")` inside the **app-level** handler.

Blueprints keep a growing app tidy: each part has its own routes, names and handlers, `url_for("auth.login")` cannot clash with a `login` in another part, and `url_prefix` can be changed in one place.

## Complexity

Routing is a lookup; blueprints add no cost per request.

## Another way

One app-level 404 handler that looks at `request.path` and answers differently per section: one place, covers unmatched URLs as well. Blueprint handlers are best for errors that your own views raise.

## Not covered

Blueprint templates and static folders, `before_request` per blueprint (`before_app_request` for the whole app).
