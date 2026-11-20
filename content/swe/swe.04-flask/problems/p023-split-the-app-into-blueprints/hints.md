## Hint 1

A blueprint object has the same decorators as the app: `@auth.get(...)`, `@auth.errorhandler(404)`. What differs is where the endpoint name and the URL start. How does Flask know which blueprint a *request* belongs to?

## Hint 2

The blueprint of a request is known only when a **route matched**. So `abort(404)` inside a view reaches that blueprint's handler, but a URL that matches nothing has no blueprint and only the app's handler can answer it. `url_for("blog.index")` includes the blueprint name.

## Hint 3

```text
auth = Blueprint("auth", __name__, url_prefix="/auth")   routes: login, logout, profile; @auth.errorhandler(404)
blog = Blueprint("blog", __name__)                       routes: index, show;              @blog.errorhandler(404)
create_app: register both; @app.errorhandler(404) -> "app 404"
```
