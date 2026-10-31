## Approach

A fake keeps the observable behaviour (results and errors) and drops the hard parts (disk, network).
The dict lives on `self`, every error is raised before any change, and `names` builds a new list so
callers cannot corrupt the repo by editing it. Because `UserNotFound` inherits from `KeyError` and
`DuplicateUser` from `ValueError`, code that handles the built-in types still works.

## Code

```python
class UserNotFound(KeyError):
    pass


class DuplicateUser(ValueError):
    pass


class FakeUserRepo:
    def __init__(self):
        self._users = {}

    def add(self, user_id, name):
        if user_id in self._users:
            raise DuplicateUser(user_id)
        if not name.strip():
            raise ValueError("name must not be blank")
        self._users[user_id] = name

    def get(self, user_id):
        if user_id not in self._users:
            raise UserNotFound(user_id)
        return self._users[user_id]

    def delete(self, user_id):
        if user_id not in self._users:
            raise UserNotFound(user_id)
        del self._users[user_id]

    def names(self):
        return [self._users[user_id] for user_id in sorted(self._users)]
```

## Complexity

`add`, `get`, `delete` are O(1); `names` is O(n log n).

## Another way

Make the fake a subclass of the real repository, overriding only the storage methods. Then they
share the logic, and a contract test still guards the overridden part.
