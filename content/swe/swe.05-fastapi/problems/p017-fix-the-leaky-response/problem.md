# Fix the leaky response

Chapter sections 7.1 and 7.2 (`response_model`, "Never leak a password hash"), "Try it: the leaky response" after section 7.6, and 7.6 (status codes). The user API in `starter.py` works, and it **sends the password hash to anyone who asks**. Fix it in `solution.py` without changing what is stored.

The app has three models, as in section 7.2: `UserCreate` (what clients send), `UserDB` (what is stored, with `password_hash`) and `UserOut` (what clients should get back). And three endpoints:

- `POST /users` registers a user and returns it.
- `GET /users/{user_id}` returns one user, or 404 `{"detail": "user not found"}`.
- `GET /users` returns the list of all users, in id order.

Find and fix the bugs:

1. **`UserOut` declares `password_hash`.** A response model only removes what it does **not** declare, so this field passes straight through (the "Try it" box).
2. **`POST /users` has no response model** and returns the full stored row. It must answer with `UserOut` and status **201**.
3. **`GET /users` has no response model** either. A list of users needs `response_model=list[UserOut]`.

After the fix, no response may contain a key with `password` or `hash` in its name **at any depth**, and the hash value must not appear anywhere in the response text. `FAKE_DB` must still store `password_hash` (the server needs it to check logins later).

## Example

```text
POST /users {"email": "asha@example.com", "password": "correct horse"}
-> 201 {"id": 1, "email": "asha@example.com"}

GET /users/1 -> 200 {"id": 1, "email": "asha@example.com"}
GET /users   -> 200 [{"id": 1, "email": "asha@example.com"}]
GET /users/9 -> 404 {"detail": "user not found"}

FAKE_DB[1].password_hash -> "pbkdf2$esroh tcerroc"   (still stored)
```
