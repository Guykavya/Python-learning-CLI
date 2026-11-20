# `get_current_user`

Chapter section 12.3 (`OAuth2PasswordBearer` and `get_current_user`), with 12.1 and 12.2 for the helpers, 9.3 for sub-dependencies and 9.6 for the injected clock.

The starter already has the pieces from p032 and p033: `hash_password` / `verify_password`, `make_token(user_id, now)` / `read_token(token, now)` with `InvalidToken`, two users in `USERS`, and a clock dependency `get_clock()` (returns `int(time.time())`). Wire them into the standard OAuth2 "password flow":

**1. `POST /token`: log in with a form.** Take the login as `form: Annotated[OAuth2PasswordRequestForm, Depends()]`. This class reads the fields `username` and `password` from an HTML-style **form** body (`application/x-www-form-urlencoded`), which is what the standard flow and the **Authorize** button in `/docs` send. It needs the package `python-multipart`; in this course it is installed. (Section 12.3, "The standard form login", shows this form version running.)

- Unknown user **or** wrong password: **401** `{"detail": "Incorrect username or password"}` with the header `WWW-Authenticate: Bearer`. The same answer in both cases.
- Success: `{"access_token": make_token(user["id"], now), "token_type": "bearer"}`, where `now` comes from `Depends(get_clock)`.

**2. `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")`.** As a dependency it reads `Authorization: Bearer <token>` and returns the token string. If the header is missing (or is not `Bearer`), it answers **401** `{"detail": "Not authenticated"}` with `WWW-Authenticate: Bearer` on its own.

**3. `get_current_user(token = Depends(oauth2_scheme), now = Depends(get_clock)) -> dict`.** Read the token with `read_token(token, now)` and find the user with that id. If the token is invalid or expired, or no user has that id: **401** `{"detail": "Invalid or expired token"}` with `WWW-Authenticate: Bearer`.

**4. `GET /me`** depends on `get_current_user` and returns `{"id": ..., "username": ...}` (never the hash).

## Example

```text
POST /token  form username=asha password=wrong     -> 401 {"detail": "Incorrect username or password"}  WWW-Authenticate: Bearer
POST /token  form username=asha password=asha-pass -> 200 {"access_token": "eyJ...", "token_type": "bearer"}
GET  /me                                           -> 401 {"detail": "Not authenticated"}               WWW-Authenticate: Bearer
GET  /me  Authorization: Bearer junk               -> 401 {"detail": "Invalid or expired token"}         WWW-Authenticate: Bearer
GET  /me  Authorization: Bearer eyJ...             -> 200 {"id": 1, "username": "asha"}
```

With the test client, a form is sent with `data=`: `client.post("/token", data={"username": "asha", "password": "asha-pass"})`.

The tests import `app`, `get_clock`, `make_token` and `get_current_user`, and replace the clock with `app.dependency_overrides[get_clock]` to test expiry.
