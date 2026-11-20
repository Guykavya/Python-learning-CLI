## Hint 1

Try `UserOut.model_validate(FakeUser(...))` with the starter: what does the error say Pydantic expected? Which setting of section 5.11 lets it read `obj.id` instead of `obj["id"]`?

## Hint 2

The nested `team` is also an object, so `TeamOut` needs the same setting. In the endpoint, return the object unchanged and declare `response_model=UserOut`: FastAPI then validates it with `from_attributes` and drops everything not declared.

## Hint 3

```text
TeamOut / UserOut: model_config = ConfigDict(from_attributes=True)

@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    user = USERS.get(user_id)
    if user is None: raise HTTPException(status_code=404, detail="user not found")
    return user
```
