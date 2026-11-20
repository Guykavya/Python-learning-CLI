import base64
import hashlib
import hmac
import os
import time
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# ---- given: password hashing (p032; few iterations so the tests stay fast) ----

def hash_password(password: str, iterations: int = 1000) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return "$".join(["pbkdf2_sha256", str(iterations), base64.b64encode(salt).decode(), base64.b64encode(digest).decode()])


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, n, salt_b64, digest_b64 = stored.split("$")
        salt, expected = base64.b64decode(salt_b64), base64.b64decode(digest_b64)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(n))
    except ValueError:
        return False
    return scheme == "pbkdf2_sha256" and hmac.compare_digest(actual, expected)


# ---- given: tokens (p033) ----

SECRET = "demo-secret-" + "k" * 40
ALGORITHM = "HS256"


class InvalidToken(Exception):
    pass


def make_token(user_id: int, now: int, minutes: int = 15) -> str:
    return jwt.encode({"sub": str(user_id), "exp": now + minutes * 60}, SECRET, algorithm=ALGORITHM)


def read_token(token: str, now: int) -> int:
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM], options={"verify_exp": False, "require": ["sub", "exp"]})
        if now >= payload["exp"]:
            raise InvalidToken("Token expired")
        return int(payload["sub"])
    except (jwt.PyJWTError, ValueError) as exc:
        raise InvalidToken(str(exc)) from exc


# ---- given: users and the clock ----

USERS = {
    "asha": {"id": 1, "username": "asha", "hash": hash_password("asha-pass")},
    "ben": {"id": 2, "username": "ben", "hash": hash_password("ben-pass")},
}


def get_clock() -> int:
    return int(time.time())


app = FastAPI()

# ---- your part ----

# TODO: oauth2_scheme = OAuth2PasswordBearer(...)


@app.post("/token")
def login():
    # TODO: read the form, check the password, return the token
    return {}


def get_current_user() -> dict:
    # TODO: token from oauth2_scheme, now from get_clock, 401 for any problem
    return {}


@app.get("/me")
def me():
    # TODO: depend on get_current_user
    return {}
