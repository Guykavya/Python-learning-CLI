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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
BEARER = {"WWW-Authenticate": "Bearer"}


@app.post("/token")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], now: Annotated[int, Depends(get_clock)]):
    user = USERS.get(form.username)
    # One answer for "no such user" and "wrong password": do not reveal which names exist.
    if user is None or not verify_password(form.password, user["hash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect username or password", headers=BEARER)
    return {"access_token": make_token(user["id"], now), "token_type": "bearer"}


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], now: Annotated[int, Depends(get_clock)]) -> dict:
    error = HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token", headers=BEARER)
    try:
        user_id = read_token(token, now)
    except InvalidToken:
        raise error
    user = next((u for u in USERS.values() if u["id"] == user_id), None)
    if user is None:                       # a valid token for a user that no longer exists
        raise error
    return user


CurrentUser = Annotated[dict, Depends(get_current_user)]


@app.get("/me")
def me(user: CurrentUser):
    return {"id": user["id"], "username": user["username"]}
