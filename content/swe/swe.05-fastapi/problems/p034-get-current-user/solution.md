## Approach

```python
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
```

Who answers each failure:

| Request | Stopped by | Answer |
|---|---|---|
| no `Authorization` header, or `Basic ...` | `oauth2_scheme` itself | 401 `Not authenticated` |
| `Bearer junk`, forged, expired | `read_token` → `InvalidToken` → your 401 | 401 `Invalid or expired token` |
| valid token, deleted user | the lookup → your 401 | 401 `Invalid or expired token` |

When a dependency raises, the endpoint never runs (section 9.3), so `me` contains no checks at all: every endpoint that takes `CurrentUser` is protected by the same code.

`WWW-Authenticate: Bearer` is part of HTTP's 401 contract: it tells the client *which* kind of credentials to send. `OAuth2PasswordBearer` adds it for the missing-header case; you add it for yours.

`tokenUrl="token"` does nothing at request time; it appears in the OpenAPI schema so that the **Authorize** button in `/docs` knows where to post the form.

## Complexity

One HMAC check per request plus an O(n) user lookup (a database would use the primary key).

## Another way

Look the user up by id in a dict keyed by id (`USERS_BY_ID[user_id]`), or in the database with `session.get(User, user_id)`. And add a `require_role(...)` dependency factory on top of `get_current_user` for 403s (section 12.3) and an ownership check (p035).
