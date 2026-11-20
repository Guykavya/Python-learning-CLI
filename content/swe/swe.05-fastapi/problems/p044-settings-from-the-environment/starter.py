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
    # TODO: frozen; database_url, secret_key (min 32, required), debug, token_minutes (1..1440)
    secret_key: str = ""

    @classmethod
    def from_env(cls, environ=None):
        # TODO: read the variables of ENV_NAMES that are present, model_validate them,
        #       turn a ValidationError into ConfigError naming the APP_ variables (never the values)
        raise NotImplementedError


def create_app(settings=None):
    settings = settings or Settings.from_env()
    app = FastAPI()
    app.state.settings = settings

    @app.get("/info")
    def info(request: Request):
        return {}                     # TODO

    return app
