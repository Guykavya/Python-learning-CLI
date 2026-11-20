## Hint 1

Split the work: the **model** knows types and rules (`bool`, `int`, `Field(min_length=32)`, `Field(ge=1, le=1440)`); `from_env` only collects strings and translates errors. Which field must have **no** default so that forgetting it is an error? How do you collect only the variables that are set: a dict comprehension over `ENV_NAMES.items()` with an `if name in environ`?

## Hint 2

```text
try:
    return cls.model_validate(values)
except ValidationError as exc:
    for each error in exc.errors():
        field = error["loc"][0]
        problem text = ENV_NAMES[field] + ": " + error["msg"]
    raise ConfigError("Invalid configuration: " + "; ".join(problems)) from None
```
Why `from None`? Without it the new exception keeps the `ValidationError` as its context, and a traceback prints it, including the secret.

## Hint 3

```text
class Settings(BaseModel):
    model_config = {"frozen": True}
    database_url: str = "sqlite:///./dev.db"
    secret_key: str = Field(min_length=32)
    debug: bool = False
    token_minutes: int = Field(default=15, ge=1, le=1440)

create_app(settings=None):
    settings = settings or Settings.from_env()
    app.state.settings = settings
    /info: {"debug", "token_minutes", "database": database_url.split("://")[0]}
```
