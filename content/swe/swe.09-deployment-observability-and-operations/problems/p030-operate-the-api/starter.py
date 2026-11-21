import sqlite3
from contextlib import closing
from dataclasses import dataclass

from fastapi import FastAPI


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class Settings:
    env: str = "development"
    version: str = "dev"
    database_path: str = "pagebound.db"
    log_level: str = "INFO"
    secret_key: str = ""

    @classmethod
    def from_env(cls, environ=None):
        # TODO (p003): read APP_ENV, APP_VERSION, DATABASE_PATH, LOG_LEVEL, APP_SECRET_KEY; validate; one ConfigError
        return cls()


def create_app(settings=None):
    settings = settings or Settings.from_env()
    app = FastAPI()
    app.state.draining = False
    # TODO: logs (p013), request ids (p014), orders, health (p017), metrics (p019), lifespan and draining (p018)
    return app


DOCKERFILE = ""        # TODO (p006): a Dockerfile that passes lint_dockerfile
COMPOSE = ""           # TODO (p009): a compose.yaml that passes check_compose
WORKFLOW = ""          # TODO (p023): a GitHub Actions workflow that passes check
