## Approach

```python
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
        raise ConfigError("; ".join(problems))
    return cls(database_url=database_url, secret_key=secret_key, port=port, log_level=log_level)


def __repr__(self):
    return (f"Settings(database_url={_mask_password(self.database_url)!r}, secret_key='***', "
            f"port={self.port!r}, log_level={self.log_level!r})")
```

Everything is checked **before** anything is raised; the object is `frozen`, so nothing changes it later; `repr` hides what must never reach a log.

## Complexity

O(1). The value is operational: a missing `SECRET_KEY` makes the deployment fail at start (and `deploy.sh` roll back, chapter 12.3) instead of failing at 3 a.m.

## Another way

`pydantic-settings` (not installed in this course) gives the same with annotations and `SecretStr`. Python's `dataclasses.field(repr=False)` hides a field from the generated `repr`, which is another way to hide the secret, but it cannot mask the password **inside** a URL.
