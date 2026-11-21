## Approach

| Setting | default | image `ENV` | `env_file` | `environment:` | `run -e` | Result |
|---|---|---|---|---|---|---|
| `LOG_LEVEL` | INFO | | DEBUG | `${LOG_LEVEL:-WARNING}`: shell has `ERROR` | | **ERROR** |
| `APP_ENV` | development | production | staging | | | **staging** |
| `PORT` | 8000 | | | `${PORT:-8080}`: not in the shell, `.env` has `9000` | | **9000** |
| `WORKERS` | 1 | 2 | 4 | 6 | 8 | **8** |
| `REDIS_URL` | none | | | `redis://${REDIS_HOST:-redis}:6379/0`: no shell value, no `.env` value, fallback `redis` | | **redis://redis:6379/0** |

Answers to the questions: for `LOG_LEVEL`, the `.env` value (`CRITICAL`), the `env_file` value (`DEBUG`) and the fallback (`WARNING`) never matter, because the shell value fills the substitution and `environment:` beats `env_file:`. Deleting the `.env` file would change `PORT` (it would become `8080`), not the others.

## Cost

Reading only. In practice: when a setting has the "wrong" value, run `docker compose config` (it prints the resolved file with every `${...}` filled in) and `docker compose exec api env` (what the process really sees), instead of guessing which layer won.

## Another way

Run the program and print each layer as it applies; or change one source at a time (delete `SHELL`, then `DOTENV`) and predict the new output before running.
