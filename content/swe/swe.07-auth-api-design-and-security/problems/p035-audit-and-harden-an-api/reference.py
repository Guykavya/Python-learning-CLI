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

SECRET = "secret"
ALLOWED_HOSTS = {"shop.example"}
log = logging.getLogger("shop")


def build_insecure_app(clock=time.time, scrypt_n=2**14):
    raise NotImplementedError("the reference solution does not need the insecure app")


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
