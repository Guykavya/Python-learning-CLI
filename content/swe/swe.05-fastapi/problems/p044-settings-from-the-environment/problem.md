# Settings from the environment

Chapter section 18. Configuration comes from **environment variables**, which are always strings. A Pydantic model turns them into typed values and refuses nonsense **at start-up**, before the first request. `pydantic-settings` is not installed, so we do it by hand, as the chapter does.

In `solution.py`:

1. **`Settings(BaseModel)`**, frozen (`model_config = {"frozen": True}`), with these fields and environment variables:

   | Field | Variable | Type and rule | Default |
   |---|---|---|---|
   | `database_url` | `APP_DATABASE_URL` | `str` | `"sqlite:///./dev.db"` |
   | `secret_key` | `APP_SECRET_KEY` | `str`, at least 32 characters | **none: required** |
   | `debug` | `APP_DEBUG` | `bool` | `False` |
   | `token_minutes` | `APP_TOKEN_MINUTES` | `int`, 1 to 1440 | `15` |

   The mapping is given as `ENV_NAMES` (field → variable).

2. **`Settings.from_env(environ=None)`**, a classmethod. Use `os.environ` when `environ` is `None` (so tests can also pass a plain dict). Take only the variables that are present, then `model_validate` them. If validation fails, raise **`ConfigError`** (given) with a message that names **every bad variable by its environment name** (`APP_SECRET_KEY`, not `secret_key`), for example:

   ```text
   Invalid configuration: APP_SECRET_KEY: Field required; APP_DEBUG: Input should be a valid boolean, unable to interpret input
   ```

   Build it from `exc.errors()`: each error has `loc` (a tuple whose first item is the field name) and `msg`. **Never** put the value into the message: `str(exc)` of a Pydantic `ValidationError` includes the input (`input_value='...'`), so a too-short secret would end up in your logs. Use `raise ConfigError(...) from None`.

3. **`create_app(settings=None)`**: `settings = settings or Settings.from_env()`, so a missing secret stops the app **when it is created**. Store it in `app.state.settings`. One route, `GET /info`, returns `{"debug": ..., "token_minutes": ..., "database": <the part of database_url before "://">}`. Never the secret.

## Example

```text
APP_SECRET_KEY=ssss...(40 chars) APP_DEBUG=true APP_TOKEN_MINUTES=30
  create_app() -> GET /info -> {"debug": true, "token_minutes": 30, "database": "sqlite"}

(no APP_SECRET_KEY)
  create_app() -> ConfigError: Invalid configuration: APP_SECRET_KEY: Field required

APP_SECRET_KEY=short APP_TOKEN_MINUTES=0
  -> ConfigError naming APP_SECRET_KEY and APP_TOKEN_MINUTES, and NOT containing "short"
```

The tests set variables with `monkeypatch.setenv(...)` and remove them with `monkeypatch.delenv(..., raising=False)`; pytest restores the real environment afterwards.
