## Hint 1

A decorator is a function that takes a view and returns another function. What must the returned function do first, before it calls the original view?

## Hint 2

Inside the wrapper, `g.user` is already set by the `before_request` hook (hooks run before the view). Put `@functools.wraps(view)` on the wrapper so it copies the name of the view. `url_for("login", next=request.path)` builds `/auth/login?next=/dashboard`.

## Hint 3

```text
def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None: return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped

@app.before_request
def load_user(): g.user = USERS.get(session.get("user_id"))
```
