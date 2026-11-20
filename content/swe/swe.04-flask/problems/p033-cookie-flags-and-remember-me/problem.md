# Cookie flags and remember-me

Chapter sections 16.5 and 16.7. A session cookie needs flags:

| Flag | Meaning |
|---|---|
| `HttpOnly` | JavaScript cannot read the cookie (limits what an XSS can steal) |
| `Secure` | sent only over HTTPS |
| `SameSite=Lax` | not sent on cross-site POSTs and embedded requests (helps against CSRF) |
| `Expires` | without it the cookie is a **session cookie**: gone when the browser closes |

In `solution.py` write `create_app(test_config=None)` with the factory's **default** config:

- `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SECURE = True`, `SESSION_COOKIE_SAMESITE = "Lax"`, `PERMANENT_SESSION_LIFETIME = timedelta(days=14)`. `test_config` is applied after and may override them.
- `POST /login` with form fields `username` and (optional) `remember`: store `session["user"] = username` after clearing the session. When `remember=on` the session is **permanent** (cookie lasts 14 days, `Expires` is set); otherwise it is a **session cookie** (no `Expires`). Answer `ok`.
- `POST /logout`: clear the session and answer `bye`; the browser must be told to delete the cookie.

The tests read the `Set-Cookie` header.

## Example

```text
POST /login username=asha remember=on  -> Set-Cookie: session=...; Expires=<in 14 days>; Secure; HttpOnly; Path=/; SameSite=Lax
POST /login username=asha              -> Set-Cookie: session=...; Secure; HttpOnly; Path=/; SameSite=Lax   (no Expires)
```
