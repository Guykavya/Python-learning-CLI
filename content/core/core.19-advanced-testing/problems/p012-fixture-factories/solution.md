## Approach

The fixture builds a closure `make` that appends each name to a list, **yields** it to the
test, and after the test deletes whatever is still registered. The guard `if name in
all_users()` makes cleanup safe when the test removed the user itself.

## Code

```python
import pytest

from target import all_users, create_user, delete_user


@pytest.fixture
def make_user():
    created = []

    def make(name, admin=False):
        user = create_user(name, admin=admin)
        created.append(name)
        return user

    yield make
    for name in created:
        if name in all_users():
            delete_user(name)
```

## Cost

Cleanup is O(k) for k users made by the test. Factory fixtures are cheap because the list lives
only as long as the test.

## Another way

`try/except KeyError: pass` around `delete_user` is the same guard. For many resource types,
`request.addfinalizer(callable)` registers a cleanup right when the resource is created, so
even a half-finished factory call is cleaned up.
