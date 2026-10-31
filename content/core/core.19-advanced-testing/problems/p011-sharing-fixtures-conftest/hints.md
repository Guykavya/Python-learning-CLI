## Hint 1

A conftest is an ordinary Python file, so its text starts with `import pytest`. What goes
between the triple quotes for `app_config`? A function decorated with `@pytest.fixture` that
returns a dict. Where must the dict be **created** so every test gets a fresh one?

## Hint 2

Why does `user` in the `api` folder get `"api-db"` without being redefined? Fixtures are looked
up **by name at the moment a test runs**, starting from the test's own folder and moving up.
`user` asks for `app_config`, and for tests in `api/` the nearest `app_config` is the override.

```
CONFTEST      = "import pytest ... @pytest.fixture def app_config(): return {...}  def user(app_config): ..."
API_CONFTEST  = "import pytest ... @pytest.fixture def app_config(): return {... 'api-db'}"
```
