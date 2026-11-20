## Approach

Allow attribute reading on both output models; the response model then turns any ORM-like object into a filtered JSON body.

```python
class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    team: TeamOut | None = None


def to_out(user) -> UserOut:
    return UserOut.model_validate(user)


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    user = USERS.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return user
```

Example: for user 1, Pydantic reads `user.id`, `user.name`, `user.email` and `user.team`; `user.team` is a `FakeTeam`, which `TeamOut` reads the same way. `password_hash` and `is_admin` are never looked at, because `UserOut` does not declare them, so they cannot leak.

## Complexity

O(number of declared fields), including the nested ones.

## Another way

Build the output by hand: `UserOut(id=u.id, name=u.name, email=u.email, team=...)`. It works without `from_attributes`, but every new field must be added in two places, and forgetting the nested conversion is easy. In a real app with SQLAlchemy, remember that reading `user.team` may run a query (lazy loading); in async code that is the `MissingGreenlet` trap of section 11.5.
