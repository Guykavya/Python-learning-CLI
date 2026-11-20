## Approach

Work through the findings in the order of the hints. The complete hardened app (the insecure `build_insecure_app` stays in the starter and is not needed):

```python
import base64
import hashlib
import hmac
import logging
import math
import os
import secrets
import sqlite3
import threading
import time
import traceback
from urllib.parse import urlparse

import jwt
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

ALLOWED_HOSTS = {"shop.example"}
log = logging.getLogger("shop")

HARDENED_SECRET = secrets.token_urlsafe(48)           # random per process; real systems read it from the environment
TOKEN_LIFETIME = 900
FAIL_LIMIT, FAIL_WINDOW = 5, 60


def hash_password(password, n):
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=n, r=8, p=1, maxmem=2**26)
    return f"scrypt${n}$" + base64.b64encode(salt).decode() + "$" + base64.b64encode(digest).decode()


def verify_password(password, stored):
    try:
        _, n, salt, digest = stored.split("$")
        actual = hashlib.scrypt(password.encode(), salt=base64.b64decode(salt), n=int(n), r=8, p=1, maxmem=2**26)
    except ValueError:
        return False
    return hmac.compare_digest(actual, base64.b64decode(digest))


def safe_next(target):
    if not target or "\\" in target:
        return "/"
    parts = urlparse(target)
    if not parts.scheme and not parts.netloc:
        return target if target.startswith("/") and not target.startswith("//") else "/"
    if parts.scheme in ("http", "https") and parts.hostname in ALLOWED_HOSTS:
        return target
    return "/"


class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=64)
    password: str = Field(min_length=12, max_length=256)


class LoginIn(BaseModel):
    name: str = Field(max_length=64)
    password: str = Field(max_length=256)


class OrderIn(BaseModel):
    total_cents: int = Field(gt=0, le=10_000_000)


class PaymentIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amount_cents: int = Field(gt=0, le=1_000_000)


def build_hardened_app(clock=time.time, scrypt_n=2**14):
    app = FastAPI()
    dummy_hash = hash_password("a dummy password so that unknown names cost the same time", scrypt_n)
    db = sqlite3.connect(":memory:", check_same_thread=False)
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT UNIQUE, password_hash TEXT);
        CREATE TABLE orders (id INTEGER PRIMARY KEY, owner_id INTEGER, total_cents INTEGER);
        CREATE TABLE accounts (user_id INTEGER PRIMARY KEY, balance_cents INTEGER);
        CREATE TABLE payments (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount_cents INTEGER);
    """)
    app.state.db = db
    lock = threading.Lock()
    failures = {}                                       # name -> times of recent failed logins
    payment_keys = {}                                   # (user_id, key) -> (amount_cents, payment_id)

    @app.exception_handler(StarletteHTTPException)
    async def on_http_error(request: Request, exc: StarletteHTTPException):
        return JSONResponse({"error": str(exc.detail)}, status_code=exc.status_code, headers=getattr(exc, "headers", None))

    @app.exception_handler(RequestValidationError)
    async def on_invalid(request: Request, exc: RequestValidationError):
        return JSONResponse({"error": "invalid request"}, status_code=422)

    @app.exception_handler(Exception)
    async def on_error(request: Request, exc: Exception):
        incident = secrets.token_hex(4)
        log.error("incident %s: %s", incident, traceback.format_exc())                  # details go to the log ...
        return JSONResponse({"error": f"internal error (incident {incident})"}, status_code=500)   # ... not to the client

    def current_user(authorization: str = Header(default="")):
        try:
            claims = jwt.decode(authorization.removeprefix("Bearer "), HARDENED_SECRET, algorithms=["HS256"],
                                options={"verify_exp": False, "require": ["sub", "exp"]})
            if clock() >= claims["exp"]:
                raise HTTPException(401, "invalid token")
            user_id = int(claims["sub"])
        except (jwt.PyJWTError, ValueError):
            raise HTTPException(401, "invalid token")
        row = db.execute("SELECT id, name FROM users WHERE id = ?", (user_id,)).fetchone()
        if row is None:
            raise HTTPException(401, "invalid token")
        return dict(row)

    @app.post("/register", status_code=201)
    def register(body: RegisterIn):
        try:
            cur = db.execute("INSERT INTO users (name, password_hash) VALUES (?, ?)", (body.name, hash_password(body.password, scrypt_n)))
        except sqlite3.IntegrityError:
            raise HTTPException(409, "that name is taken")
        db.execute("INSERT INTO accounts VALUES (?, 100000)", (cur.lastrowid,))
        db.commit()
        return {"id": cur.lastrowid}

    @app.post("/login")
    def login(body: LoginIn):
        now = clock()
        with lock:
            recent = [t for t in failures.get(body.name, []) if now - t < FAIL_WINDOW]
            failures[body.name] = recent
            if len(recent) >= FAIL_LIMIT:
                wait = max(1, math.ceil(min(recent) + FAIL_WINDOW - now))
                raise HTTPException(429, "too many attempts, try again later", headers={"Retry-After": str(wait)})
        row = db.execute("SELECT * FROM users WHERE name = ?", (body.name,)).fetchone()
        stored = row["password_hash"] if row else dummy_hash               # same work for unknown names
        if not (verify_password(body.password, stored) and row is not None):
            with lock:
                failures.setdefault(body.name, []).append(now)
            log.warning("failed login for user %r", body.name)
            raise HTTPException(401, "invalid name or password")
        claims = {"sub": str(row["id"]), "iat": int(now), "exp": int(now) + TOKEN_LIFETIME}
        return {"access_token": jwt.encode(claims, HARDENED_SECRET, algorithm="HS256")}

    @app.post("/orders", status_code=201)
    def create_order(body: OrderIn, user: dict = Depends(current_user)):
        cur = db.execute("INSERT INTO orders (owner_id, total_cents) VALUES (?, ?)", (user["id"], body.total_cents))
        db.commit()
        return {"id": cur.lastrowid}

    @app.get("/orders/{order_id}")
    def get_order(order_id: int, user: dict = Depends(current_user)):
        row = db.execute("SELECT * FROM orders WHERE id = ? AND owner_id = ?", (order_id, user["id"])).fetchone()
        if row is None:
            raise HTTPException(404, "order not found")                       # also for other people's orders
        return dict(row)

    @app.post("/payments", status_code=201)
    def pay(body: PaymentIn, user: dict = Depends(current_user), idempotency_key: str | None = Header(default=None)):
        if not idempotency_key:
            raise HTTPException(400, "the Idempotency-Key header is required")
        with lock:
            seen = payment_keys.get((user["id"], idempotency_key))
            if seen is not None:
                if seen[0] != body.amount_cents:
                    raise HTTPException(422, "this Idempotency-Key was already used with a different request")
                return {"payment_id": seen[1]}                                # replay: no second charge
            cur = db.execute("UPDATE accounts SET balance_cents = balance_cents - ? WHERE user_id = ? AND balance_cents >= ?",
                             (body.amount_cents, user["id"], body.amount_cents))
            if cur.rowcount == 0:
                raise HTTPException(402, "insufficient funds")
            pid = db.execute("INSERT INTO payments (user_id, amount_cents) VALUES (?, ?)", (user["id"], body.amount_cents)).lastrowid
            db.commit()
            payment_keys[(user["id"], idempotency_key)] = (body.amount_cents, pid)
            return {"payment_id": pid}

    @app.get("/logout")
    def logout(next: str = "/"):
        return RedirectResponse(safe_next(next))

    return app
```

What each part answers:

1. **Login.** `failures` remembers the times of failed attempts per typed name (existing or not); old ones fall out of the 60-second window by the injected clock; five left means `429` with `Retry-After` computed from the oldest failure. An unknown name is verified against `dummy_hash`, so it costs the same work and gives the same `401` body. The failure is logged with the name only. Throttling (not locking) keeps an attacker from locking Asha out for ever.
2. **Passwords.** scrypt with a random 16-byte salt, the parameters stored in the string so they can be raised later, `hmac.compare_digest` for the comparison.
3. **Tokens.** A random key per process (in real life: a long secret from the environment that the app refuses to start without), `exp` 15 minutes ahead, `algorithms=["HS256"]` and `require` so unsigned and incomplete tokens fail. PyJWT's own expiry check is switched off so that `clock()` decides.
4. **Orders.** The ownership check is inside the query (`AND owner_id = ?`), so a foreign order and a missing order are the same `404`.
5. **Payments.** The key table and the debit sit under one lock, so two simultaneous identical requests cannot both charge (problem p032 explains the full protocol, including the "in progress" case and the database version with a unique constraint).
6. **Redirects.** Reject backslashes; a target without scheme and host must start with exactly one `/`; an absolute URL is accepted only if `parts.hostname` is exactly in `ALLOWED_HOSTS` (`urlparse` reads the host after the `@`, so `shop.example@evil.example` is `evil.example`).
7. **Logs.** Passwords and tokens are simply never passed to the logger.
8. **Errors.** One handler per class of error, all returning `{"error": ...}`. The 500 handler logs the traceback with an incident id and sends only the id.

## Complexity

Each request is O(1) except the password hash, which is deliberately slow (about 0.1 s at the default `2**14`). The in-memory dictionaries (`failures`, `payment_keys`) are per process: several workers need a shared store (chapter 11.6), and the payment keys belong in a table with a unique constraint.

## Another way

Put the shared parts in dependencies and middleware instead of repeating checks: a `current_user` dependency (as here), a rate-limit dependency per route (problem p028), and a small `Repository` class that always filters by `owner_id`, so that "forgetting the ownership check" becomes impossible by construction. Move the settings (secret, token lifetime, limits) into one config object read from the environment.

## Remaining risks

Even the hardened app has open points, and a real report lists them (chapter 17.9): HTTPS and security headers are not set, the in-memory state is lost on restart, there is no password policy beyond a length, no logout or token revocation (a stolen token works until it expires), no refresh tokens, no rate limit on `/register`, and the throttle keys on the typed name only (an attacker can try one password against many names).
