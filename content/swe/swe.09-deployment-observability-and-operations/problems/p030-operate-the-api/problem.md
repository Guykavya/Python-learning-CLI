# Operate the API

Chapter section 15 (the project: Dockerise, deploy and monitor your API with CI). This is the module's project in miniature, and a **build** problem: you assemble what you wrote in the earlier problems into one operable service, and write the three deployment texts. Docker, Compose and GitHub are never run by the tests; the tests run the service with `TestClient` and judge your texts with the **same checkers you wrote** (the reference versions of p006, p009 and p023 are bundled in the tests).

## What to write (`solution.py`)

**1. Settings** (problem p003, with the chapter's names).

```python
class ConfigError(RuntimeError): ...
@dataclass(frozen=True)
class Settings:
    env: str = "development"; version: str = "dev"; database_path: str = "pagebound.db"
    log_level: str = "INFO"; secret_key: str = ""
    @classmethod
    def from_env(cls, environ=None): ...      # environ is a dict; None means no variables at all
```

`from_env` reads `APP_ENV`, `APP_VERSION`, `DATABASE_PATH`, `LOG_LEVEL` (upper-cased) and `APP_SECRET_KEY`. `APP_ENV` must be `development`, `test` or `production`; `LOG_LEVEL` one of `DEBUG`, `INFO`, `WARNING`, `ERROR`; in **production** the secret key needs at least **32 characters**. All problems go into **one** `ConfigError` (joined with `"; "`, naming the variables). `repr` never shows the secret (`secret_key='***'`).

**2. The service**, `create_app(settings=None)`, a FastAPI app that:

- calls `configure_logging(settings.log_level)` (JSON logs on **stdout**, problem p013) and keeps the request-id context variable;
- wraps every request in the request-id middleware of problem p014, logging `request finished` with `method`, `path`, `status`, `duration_ms` (not for `/healthz`, `/readyz`, `/metrics`), answering unhandled errors with `{"error": "internal error", "request_id": ...}` and the `X-Request-ID` header on every response;
- records every request in a `Metrics` registry (problem p019): route **template** as label, `unmatched` for no route, in-flight gauge;
- has these routes: `GET /` returns `{"service": "pagebound", "version": ..., "env": ...}`; `POST /orders` (`item`: 1 to 100 characters, `quantity`: 1 to 1000; `201`, stores the order in SQLite at `settings.database_path` and returns `{"id", "item", "quantity"}`); `GET /orders/{order_id}` (`404` with `order not found`); `GET /boom` raises `RuntimeError("simulated bug while building the invoice")`; `GET /healthz` (problem p017: always `200 {"status": "alive"}`); `GET /readyz` (`503` with `{"status": "not ready", "problems": {...}}` when the database cannot be opened with `sqlite3.connect(settings.database_path, timeout=1)` and queried, **named `database`**, or when `app.state.draining` is true, named `draining`); `GET /metrics` (the Prometheus text);
- uses a **lifespan**: at start it creates the table `orders (id INTEGER PRIMARY KEY, item TEXT NOT NULL, quantity INTEGER NOT NULL)` and logs `starting` with the fields `version` and `env`; at shutdown it sets `app.state.draining = True` (readiness red) and logs `shutting down` (problem p018).

**3. The deployment texts**: three string constants.

- `DOCKERFILE`: passes `lint_dockerfile` of p006 (`[]`) and contains a `HEALTHCHECK` that calls `/readyz`.
- `COMPOSE`: passes `check_compose` of p009 (`[]`); the service `api` is **built here**, uses a **named volume**, has **log rotation** (`logging.options.max-size`), and is **not published**; the service `nginx` is the only one with `ports`, bound to `127.0.0.1`, and waits for `api` with `condition: service_healthy`.
- `WORKFLOW`: a GitHub Actions workflow that passes `check` of p023 (no errors and no warnings): pinned actions, timeouts, permissions, and a step that runs `make test`.

The chapter's own files (5.2, 6.2 with the edit of 7.2, and 11.4) are the model for all three. Everything in the chapter's acceptance checklist that can be tested without Docker is tested here: a failing request is **traceable by its id end to end**, readiness flips during drain, the metrics count the 500, and the deployment texts are clean.

## Example

```text
POST /orders {"item": "pen", "quantity": 3}  -> 201 {"id": 1, "item": "pen", "quantity": 3}
GET /boom with X-Request-ID: trace-me-0002  -> 500 {"error": "internal error", "request_id": "trace-me-0002"}
stdout (one JSON object per line), among others:
{"ts":"...","level":"ERROR","logger":"pagebound","msg":"unhandled error","request_id":"trace-me-0002","exception":"Traceback ... RuntimeError: simulated bug ..."}
{"ts":"...","level":"INFO","logger":"pagebound","msg":"request finished","request_id":"trace-me-0002","method":"GET","path":"/boom","status":500,"duration_ms":2.3}
```
