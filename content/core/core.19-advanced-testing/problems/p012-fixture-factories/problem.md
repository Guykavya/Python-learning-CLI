# Write a fixture factory with cleanup

A plain fixture gives every test **one** object. When tests need a **varying number** of objects
with different arguments, the fixture returns a **function** that makes them (a *factory*), and
it remembers what it made so it can **clean up** afterwards:

```python
@pytest.fixture
def make_thing():
    made = []
    def make(name):
        thing = create(name)
        made.append(thing)
        return thing
    yield make
    for thing in made:        # teardown: runs after the test, even if it failed
        destroy(thing)
```

The code under test keeps its users in a module-level registry, so leftovers from one test
would break the next:

```python
_USERS = {}


def create_user(name, admin=False):
    if name in _USERS:
        raise ValueError(f"user {name!r} already exists")
    user = {"name": name, "admin": admin}
    _USERS[name] = user
    return user


def delete_user(name):
    del _USERS[name]           # KeyError if the user does not exist


def all_users():
    return sorted(_USERS)
```

In `solution.py` write the fixture **`make_user`** (`import pytest` and
`from target import create_user, delete_user, all_users` first). Using it, a test calls
`make_user("ann")` or `make_user("bob", admin=True)` and gets the user dict. After each test, every
user that the factory created must be gone from the registry, **including when the test already
deleted its own user** (a second `delete_user` would raise `KeyError`).

**How this is checked.** The checker copies your `solution.py` into a temporary project as
`conftest.py` and runs seven checker-written tests that use `make_user`; the later ones look at
the registry to see whether you cleaned up.

**Example** of what a test does with it:

```python
def test_two_users(make_user):
    ann = make_user("ann")
    bob = make_user("bob", admin=True)
    assert all_users() == ["ann", "bob"]
```
