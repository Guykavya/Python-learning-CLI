## Approach

Store a random token in the session, print it in every form, and compare on every unsafe request.

```python
import hmac
import secrets

from flask import Flask, abort, render_template_string, request, session

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def create_app(test_config=None):
    ...

    def csrf_token():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_urlsafe(32)
        return session["csrf_token"]

    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    def check_csrf():
        if request.method in SAFE_METHODS:
            return
        sent = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token", "")
        expected = session.get("csrf_token", "")
        if not sent or not expected or not hmac.compare_digest(sent.encode(), expected.encode()):
            abort(400, description="Bad or missing CSRF token.")
```

Example: the attacker's page auto-submits a form to `/deposit`. The browser attaches the victim's session cookie, but the form cannot contain the victim's token (the attacker cannot read the `/form` page of another origin), so the hook answers 400 before the view runs.

Three details the tests check:

- **Empty tokens never match.** Without `not sent or not expected`, a visitor without a session who sends `csrf_token=` would compare `""` with `""` and pass.
- **`compare_digest` on bytes.** On `str` it raises `TypeError` for non-ASCII input: an attacker could turn your 400 into a 500. It also takes the same time wherever the strings differ, so the token cannot be guessed character by character from timing.
- **Unsafe methods only, and GET never changes data.** The check cannot protect a GET that changes data, because a GET can be fired by an `<img src>`.

## Complexity

`O(token length)` per request.

## Another way

Flask-WTF's `CSRFProtect` does this (plus signed, time-limited tokens). Or a **double-submit cookie**. Also set `SameSite=Lax` on the session cookie (problem 33): browsers then refuse to send it on cross-site POSTs. Use both: the token is the defence in depth.

## Not covered

JSON APIs that authenticate with a header token (not a cookie) are not open to CSRF, because the browser does not attach that header by itself.
