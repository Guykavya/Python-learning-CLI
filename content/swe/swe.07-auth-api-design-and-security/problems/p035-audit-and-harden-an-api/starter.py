"""The Pagebound shop API as it was delivered: it works, and it has eight security problems.

Read build_insecure_app like an auditor. Then write build_hardened_app at the bottom.
"""
import hashlib
import logging
import sqlite3
import time
import traceback

import jwt
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse

SECRET = "secret"
ALLOWED_HOSTS = {"shop.example"}
log = logging.getLogger("shop")


def build_insecure_app(clock=time.time, scrypt_n=2**14):
    app = FastAPI()
    db = sqlite3.connect(":memory:", check_same_thread=False)
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT UNIQUE, password_hash TEXT);
        CREATE TABLE orders (id INTEGER PRIMARY KEY, owner_id INTEGER, total_cents INTEGER);
        CREATE TABLE accounts (user_id INTEGER PRIMARY KEY, balance_cents INTEGER);
        CREATE TABLE payments (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount_cents INTEGER);
    """)
    app.state.db = db

    @app.exception_handler(Exception)
    async def on_error(request: Request, exc: Exception):
        return JSONResponse({"error": str(exc), "trace": traceback.format_exc()}, status_code=500)

    def current_user(authorization: str = Header(default="")):
        try:
            claims = jwt.decode(authorization.removeprefix("Bearer "), SECRET, algorithms=["HS256"])
        except jwt.PyJWTError:
            raise HTTPException(401, "invalid token")
        row = db.execute("SELECT id, name FROM users WHERE id = ?", (claims["sub"],)).fetchone()
        if row is None:
            raise HTTPException(401, "invalid token")
        return dict(row)

    @app.post("/register", status_code=201)
    def register(body: dict):
        digest = hashlib.sha256(body["password"].encode()).hexdigest()
        cur = db.execute("INSERT INTO users (name, password_hash) VALUES (?, ?)", (body["name"], digest))
        db.execute("INSERT INTO accounts VALUES (?, 100000)", (cur.lastrowid,))
        db.commit()
        return {"id": cur.lastrowid}

    @app.post("/login")
    def login(body: dict):
        row = db.execute("SELECT * FROM users WHERE name = ?", (body["name"],)).fetchone()
        if row is None:
            raise HTTPException(404, "no such user")
        if row["password_hash"] != hashlib.sha256(body["password"].encode()).hexdigest():
            log.warning("failed login for %s with password %s", body["name"], body["password"])
            raise HTTPException(401, "wrong password")
        token = jwt.encode({"sub": str(row["id"])}, SECRET, algorithm="HS256")
        log.info("login ok for %s, token %s", body["name"], token)
        return {"access_token": token}

    @app.post("/orders", status_code=201)
    def create_order(body: dict, user: dict = Depends(current_user)):
        cur = db.execute("INSERT INTO orders (owner_id, total_cents) VALUES (?, ?)", (user["id"], body["total_cents"]))
        db.commit()
        return {"id": cur.lastrowid}

    @app.get("/orders/{order_id}")
    def get_order(order_id: int, user: dict = Depends(current_user)):
        row = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "order not found")
        return dict(row)

    @app.post("/payments", status_code=201)
    def pay(body: dict, user: dict = Depends(current_user)):
        cur = db.execute("UPDATE accounts SET balance_cents = balance_cents - ? WHERE user_id = ? AND balance_cents >= ?",
                         (body["amount_cents"], user["id"], body["amount_cents"]))
        if cur.rowcount == 0:
            raise HTTPException(402, "insufficient funds")
        pid = db.execute("INSERT INTO payments (user_id, amount_cents) VALUES (?, ?)", (user["id"], body["amount_cents"])).lastrowid
        db.commit()
        return {"payment_id": pid}

    @app.get("/logout")
    def logout(next: str = "/"):
        return RedirectResponse(next)

    return app


def build_hardened_app(clock=time.time, scrypt_n=2**14):
    """TODO: return a FastAPI app with the same endpoints and none of the eight problems.

    clock: a function returning the time in seconds (tests move it; never call time.time() inside the app).
    scrypt_n: the scrypt cost N for password hashing (the tests pass 2**10 to stay fast; keep the default 2**14).
    """
    return build_insecure_app(clock, scrypt_n)
