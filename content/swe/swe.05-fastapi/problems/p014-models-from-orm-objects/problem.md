# Models from ORM objects

Chapter sections 5.11 (`from_attributes`) and 7.1 to 7.2 (`response_model`). A database layer (swe.03) gives you **objects with attributes**, not dicts. By default Pydantic refuses them. Make output models that read attributes, copy only what they declare, and handle a nested object.

In `solution.py` define `app = FastAPI()` and:

```python
class TeamOut(BaseModel):          # reads attributes too
    id: int
    name: str

class UserOut(BaseModel):          # reads attributes too
    id: int
    name: str
    email: str
    team: TeamOut | None = None

USERS: dict = {}                   # user id -> an ORM-like user object (the tests fill it)
```

Both models need `model_config = ConfigDict(from_attributes=True)`.

1. `to_out(user) -> UserOut` returns `UserOut.model_validate(user)`.
2. `GET /users/{user_id}` uses `response_model=UserOut` and returns the **object** from `USERS` as it is. If the id is not in `USERS`, `raise HTTPException(status_code=404, detail="user not found")` (from `fastapi`; section 8.1 explains it fully: raising it stops the endpoint and sends that status).

The user objects the tests use look like this (a stand-in for a SQLAlchemy row):

```python
class FakeTeam:
    def __init__(self, id, name):
        self.id, self.name = id, name

class FakeUser:
    def __init__(self, id, name, email, team=None):
        self.id, self.name, self.email, self.team = id, name, email, team
        self.password_hash = "pbkdf2$" + name[::-1]     # must never be copied
        self.is_admin = False                            # not part of the output either
```

## Example

```text
USERS[1] = FakeUser(1, "Asha", "asha@example.com", team=FakeTeam(7, "Platform"))

to_out(USERS[1])  -> UserOut(id=1, name='Asha', email='asha@example.com', team=TeamOut(id=7, name='Platform'))

GET /users/1 -> 200 {"id": 1, "name": "Asha", "email": "asha@example.com", "team": {"id": 7, "name": "Platform"}}
GET /users/9 -> 404 {"detail": "user not found"}
```
