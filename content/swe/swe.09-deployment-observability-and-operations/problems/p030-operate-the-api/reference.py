import contextvars
import json
import logging
import re
import sqlite3
import sys
import threading
import time
import uuid
from collections import defaultdict
from contextlib import asynccontextmanager, closing
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field


# ------------------------------------------------------------------ settings (problem p003)
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
        e = {} if environ is None else environ
        settings = cls(
            env=e.get("APP_ENV", "development"),
            version=e.get("APP_VERSION", "dev"),
            database_path=e.get("DATABASE_PATH", "pagebound.db"),
            log_level=e.get("LOG_LEVEL", "INFO").upper(),
            secret_key=e.get("APP_SECRET_KEY", ""),
        )
        problems = []
        if settings.env not in {"development", "test", "production"}:
            problems.append(f"APP_ENV must be development, test or production (got {settings.env!r})")
        if settings.log_level not in {"DEBUG", "INFO", "WARNING", "ERROR"}:
            problems.append(f"LOG_LEVEL is not a valid level: {settings.log_level!r}")
        if settings.env == "production" and len(settings.secret_key) < 32:
            problems.append("APP_SECRET_KEY must be set to at least 32 characters in production")
        if problems:
            raise ConfigError("; ".join(problems))
        return settings

    def __repr__(self):
        return (f"Settings(env={self.env!r}, version={self.version!r}, database_path={self.database_path!r}, "
                f"log_level={self.log_level!r}, secret_key='***')")


# ------------------------------------------------------------------ JSON logs with a request id (problem p013)
request_id_var = contextvars.ContextVar("request_id", default="-")


class JsonFormatter(logging.Formatter):
    def format(self, record):
        entry = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)) + f".{int(record.msecs):03d}Z",
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": request_id_var.get(),
        }
        for key, value in (getattr(record, "fields", None) or {}).items():
            if key not in entry:
                entry[key] = value
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, separators=(",", ":"), default=str)


def configure_logging(level="INFO", stream=None):
    handler = logging.StreamHandler(stream or sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level)


# ------------------------------------------------------------------ metrics (problem p019)
BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)


class Metrics:
    def __init__(self):
        self._lock = threading.Lock()
        self.requests = defaultdict(int)
        self.bucket_counts = defaultdict(lambda: [0] * len(BUCKETS))
        self.sums = defaultdict(float)
        self.counts = defaultdict(int)
        self.in_flight = 0

    def observe(self, method, route, status, seconds):
        with self._lock:
            self.requests[(method, route, str(status))] += 1
            key = (method, route)
            self.sums[key] += seconds
            self.counts[key] += 1
            for i, upper in enumerate(BUCKETS):
                if seconds <= upper:
                    self.bucket_counts[key][i] += 1

    def observe_request(self, scope, status, seconds):
        route = getattr(scope.get("route"), "path", "unmatched")
        self.observe(scope["method"], route, status, seconds)

    def render(self):
        with self._lock:
            lines = ["# HELP http_requests_total Requests handled, by method, route template and status.",
                     "# TYPE http_requests_total counter"]
            for (method, route, status), n in sorted(self.requests.items()):
                lines.append(f'http_requests_total{{method="{method}",route="{route}",status="{status}"}} {n}')
            lines += ["# HELP http_request_duration_seconds Request latency.", "# TYPE http_request_duration_seconds histogram"]
            for (method, route), counts in sorted(self.bucket_counts.items()):
                labels = f'method="{method}",route="{route}"'
                for upper, n in zip(BUCKETS, counts):
                    lines.append(f'http_request_duration_seconds_bucket{{{labels},le="{upper}"}} {n}')
                lines.append(f'http_request_duration_seconds_bucket{{{labels},le="+Inf"}} {self.counts[(method, route)]}')
                lines.append(f'http_request_duration_seconds_sum{{{labels}}} {self.sums[(method, route)]:.6f}')
                lines.append(f'http_request_duration_seconds_count{{{labels}}} {self.counts[(method, route)]}')
            lines += ["# HELP http_requests_in_flight Requests being handled right now.", "# TYPE http_requests_in_flight gauge",
                      f"http_requests_in_flight {self.in_flight}"]
            return "\n".join(lines) + "\n"


# ------------------------------------------------------------------ request context (problem p014)
log = logging.getLogger("pagebound")
VALID_ID = re.compile(r"^[A-Za-z0-9._-]{8,64}$")
QUIET_PATHS = {"/healthz", "/readyz", "/metrics"}


class RequestContext:
    def __init__(self, app, metrics):
        self.app, self.metrics = app, metrics

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        incoming = dict(scope["headers"]).get(b"x-request-id", b"").decode("latin-1")
        rid = incoming if VALID_ID.match(incoming) else uuid.uuid4().hex
        token = request_id_var.set(rid)
        started, status = time.perf_counter(), 500
        self.metrics.in_flight += 1

        async def send_with_id(message):
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                message.setdefault("headers", []).append((b"x-request-id", rid.encode()))
            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
        except Exception:
            log.exception("unhandled error")
            response = JSONResponse({"error": "internal error", "request_id": rid}, status_code=500)
            await response(scope, receive, send_with_id)
        finally:
            seconds = time.perf_counter() - started
            self.metrics.in_flight -= 1
            self.metrics.observe_request(scope, status, seconds)
            if scope["path"] not in QUIET_PATHS:
                log.info("request finished", extra={"fields": {
                    "method": scope["method"], "path": scope["path"], "status": status, "duration_ms": round(seconds * 1000, 1)}})
            request_id_var.reset(token)


# ------------------------------------------------------------------ the service
class OrderIn(BaseModel):
    item: str = Field(min_length=1, max_length=100)
    quantity: int = Field(ge=1, le=1000)


def create_app(settings=None):
    settings = settings or Settings.from_env()
    configure_logging(settings.log_level)
    metrics = Metrics()

    @asynccontextmanager
    async def lifespan(app):
        with closing(sqlite3.connect(settings.database_path)) as db:
            db.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, item TEXT NOT NULL, quantity INTEGER NOT NULL)")
            db.commit()
        log.info("starting", extra={"fields": {"version": settings.version, "env": settings.env}})
        yield
        app.state.draining = True                                  # readiness goes red before we exit
        log.info("shutting down")

    app = FastAPI(title="Pagebound API", version=settings.version, lifespan=lifespan,
                  docs_url=None if settings.env == "production" else "/docs")
    app.state.draining = False
    app.add_middleware(RequestContext, metrics=metrics)

    @app.get("/")
    def index():
        return {"service": "pagebound", "version": settings.version, "env": settings.env}

    @app.post("/orders", status_code=201)
    def create_order(body: OrderIn):
        with closing(sqlite3.connect(settings.database_path)) as db:
            cur = db.execute("INSERT INTO orders (item, quantity) VALUES (?, ?)", (body.item, body.quantity))
            db.commit()
        log.info("order created", extra={"fields": {"order_id": cur.lastrowid, "item": body.item}})
        return {"id": cur.lastrowid, **body.model_dump()}

    @app.get("/orders/{order_id}")
    def get_order(order_id: int):
        with closing(sqlite3.connect(settings.database_path)) as db:
            row = db.execute("SELECT id, item, quantity FROM orders WHERE id = ?", (order_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "order not found")
        return {"id": row[0], "item": row[1], "quantity": row[2]}

    @app.get("/boom")
    def boom():
        raise RuntimeError("simulated bug while building the invoice")

    @app.get("/healthz")
    def healthz():
        return {"status": "alive"}

    @app.get("/readyz")
    def readyz():
        problems = {}
        if app.state.draining:
            problems["draining"] = "shutting down"
        try:
            with closing(sqlite3.connect(settings.database_path, timeout=1)) as db:
                db.execute("SELECT 1").fetchone()
        except sqlite3.Error as exc:
            problems["database"] = str(exc)
        if problems:
            return JSONResponse({"status": "not ready", "problems": problems}, status_code=503)
        return {"status": "ready"}

    @app.get("/metrics", response_class=PlainTextResponse)
    def metrics_endpoint():
        return metrics.render()

    return app


# ------------------------------------------------------------------ the deployment texts (problems p006, p009, p023)
DOCKERFILE = r'''# syntax=docker/dockerfile:1
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN useradd --create-home --uid 10001 app
WORKDIR /srv

# dependencies first: this layer is rebuilt only when requirements.txt changes
COPY requirements.txt .
RUN pip install -r requirements.txt

# application code last: it changes most often
COPY app ./app

ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION} \
    DATABASE_PATH=/data/pagebound.db
RUN mkdir /data && chown app:app /data
VOLUME /data

USER app
EXPOSE 8000
HEALTHCHECK --interval=5s --timeout=2s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/readyz', timeout=1).status == 200 else 1)"]

# exec form: uvicorn is PID 1 and receives SIGTERM directly
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
'''

COMPOSE = '''name: pagebound

services:
  api:
    build:
      context: .
      args:
        APP_VERSION: ${APP_VERSION:-dev}
    image: pagebound-api:${APP_VERSION:-dev}
    environment:
      APP_ENV: production
      APP_VERSION: ${APP_VERSION:-dev}
      APP_SECRET_KEY: ${APP_SECRET_KEY:?set APP_SECRET_KEY in the .env file}
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
    volumes:
      - api-data:/data
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "127.0.0.1:${PUBLIC_PORT:-18080}:80"
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      api:
        condition: service_healthy
    restart: unless-stopped

volumes:
  api-data:
'''

WORKFLOW = '''name: ci

on:
  push:
    branches: [main]
    tags: ["v*"]
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.13", "3.14"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
      - name: Install dependencies
        run: pip install -r requirements.txt pytest httpx mypy
      - name: Type check
        run: make typecheck
      - name: Tests
        run: make test

  image:
    needs: test
    runs-on: ubuntu-latest
    timeout-minutes: 15
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - name: Log in to GitHub Container Registry
        if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/v')
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Build (and push on main or on a version tag)
        uses: docker/build-push-action@v6
        with:
          context: .
          push: ${{ github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/v') }}
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          build-args: APP_VERSION=${{ github.sha }}
'''
