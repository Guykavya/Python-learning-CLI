## Hint 1

What must the attacker's page **not** be able to know? Where can you keep a value that the browser sends with every request (a cookie) but that a *form on another site* cannot reproduce in a field?

## Hint 2

The session cookie travels automatically, so it cannot be the proof. The proof is a second copy of a secret: one in the session (the server's memory of it) and one in the form/header (which only a page that **read your form** can know). Compare them in a `before_request` hook; `abort(400)` ends the request.

## Hint 3

```text
def csrf_token(): create session["csrf_token"] = secrets.token_urlsafe(32) if missing; return it
app.jinja_env.globals["csrf_token"] = csrf_token

@app.before_request
def check():
    if method in GET/HEAD/OPTIONS: return
    sent = form["csrf_token"] or header X-CSRF-Token
    expected = session.get("csrf_token")
    if not sent or not expected or not hmac.compare_digest(sent.encode(), expected.encode()): abort(400)
```
