import os

from fastapi import FastAPI, Request
from pydantic import BaseModel, Field, ValidationError

ENV_NAMES = {
    "database_url": "APP_DATABASE_URL",
    "secret_key": "APP_SECRET_KEY",
    "debug": "APP_DEBUG",
    "token_minutes": "APP_TOKEN_MINUTES",
}


class ConfigError(Exception):
    """The configuration is invalid: the app must not start."""


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

    @app.get("/info")
    def info(request: Request):
        s = request.app.state.settings
        return {"debug": s.debug, "token_minutes": s.token_minutes, "database": s.database_url.split("://")[0]}

    return app
