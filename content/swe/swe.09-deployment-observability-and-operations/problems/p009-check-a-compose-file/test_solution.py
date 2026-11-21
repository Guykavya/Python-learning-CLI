import pytest

from solution import check_compose

CHAPTER = '''# compose.yaml
name: pbtut

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
      REDIS_URL: redis://redis:6379/0
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
    volumes:
      - api-data:/data
    ports:
      - "127.0.0.1:${PUBLIC_PORT:-18080}:8000"
    depends_on:
      redis:
        condition: service_healthy
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: ["redis-server", "--save", "", "--appendonly", "no"]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 3s
      timeout: 2s
      retries: 5
    restart: unless-stopped

volumes:
  api-data:
'''

WITH_PROXY = '''name: pbtut
services:
  api:
    build: {context: .}
    image: pagebound-api:${APP_VERSION:-dev}
    environment:
      APP_SECRET_KEY: ${APP_SECRET_KEY:?set it}
    volumes:
      - api-data:/data
    depends_on:
      redis:
        condition: service_healthy
    logging:
      driver: json-file
      options: {max-size: "10m", max-file: "3"}
  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
  nginx:
    image: nginx:alpine
    ports:
      - "127.0.0.1:${PUBLIC_PORT:-18080}:80"
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      api:
        condition: service_healthy
volumes:
  api-data:
'''

BAD = '''
services:
  web:
    build: .
    ports: ["8000:8000"]
    environment:
      DATABASE_PASSWORD: hunter2
    volumes:
      - ./data:/data
    depends_on:
      - db
  db:
    image: postgres:16
    ports: ["5432:5432"]
'''


def one(text):
    return check_compose(text)


def test_chapter_compose_is_clean():
    assert one(CHAPTER) == [], "The compose file of chapter 6.2 follows every rule: expected []."


def test_compose_with_the_proxy_is_clean():
    assert one(WITH_PROXY) == [], \
        "With the proxy: the API is built here (its Dockerfile has the HEALTHCHECK), is not published, and the read-only bind mount of nginx is fine."


def test_bad_compose_gets_every_finding():
    assert one(BAD) == [
        ("db", "dependency-port-published"), ("db", "no-healthcheck"),
        ("web", "data-not-in-named-volume"), ("web", "depends-not-healthy"), ("web", "inline-secret"),
    ], "Five findings, sorted by (service, code)."


def test_depends_on_condition_variants():
    base = "services:\n  app:\n    build: .\n    depends_on:\n{}\n  db:\n    image: postgres:16\n    healthcheck: {{test: [\"CMD\", \"true\"]}}\n"
    started = base.format("      db:\n        condition: service_started")
    no_condition = base.format("      db: {}")
    healthy = base.format("      db:\n        condition: service_healthy")
    assert one(started) == [("app", "depends-not-healthy")], "service_started only waits for the process to start, not to be ready."
    assert one(no_condition) == [("app", "depends-not-healthy")], "Without a condition it is the same as service_started."
    assert one(healthy) == [], "service_healthy plus a healthcheck on the dependency is the safe form."


def test_no_healthcheck_only_for_images_not_built_here():
    text = "services:\n  app:\n    build: .\n    depends_on:\n      cache:\n        condition: service_healthy\n  cache:\n    image: redis:7\n"
    assert one(text) == [("cache", "no-healthcheck")], "A pulled image has no HEALTHCHECK we know of: the compose file must define one."


def test_published_dependency_port():
    text = ("services:\n  proxy:\n    image: nginx\n    ports: ['127.0.0.1:80:80']\n    depends_on:\n      api:\n        condition: service_healthy\n"
            "  api:\n    build: .\n    ports: ['127.0.0.1:8000:8000']\n")
    assert one(text) == [("api", "dependency-port-published")], \
        "The API is a dependency of the proxy: publishing it too lets clients bypass the proxy (even on 127.0.0.1 it is a finding in this checker)."


@pytest.mark.parametrize("volume, bad", [
    ("api-data:/data", False),
    ("api-data:/data:rw", False),
    ("./nginx.conf:/etc/nginx/nginx.conf:ro", False),
    ("/etc/ssl/certs:/certs:ro", False),
    ("./data:/data", True),
    ("./data:/data:rw", True),
    ("/srv/data:/data", True),
    ("~/data:/data", True),
    ("/data", True),
    ("undeclared:/data", True),
])
def test_volumes(volume, bad):
    text = f"services:\n  app:\n    image: x\n    volumes:\n      - {volume}\nvolumes:\n  api-data:\n"
    assert one(text) == ([("app", "data-not-in-named-volume")] if bad else []), f"volume {volume!r}: finding expected={bad}"


def test_long_volume_syntax():
    bind = "services:\n  app:\n    image: x\n    volumes:\n      - {type: bind, source: ./d, target: /d}\n"
    ro = "services:\n  app:\n    image: x\n    volumes:\n      - {type: bind, source: ./d, target: /d, read_only: true}\n"
    named = "services:\n  app:\n    image: x\n    volumes:\n      - {type: volume, source: v, target: /d}\nvolumes:\n  v:\n"
    assert one(bind) == [("app", "data-not-in-named-volume")], "A writable bind mount in long syntax is a finding."
    assert one(ro) == [] and one(named) == [], "A read-only bind mount and a declared named volume are fine."


@pytest.mark.parametrize("environment, bad", [
    ("{APP_SECRET_KEY: '${APP_SECRET_KEY:?set it}'}", False),
    ("{APP_SECRET_KEY: abc123}", True),
    ("{DB_PASSWORD: hunter2}", True),
    ("{STRIPE_KEY: sk_live_x}", True),
    ("{APP_SECRET_KEY: }", False),
    ("{LOG_LEVEL: INFO, APP_VERSION: '1.0'}", False),
    ("['APP_TOKEN=abc']", True),
    ("['APP_TOKEN']", False),
    ("['APP_TOKEN=${APP_TOKEN}']", False),
])
def test_inline_secrets(environment, bad):
    text = f"services:\n  app:\n    image: x\n    environment: {environment}\n"
    assert one(text) == ([("app", "inline-secret")] if bad else []), f"environment {environment}: finding expected={bad}"


def test_env_file_is_the_right_way():
    assert one("services:\n  app:\n    image: x\n    env_file: [.env]\n") == [], "Secrets in an env_file are not findings."


@pytest.mark.parametrize("text", ["just text", "services: []", "services: {}", "- a\n- b", ""])
def test_not_a_compose_file(text):
    with pytest.raises(ValueError):
        one(text)


def test_result_is_sorted_and_unique():
    text = ("services:\n  a:\n    image: x\n    volumes: ['/one', '/two']\n    environment: {X_TOKEN: a, Y_TOKEN: b}\n")
    assert one(text) == [("a", "data-not-in-named-volume"), ("a", "inline-secret")], "Report each (service, code) once."
