## Approach

Put what many tests share in the top `conftest.py`. Override only the one fixture that differs
in the subfolder; everything that depends on it follows automatically because fixtures are
resolved by name for each test.

## Code

```python
CONFTEST = """
import pytest


@pytest.fixture
def app_config():
    return {"debug": False, "db": "memory"}


@pytest.fixture
def user(app_config):
    return {"name": "ada", "db": app_config["db"]}
"""

API_CONFTEST = """
import pytest


@pytest.fixture
def app_config():
    return {"debug": True, "db": "api-db"}
"""
```

## Cost

Nothing at run time. The cost is **readability**: a fixture can come from any conftest above the
test, so `pytest --fixtures` (it lists each fixture with its file) is the tool to find where a
name comes from.

## Another way

Put fixtures in a plain module (`fixtures.py`) and load it with
`pytest_plugins = ["fixtures"]` in the top conftest, which scales better in big projects. A
fixture can also be overridden in a single test module by defining it there.
