## Approach

```python
class Settings(BaseModel):
    model_config = {"frozen": True}
    database_url: str = "sqlite:///./dev.db"
    secret_key: str = Field(min_length=32)               # no default: a missing secret must fail loudly
    debug: bool = False
    token_minutes: int = Field(default=15, ge=1, le=1440)

    @classmethod
    def from_env(cls, environ=None):
        if environ is None:
            environ = os.environ
        values = {field: environ[name] for field, name in ENV_NAMES.items() if name in environ}
        try:
            return cls.model_validate(values)            # strings in, typed values out
        except ValidationError as exc:
            problems = []
            for error in exc.errors():
                field = error["loc"][0]
                problems.append(f"{ENV_NAMES.get(field, field)}: {error['msg']}")    # never error["input"]
            raise ConfigError("Invalid configuration: " + "; ".join(problems)) from None


def create_app(settings=None):
    settings = settings or Settings.from_env()           # fails here, at start-up
    app = FastAPI()
    app.state.settings = settings
    ...
```

Example: `APP_SECRET_KEY=short-but-secret`, `APP_TOKEN_MINUTES=0`. `values` is `{"secret_key": "short-but-secret", "token_minutes": "0"}`. Pydantic converts `"0"` to `0` and then finds two errors: `secret_key` too short, `token_minutes` not ≥ 1. The loop turns them into `APP_SECRET_KEY: String should have at least 32 characters; APP_TOKEN_MINUTES: Input should be greater than or equal to 1`. The value `short-but-secret` appears nowhere.

Why the environment names in the message: the person who reads the error at 3 a.m. is fixing a deployment file, where the variable is called `APP_SECRET_KEY`. `secret_key` would send them looking in the code.

Why `create_app` fails and not the first request: a server that starts happily and then answers 500 to everyone is worse than one that refuses to start: the deployment tool sees the failed start and keeps the old version running.

## Complexity

O(v) for v variables, once at start-up.

## Another way

`pydantic-settings` (`class Settings(BaseSettings)` with `model_config = SettingsConfigDict(env_prefix="APP_")`) does the reading, the prefix and `.env` files for you. It is the usual choice in real projects; this exercise shows that the core of it is twenty lines. A different style, used by twelve-factor apps, is a **dataclass** with an explicit `from_env` that parses each value by hand: more code, but no dependency at all.
