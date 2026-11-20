# Audit and harden an API

The module project, chapter section 17 ("Project: security audit and hardening of an API"), a smaller version of it. `starter.py` holds the **Pagebound shop API** as it was delivered: `build_insecure_app()` builds a small FastAPI service with users, orders and payments. It works, and it has **eight security problems**. Your job is the loop of section 17.3: **find** each problem, read the test that **proves** it (red), **fix** it, watch the test turn **green**.

You write one function in `solution.py`:

```python
def build_hardened_app(clock=time.time, scrypt_n=2**14) -> FastAPI
```

It returns an app with **the same endpoints** as the insecure one and none of the eight problems. Copy `build_insecure_app` into your function (or call helpers from it) and change it. Do not break what works: the tests also check that the legitimate flows still work.

## The contract that must not change

| Endpoint | Behaviour |
|---|---|
| `POST /register` `{"name", "password"}` | `2xx` with `{"id": <int>}`; also creates the user's account row with `100000` cents |
| `POST /login` `{"name", "password"}` | `200` with `{"access_token": "<JWT>"}`; failure is an error |
| `POST /orders` `{"total_cents"}` | `2xx` with `{"id"}`; needs `Authorization: Bearer <token>` |
| `GET /orders/{id}` | the order as JSON `{"id", "owner_id", "total_cents"}`; needs the token |
| `POST /payments` `{"amount_cents"}` | `201` with `{"payment_id"}`; debits `accounts.balance_cents`; `402` if the balance is too small |
| `GET /logout?next=...` | a redirect (3xx) with a `Location` header |

`app.state.db` is the SQLite connection with the four tables of the starter (`users`, `orders`, `accounts`, `payments`); the tests read `users.password_hash`, `accounts.balance_cents` and count `payments`. `clock()` returns the current time in seconds: **every** time-based rule (token expiry, the login throttle) must use it, never `time.time()`. `scrypt_n` is the scrypt cost: the tests pass `2**10` so that they stay fast; its default must stay `2**14` or more.

## The eight findings (each is a test group: `test_f1_...` to `test_f8_...`)

1. **Login: enumeration and throttling** (chapter 2.5 and 11.5). Unknown name and wrong password must give the same status (`401`) and the same body. After **5 failed attempts for one name within 60 seconds** the next attempt, even with the right password, is `429` with `Retry-After` (whole seconds, 1 to 60). It also applies to names that do not exist. Failures older than 60 seconds stop counting; successful logins never count; another user is not affected.
2. **Passwords** (chapter 2). `users.password_hash` must not be the password or a plain SHA-256/MD5/SHA-1 of it. Use `hashlib.scrypt` with a random salt per password (two users with the same password get different values), compare with `hmac.compare_digest`.
3. **Tokens** (chapter 4). The token needs `exp` at most one hour ahead (`exp` and `sub` as in swe.05: `sub` is the user id as text). Valid while `clock() < exp`, refused (`401`) when `clock() >= exp`. PyJWT checks `exp` against the real clock, so pass `options={"verify_exp": False}` and compare with `clock()` yourself. The signing key must not be guessable: a token signed with `"secret"` must be refused. Always `algorithms=["HS256"]`.
4. **Order access, IDOR** (chapter 8). A user reads only their own orders. Another user's order and a missing order both answer `404` with the same body; no token is `401`.
5. **Payments** (chapter 13). `POST /payments` needs an `Idempotency-Key` header (`400` without it). The same key and the same amount from the same user charges **once** and returns the same `payment_id`; the same key with another amount is `422`; a different key is a new payment; keys are per user.
6. **Redirects** (chapter 14.8). `/logout?next=` is followed only for a **local path** (`/orders`, `/orders?page=2`) or an absolute `http(s)` URL whose host is exactly in `ALLOWED_HOSTS` (`shop.example`). Anything else (including `//evil.example`, `/\evil.example`, `https://shop.example.evil.example/`, `https://shop.example@evil.example/`, `javascript:...`) redirects to `/`.
7. **Logs** (chapter 15.6). No log line may contain a password (right or wrong) or an access token. The failed login itself must still be logged with the user name.
8. **Errors** (chapter 9.4 and 15.7). Every error response, from your own `HTTPException`s, from validation, from unknown routes and from unexpected crashes, is JSON with a text under `"error"`, and never a stack trace (`"trace"`, `Traceback`, `File "..."`) or internal details. Bad input (`{}`, `{"total_cents": "abc"}`) is a `4xx` produced by a validation model, not a `500`.

## How to work

1. Run `learn check swe.07.p035` first. With the starter, many tests fail: that is the audit report. Each failing test message names the problem.
2. Fix one finding at a time and run the tests again. Do not try to fix all eight at once.
3. Read `build_insecure_app` once as an auditor, with the six questions of chapter 1.4 beside you (who is calling, may they do this to this object, is every input checked, what can this cost, what if it is called twice, what do we log and leak).

The tests import `build_hardened_app`. Some things stay out of scope on purpose (rate limits on other endpoints, HTTPS, security headers, a real secret store): list them in your head as the "remaining risks" of chapter 17.9.
