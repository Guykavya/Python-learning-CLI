import re
from dataclasses import dataclass


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class Settings:
    database_url: str
    secret_key: str
    port: int = 8000
    log_level: str = "INFO"

    @classmethod
    def from_env(cls, env):
        # TODO: read, validate everything, raise ONE ConfigError listing every problem
        return cls(database_url=env.get("DATABASE_URL", ""), secret_key=env.get("SECRET_KEY", ""))

    def __repr__(self):
        # TODO: hide the secret key and the password inside database_url
        return f"Settings(database_url={self.database_url!r}, secret_key={self.secret_key!r})"
