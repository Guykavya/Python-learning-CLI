# Who wins?

Chapter sections 3.2 (where settings come from, and who wins), 3.4 (how Docker passes settings in) and 6.2 (the Compose file). The same setting can be given in several places. The program below models the order for one container started by Docker Compose, from the weakest source to the strongest:

1. **Defaults in code** (`DEFAULTS`).
2. **`ENV` lines of the Dockerfile** (`IMAGE_ENV`).
3. **`env_file:`** of the service (`ENV_FILE`).
4. **`environment:`** of the service (`COMPOSE_ENVIRONMENT`). Its values may contain `${NAME:-fallback}`: Compose fills that in **before** the container starts, taking `NAME` from the **shell** that runs `docker compose` first, then from the **`.env` file next to `compose.yaml`**, and otherwise using the fallback. (That `.env` file is only for these substitutions; it does not set variables inside the container by itself.)
5. **`docker compose run -e NAME=value`** (`RUN_E`), the strongest.

Later sources win.

```python
import re

DEFAULTS = {"LOG_LEVEL": "INFO", "APP_ENV": "development", "PORT": "8000", "WORKERS": "1", "REDIS_URL": "none"}
IMAGE_ENV = {"APP_ENV": "production", "WORKERS": "2"}                    # ENV lines in the Dockerfile
ENV_FILE = {"APP_ENV": "staging", "LOG_LEVEL": "DEBUG", "WORKERS": "4"}  # the service's env_file:
COMPOSE_ENVIRONMENT = {                                                  # the service's environment:
    "LOG_LEVEL": "${LOG_LEVEL:-WARNING}",
    "PORT": "${PORT:-8080}",
    "WORKERS": "6",
    "REDIS_URL": "redis://${REDIS_HOST:-redis}:6379/0",
}
SHELL = {"LOG_LEVEL": "ERROR"}                                           # exported in the shell that runs `docker compose`
DOTENV = {"PORT": "9000", "LOG_LEVEL": "CRITICAL"}                       # the .env file next to compose.yaml
RUN_E = {"WORKERS": "8"}                                                 # docker compose run -e WORKERS=8 api


def substitute(text):
    """Fill in ${NAME:-fallback}: the shell first, then the .env file, then the fallback."""
    def fill(match):
        name, fallback = match.group(1), match.group(2)
        if name in SHELL:
            return SHELL[name]
        if name in DOTENV:
            return DOTENV[name]
        return fallback
    return re.sub(r"\$\{(\w+):-([^}]*)\}", fill, text)


def final(name):
    value = DEFAULTS[name]
    if name in IMAGE_ENV:
        value = IMAGE_ENV[name]
    if name in ENV_FILE:
        value = ENV_FILE[name]
    if name in COMPOSE_ENVIRONMENT:
        value = substitute(COMPOSE_ENVIRONMENT[name])
    if name in RUN_E:
        value = RUN_E[name]
    return value


for name in ["LOG_LEVEL", "APP_ENV", "PORT", "WORKERS", "REDIS_URL"]:
    print(f"{name}={final(name)}")
```

## What to write

The exact output: five lines, in the order of the final loop.

## Example

`WORKERS`: the default is 1, the image says 2, the `env_file` says 4, `environment:` says 6 and `run -e` says 8. The strongest source wins: `WORKERS=8`.

## After you answer

- `LOG_LEVEL` appears in six places. Which two of them never matter for the final value, and why?
- Which setting would change if you deleted the `.env` file? Which would not?
