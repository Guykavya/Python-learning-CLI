## Approach

```python
app.config.update(
    SECRET_KEY="dev",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(days=14),
)
app.config.update(test_config or {})

@app.post("/login")
def login():
    session.clear()
    session["user"] = request.form.get("username", "")
    session.permanent = request.form.get("remember") == "on"
    return "ok"
```

Example: with `remember=on` the header becomes `Set-Cookie: session=...; Expires=Thu, 03 Dec 2026 ...; Secure; HttpOnly; Path=/; SameSite=Lax`; without it the `Expires` part is absent and the browser forgets the cookie when it closes.

What each flag buys you: `HttpOnly` means an XSS bug cannot read the cookie with `document.cookie`; `Secure` keeps it off plain HTTP, where anyone on the network could read it; `SameSite=Lax` stops the browser from sending it on forged cross-site POSTs. A longer life (*remember me*) is a trade: a stolen cookie works for 14 days. Offer it as a choice, never by default.

In production behind HTTPS, `Secure` is right. For local development over `http://localhost` browsers make an exception, but a development config may switch it off (as the tests do).

## Complexity

`O(1)`.

## Another way

Store a separate long-lived **remember token** in its own cookie (a random value saved, hashed, in the database) and keep the session itself short; the server can then revoke the token. Flask-Login does it this way.

## Not covered

`SESSION_COOKIE_NAME`, `SESSION_COOKIE_DOMAIN` and cookie prefixes (`__Host-`).
