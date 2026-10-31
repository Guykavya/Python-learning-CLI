# Write an in-memory fake

A **fake** is a working but simplified copy of a dependency (a dict instead of a database). It is only
trustworthy if it behaves like the real thing, so the same **contract tests** run against both.

The contract (a `typing.Protocol`, shown for reading):

```python
class UserRepo(Protocol):
    def add(self, user_id, name): ...    # DuplicateUser if user_id exists; ValueError if name is blank
    def get(self, user_id): ...          # returns the name; UserNotFound if missing
    def delete(self, user_id): ...       # UserNotFound if missing
    def names(self): ...                 # list of names ordered by user_id (a NEW list each call)
```

In `solution.py` write:

- `class UserNotFound(KeyError)` and `class DuplicateUser(ValueError)` (empty bodies are fine);
- `class FakeUserRepo` implementing the four methods with a dict. Two repos must not share data.

A blank name is `""` or only spaces. Names are stored as given.

The checker runs one set of contract tests against a dict-backed "real" repo and against your fake.

**Example**

```python
repo = FakeUserRepo()
repo.add(2, "Bo"); repo.add(1, "Ann")
repo.names()        # ['Ann', 'Bo']   (ordered by id 1, 2)
repo.get(2)         # 'Bo'
repo.get(9)         # raises UserNotFound
```
