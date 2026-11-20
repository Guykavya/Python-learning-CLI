## Approach

Make the output model declare only public fields, and put it on **every** endpoint that returns user data.

```python
class UserOut(BaseModel):                        # what clients get back: no secrets declared
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str


@app.post("/users", response_model=UserOut, status_code=201)
def register(data: UserCreate):
    row = UserDB(id=len(FAKE_DB) + 1, email=data.email, password_hash=hash_password(data.password))
    FAKE_DB[row.id] = row
    return row


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    if user_id not in FAKE_DB:
        raise HTTPException(status_code=404, detail="user not found")
    return FAKE_DB[user_id]


@app.get("/users", response_model=list[UserOut])
def list_users():
    return [FAKE_DB[user_id] for user_id in sorted(FAKE_DB)]
```

Example: `register` still returns the full `UserDB` row on purpose. FastAPI validates it against `UserOut`, which reads `id` and `email` (via `from_attributes`) and never looks at `password_hash`, so the response is `{"id": 1, "email": "asha@example.com"}`.

- **Bug 1** was the subtle one: `GET /users/1` *had* a response model, but a model that declares the secret lets it through. The filter only removes what is not declared.
- **Bug 2 and 3:** without any response model, FastAPI serialises whatever you return, the whole row.

The tests look for secret-looking keys at **any depth**, because leaks often hide in nested objects and lists.

## Complexity

O(number of users returned): each one is validated against `UserOut`.

## Another way

Build the output explicitly: `return UserOut.model_validate(row)` (and a list comprehension for the list), with the return annotation `-> UserOut` / `-> list[UserOut]`. The response model then comes from the annotation (section 7.1). Either way, keep all output models in one `schemas` module where every field is a deliberate choice, and keep a test like `assert_no_leak` for every endpoint that returns users.
