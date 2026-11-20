## Hint 1

Start with the foundations, in this order: (a) Pydantic models for every body, (b) one set of error handlers, (c) a real secret and the expiry check, (d) a password hash function. Then the access rules (orders, payments), then the small ones (redirect, logs). Which of the eight findings can you prove with a one-line change, and which need new state (the failure list for the throttle, the table of payment keys)?

## Hint 2

For each finding ask what the test needs, not what the textbook says. 1: a dict `name -> list of failure times`, filtered with `now - t < 60`. 3: `jwt.decode(..., options={"verify_exp": False, "require": ["sub", "exp"]})` and then `if clock() >= claims["exp"]`. 4: one extra condition in the SQL. 5: a dict `(user_id, key) -> (amount, payment_id)`, guarded by a `threading.Lock`. 8: three handlers: `StarletteHTTPException` (also covers unknown routes), `RequestValidationError`, `Exception`.

## Hint 3

```text
handlers: http error -> {"error": detail}, keep exc.headers (Retry-After!); validation -> {"error": "invalid request"}, 422; any other -> log traceback, {"error": "internal error"}, 500
hash: "scrypt$<n>$<salt_b64>$<hash_b64>", random salt, hmac.compare_digest; for an unknown name verify against a DUMMY hash
login: drop failures older than 60 s; if 5 left -> 429 + Retry-After; verify; on failure append now, log the NAME only, 401 "invalid name or password"
token: {"sub": str(id), "iat": ..., "exp": int(clock()) + 900}, signed with secrets.token_urlsafe(48)
orders: WHERE id = ? AND owner_id = ?  -> no row -> 404
payments: header required; under a lock: known key? same amount -> replay, other amount -> 422; else debit + insert + remember
logout: reject backslash; no scheme and no host -> must start with one "/"; http(s) -> hostname in ALLOWED_HOSTS
```
