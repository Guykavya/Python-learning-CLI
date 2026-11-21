# Settings that fail fast

Chapter sections 3.1 to 3.3 (configuration from the environment; a `Settings` class that fails fast) and "Try it: fail fast". A service should read its configuration **once, at start-up**, into a validated object, and **refuse to start** when it is wrong: a deployment that fails at start can be rolled back before any user is affected, while a service that limps along fails at 3 a.m. under load. The settings here are the typical ones of a service with a SQL database.

## What to write

```python
class ConfigError(RuntimeError): ...

@dataclass(frozen=True)
class Settings:
    database_url: str
    secret_key: str
    port: int = 8000
    log_level: str = "INFO"

    @classmethod
    def from_env(cls, env: dict) -> "Settings": ...
    def __repr__(self) -> str: ...
```

`from_env(env)` reads these names from the dict `env` (the tests pass a plain dict; real code would pass `os.environ`):

| Name | Rule |
|---|---|
| `DATABASE_URL` | **required**; must contain `://` |
| `SECRET_KEY` | **required**; at least 32 characters |
| `PORT` | optional, default `8000`; must be an integer from 1 to 65535 |
| `LOG_LEVEL` | optional, default `INFO`; case-insensitive, stored in upper case; one of `DEBUG`, `INFO`, `WARNING`, `ERROR` |

- Collect **every** problem and raise **one** `ConfigError` whose message joins them with `"; "`. A person fixing a deployment should see all mistakes at once. Each problem must **name the variable** (for example `PORT must be ...`).
- A missing variable and an empty string (`""`) are both "not set".
- `__repr__` must **never show the secret key**, and must hide a **password inside `database_url`** (`postgresql://app:s3cret@db/app` is shown as `postgresql://app:***@db/app`). A URL without a password is shown as it is.

## Example

```python
Settings.from_env({"DATABASE_URL": "sqlite:///dev.db", "SECRET_KEY": "k" * 32})
# Settings(database_url='sqlite:///dev.db', secret_key='***', port=8000, log_level='INFO')

Settings.from_env({"PORT": "99999", "LOG_LEVEL": "loud"})
# ConfigError: DATABASE_URL is required; SECRET_KEY is required; PORT must be an integer from 1 to 65535 (got '99999'); LOG_LEVEL must be one of DEBUG, ERROR, INFO, WARNING (got 'loud')
```

The exact wording is yours; the tests look for the variable names and for the words in the examples above.
