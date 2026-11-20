## Hint 1

Call each endpoint in your head and ask: what object does the function return, and what filter (if any) sits between it and the client? Which endpoints have **no** `response_model` at all? And for the one that has it, what does `UserOut` declare?

## Hint 2

Section 7.2: the filter keeps exactly the fields of the response model. So the model must not declare the secret, and every endpoint that returns user data needs the model: `response_model=UserOut` for one user, `response_model=list[UserOut]` for a list. Leave `UserDB` and `FAKE_DB` alone.

## Hint 3

```text
class UserOut: id, email                         (delete password_hash)
@app.post("/users", response_model=UserOut, status_code=201)
@app.get("/users/{user_id}", response_model=UserOut)       (already there)
@app.get("/users", response_model=list[UserOut])
```
