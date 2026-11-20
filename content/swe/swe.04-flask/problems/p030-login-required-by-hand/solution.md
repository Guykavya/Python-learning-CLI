## Approach

```python
import functools

from flask import g, redirect, request, session, url_for


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


@app.before_request
def load_user():
    g.user = USERS.get(session.get("user_id"))
```

Example: `GET /dashboard` anonymous: `load_user` sets `g.user = None`; the router calls `wrapped`; it sees `None` and returns `redirect("/auth/login?next=/dashboard")`. After a successful login the login view will send the user to `next` (see problem 31 for doing that **safely**).

`functools.wraps` copies `__name__`, `__doc__` and sets `__wrapped__`. Flask names an endpoint after the **function name**; without `wraps` every protected view is called `wrapped`, and the second registration raises an `AssertionError` at startup.

The session holds only the **id**; `g.user` is the fresh row for this request. If the user is deleted at noon, their old cookie stops working at once.

## Complexity

`O(1)` per request (plus the user lookup: here a dict, in a real app one primary-key query).

## Another way

Flask-Login provides `login_required`, `current_user` and "remember me". The hand-written version is 10 lines and shows exactly what the library does.

## Not covered

An API should answer `401` with JSON instead of a redirect (problem 34).
