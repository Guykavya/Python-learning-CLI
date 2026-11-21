import re
from dataclasses import dataclass

LEVELS = ("DEBUG", "ERROR", "INFO", "WARNING")


class ConfigError(RuntimeError):
    pass


def _mask_password(url):
    return re.sub(r"(://[^:/@]+:)[^@]+(@)", r"\1***\2", url)


@dataclass(frozen=True)
class Settings:
    database_url: str
    secret_key: str
    port: int = 8000
    log_level: str = "INFO"

    @classmethod
    def from_env(cls, env):
        problems = []
        database_url = env.get("DATABASE_URL") or ""
        if not database_url:
            problems.append("DATABASE_URL is required")
        elif "://" not in database_url:
            problems.append(f"DATABASE_URL must look like scheme://... (got {database_url!r})")
        secret_key = env.get("SECRET_KEY") or ""
        if not secret_key:
            problems.append("SECRET_KEY is required")
        elif len(secret_key) < 32:
            problems.append("SECRET_KEY must be at least 32 characters")
        port = 8000
        raw_port = env.get("PORT") or ""
        if raw_port:
            try:
                port = int(raw_port)
            except ValueError:
                port = 0
            if not 1 <= port <= 65535:
                problems.append(f"PORT must be an integer from 1 to 65535 (got {raw_port!r})")
        raw_level = env.get("LOG_LEVEL") or ""
        log_level = raw_level.upper() if raw_level else "INFO"
        if log_level not in LEVELS:
            problems.append(f"LOG_LEVEL must be one of {', '.join(LEVELS)} (got {raw_level!r})")
        if problems:
            raise ConfigError("; ".join(problems))               # refuse to start with a bad configuration
        return cls(database_url=database_url, secret_key=secret_key, port=port, log_level=log_level)

    def __repr__(self):
        return (f"Settings(database_url={_mask_password(self.database_url)!r}, secret_key='***', "
                f"port={self.port!r}, log_level={self.log_level!r})")
