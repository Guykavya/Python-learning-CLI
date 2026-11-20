## Approach

Look at what the three parts are, then reason from "who has the key".

```python
from itsdangerous import base64_decode

payload, stamp, signature = cookie.split(".")
print(base64_decode(payload))                          # b'{"role":"member","user_id":7}'
print(int.from_bytes(base64_decode(stamp), "big"))     # seconds since 1970 when it was signed
```

Example: the decoded payload is `{"role":"member","user_id":7}`; the timestamp is the date the cookie was made. The 20 bytes of the signature are an HMAC-SHA1 of `payload.timestamp` under a key derived from `SECRET_KEY`.

See `answer.md` for the full model answer and the checklist. The one-line summary: **a signed cookie is tamper-proof but not secret**; so it carries a pointer (the user id), not data, and the key must stay secret.

## Complexity

Not applicable.

## Another way

**Server-side sessions** (Flask-Session): the cookie holds a random id and the data lives in Redis or the database. The user cannot read it, and you can end a session from the server (log a user out everywhere). The price: a lookup per request and storage to run. Signed cookies are enough for most small apps.

## Not covered

How `SESSION_COOKIE_HTTPONLY`, `Secure` and `SameSite` protect the cookie in the browser (problem 33).
