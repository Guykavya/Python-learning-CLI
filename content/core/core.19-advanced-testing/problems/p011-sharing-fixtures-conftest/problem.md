# Sharing fixtures with conftest.py

Fixtures defined in a file called **`conftest.py`** are available to every test in that folder
and in all folders below it, **without importing anything**. A `conftest.py` in a deeper folder
can **override** a fixture of the same name from above, for the tests in that folder only.

Your project layout:

```text
tests/
    conftest.py          <- you write it (CONFTEST)
    test_top.py          <- written by the checker
    api/
        conftest.py      <- you write it (API_CONFTEST)
        test_api.py      <- written by the checker
```

In `solution.py` define two strings (the full text of the two files):

- **`CONFTEST`** (`tests/conftest.py`) with two fixtures
  - `app_config` returns `{"debug": False, "db": "memory"}` (a **new** dict for every test)
  - `user` depends on `app_config` and returns `{"name": "ada", "db": <the db from app_config>}`
- **`API_CONFTEST`** (`tests/api/conftest.py`) overrides **only** `app_config`, returning
  `{"debug": True, "db": "api-db"}`. It must not define `user`.

The checker's tests then expect: outside `api/`, `app_config` is the default and `user["db"]` is
`"memory"`; inside `api/`, `app_config` is the override and (without redefining `user`!)
`user["db"]` is `"api-db"`; and a test that changes `app_config` does not affect the next test.

**Example** of a conftest as a string:

```python
CONFTEST = """
import pytest


@pytest.fixture
def greeting():
    return "hello"
"""
```
