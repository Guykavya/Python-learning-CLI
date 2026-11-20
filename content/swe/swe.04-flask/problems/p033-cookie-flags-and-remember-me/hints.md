## Hint 1

Which config names control the three flags and the lifetime? (They all start with `SESSION_COOKIE_` or `PERMANENT_SESSION_`.) And which attribute of `session` decides whether Flask sets `Expires`?

## Hint 2

`session.permanent = True` makes the cookie last `PERMANENT_SESSION_LIFETIME`; `False` makes it a browser-session cookie. A checkbox sends `remember=on` when ticked and nothing when not: compare the string.

## Hint 3

```text
app.config.update(SECRET_KEY, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SECURE=True,
                  SESSION_COOKIE_SAMESITE="Lax", PERMANENT_SESSION_LIFETIME=timedelta(days=14))
app.config.update(test_config or {})        # after the defaults
login: session.clear(); session["user"] = ...; session.permanent = (form.get("remember") == "on")
```
