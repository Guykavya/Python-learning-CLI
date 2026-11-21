import contextlib
import json
import os
import shutil

import pytest
import yaml
from fastapi.testclient import TestClient

from solution import COMPOSE, DOCKERFILE, WORKFLOW, ConfigError, Settings, create_app


@pytest.fixture(autouse=True)
def restore_root_logging():
    import logging
    root = logging.getLogger()
    saved, level = root.handlers[:], root.level
    yield
    root.handlers[:] = saved
    root.setLevel(level)


@pytest.fixture
def settings(tmp_path):
    (tmp_path / "data").mkdir()
    return Settings(database_path=str(tmp_path / "data" / "t.db"))


@pytest.fixture
def make_client(settings, capsys):
    """make_client() creates the app and enters its lifespan INSIDE the test (so the JSON logs go to the stdout that capsys captures)."""
    stack = contextlib.ExitStack()

    def make():
        return stack.enter_context(TestClient(create_app(settings), raise_server_exceptions=False))

    yield make
    stack.close()


def records(capsys):
    """Every line the service wrote to stdout, parsed. A line that is not JSON fails the test."""
    out = capsys.readouterr().out
    return [json.loads(line) for line in out.splitlines() if line.strip()]


def finished(recs):
    return [r for r in recs if r["msg"] == "request finished"]


# ----------------------------------------------------------------------------- configuration
def test_defaults_and_secret_hiding():
    assert Settings.from_env({}).env == "development" and Settings.from_env().log_level == "INFO", "No variables: the development defaults."
    assert "s" * 40 not in repr(Settings.from_env({"APP_SECRET_KEY": "s" * 40})), "The secret must never be printed."
    assert "secret_key='***'" in repr(Settings.from_env({"APP_SECRET_KEY": "s" * 40}))


def test_configuration_fails_fast_with_every_problem():
    with pytest.raises(ConfigError, match="APP_SECRET_KEY"):
        Settings.from_env({"APP_ENV": "production"})
    with pytest.raises(ConfigError) as info:
        Settings.from_env({"APP_ENV": "prod", "LOG_LEVEL": "LOUD"})
    assert "APP_ENV" in str(info.value) and "LOG_LEVEL" in str(info.value), f"Report all problems in ONE error; got {info.value}"
    assert Settings.from_env({"APP_ENV": "production", "APP_SECRET_KEY": "k" * 32, "APP_VERSION": "1.4.2", "LOG_LEVEL": "warning"}).log_level == "WARNING"


# ----------------------------------------------------------------------------- the service itself
def test_orders_round_trip_and_validation(make_client):
    client = make_client()
    created = client.post("/orders", json={"item": "pen", "quantity": 3})
    assert created.status_code == 201 and created.json() == {"id": 1, "item": "pen", "quantity": 3}, f"Got {created.status_code} {created.text}"
    assert client.get("/orders/1").json() == {"id": 1, "item": "pen", "quantity": 3}
    assert client.get("/orders/999").status_code == 404, "A missing order is a 404."
    assert client.post("/orders", json={"item": "pen", "quantity": 0}).status_code == 422
    assert client.post("/orders", json={"item": "", "quantity": 1}).status_code == 422
    assert client.get("/").json() == {"service": "pagebound", "version": "dev", "env": "development"}


def test_request_ids(make_client):
    client = make_client()
    assert client.get("/", headers={"X-Request-ID": "trace-me-0001"}).headers["x-request-id"] == "trace-me-0001", "A valid incoming id is reused."
    generated = client.get("/").headers["x-request-id"]
    assert len(generated) == 32, "Otherwise a uuid4 hex string is generated."
    assert client.get("/", headers={"X-Request-ID": "bad id with spaces"}).headers["x-request-id"] != "bad id with spaces", "A malformed id is replaced."


def test_start_up_is_logged(settings, capsys):
    with TestClient(create_app(Settings(env="test", version="1.4.2", database_path=settings.database_path))):
        pass
    recs = records(capsys)
    starting = [r for r in recs if r["msg"] == "starting"]
    assert starting and starting[0]["version"] == "1.4.2" and starting[0]["env"] == "test", f"Log 'starting' with the version and env fields; got {recs}"
    assert starting[0]["request_id"] == "-", "Outside a request the id is '-'."


# ----------------------------------------------------------------------------- outcome 1: follow one failing request
def test_a_failing_request_is_traceable_by_its_id_end_to_end(make_client, capsys):
    client = make_client()
    capsys.readouterr()                                           # forget the start-up line
    response = client.get("/boom", headers={"X-Request-ID": "trace-me-0002"})
    assert response.status_code == 500
    assert response.json() == {"error": "internal error", "request_id": "trace-me-0002"}, f"The client gets only the id; got {response.text}"
    assert "simulated bug" not in response.text, "Internal details must not reach the client."
    client.get("/orders/1", headers={"X-Request-ID": "someone-else-1"})
    mine = [r for r in records(capsys) if r["request_id"] == "trace-me-0002"]
    assert [r["level"] for r in mine] == ["ERROR", "INFO"], f"Two lines carry the id: the ERROR with the traceback, then the access line; got {[(r['level'], r['msg']) for r in mine]}"
    assert mine[0]["msg"] == "unhandled error" and "RuntimeError: simulated bug while building the invoice" in mine[0]["exception"], \
        "The traceback is in ONE 'exception' field of the ERROR record."
    assert (mine[1]["msg"], mine[1]["status"], mine[1]["path"], mine[1]["method"]) == ("request finished", 500, "/boom", "GET")


def test_every_log_line_is_json_with_the_fixed_keys(make_client, capsys):
    client = make_client()
    client.post("/orders", json={"item": "pen", "quantity": 1})
    client.get("/nothing-here")
    recs = records(capsys)
    assert recs, "The service must log to stdout."
    for rec in recs:
        assert {"ts", "level", "logger", "msg", "request_id"} <= set(rec), f"Every record has the fixed keys; got {sorted(rec)}"
    created = [r for r in recs if r["msg"] == "order created"]
    assert created and created[0]["order_id"] == 1 and created[0]["item"] == "pen", "Facts go into fields, the message stays constant."


def test_probes_and_scrapes_are_not_logged(make_client, capsys):
    client = make_client()
    capsys.readouterr()
    client.get("/healthz")
    client.get("/readyz")
    client.get("/metrics")
    assert finished(records(capsys)) == [], "Do not log health probes and metric scrapes: they would bury the real events."


# ----------------------------------------------------------------------------- health, drain
def test_liveness_and_readiness_with_a_failing_database(settings, make_client):
    client = make_client()
    assert client.get("/healthz").json() == {"status": "alive"}
    assert client.get("/readyz").json() == {"status": "ready"}
    shutil.rmtree(os.path.dirname(settings.database_path))        # the database becomes unreachable
    not_ready = client.get("/readyz")
    assert not_ready.status_code == 503 and "database" in not_ready.json()["problems"], f"A database outage makes readiness red; got {not_ready.text}"
    assert client.get("/healthz").status_code == 200, "Liveness must NOT depend on the database (a restart would not help: restart storm)."
    os.makedirs(os.path.dirname(settings.database_path))
    assert client.get("/readyz").status_code == 200, "When the database is back the service recovers without a restart."


def test_readiness_flips_while_draining(make_client):
    client = make_client()
    assert client.get("/readyz").status_code == 200
    client.app.state.draining = True
    r = client.get("/readyz")
    assert (r.status_code, r.json()["problems"]) == (503, {"draining": "shutting down"}), f"Got {r.status_code} {r.text}"
    assert client.get("/healthz").status_code == 200 and client.get("/orders/1").status_code in (200, 404), \
        "A draining instance is alive and still serves the requests that still arrive."


def test_shutdown_starts_draining_and_says_so(settings, capsys):
    app = create_app(settings)
    with TestClient(app) as c:
        assert c.get("/readyz").status_code == 200
        assert app.state.draining is False
    assert app.state.draining is True, "Leaving the lifespan (SIGTERM) must set app.state.draining: readiness goes red before the process exits."
    assert [r["msg"] for r in records(capsys) if r["msg"] == "shutting down"] == ["shutting down"]


# ----------------------------------------------------------------------------- metrics
def test_metrics_use_route_templates_and_count_the_500(make_client):
    client = make_client()
    client.get("/orders/1")
    client.get("/orders/2")
    client.get("/boom")
    client.get("/wp-login.php")
    text = client.get("/metrics").text
    assert 'http_requests_total{method="GET",route="/orders/{order_id}",status="404"} 2' in text, "Route TEMPLATE as the label, never the raw path."
    assert "/orders/1" not in text and "/orders/2" not in text, "Raw paths would explode the number of time series."
    assert 'http_requests_total{method="GET",route="/boom",status="500"} 1' in text, "The failed request is counted as a 500."
    assert 'http_requests_total{method="GET",route="unmatched",status="404"} 1' in text, "Scanner traffic shares the label 'unmatched'."
    for line in ("# TYPE http_requests_total counter", "# TYPE http_request_duration_seconds histogram", "# TYPE http_requests_in_flight gauge"):
        assert line in text.splitlines(), f"Missing {line!r}"
    assert 'http_request_duration_seconds_count{method="GET",route="/boom"} 1' in text


# ----------------------------------------------------------------------------- the deployment texts
def test_texts_are_not_empty():
    for name, text in (("DOCKERFILE", DOCKERFILE), ("COMPOSE", COMPOSE), ("WORKFLOW", WORKFLOW)):
        assert isinstance(text, str) and text.strip(), f"{name} is empty: write the file's text into the constant."


def test_the_dockerfile_passes_the_linter_and_has_a_healthcheck(checkers):
    assert checkers.lint_dockerfile(DOCKERFILE) == [], f"The Dockerfile must pass the linter of p006; findings: {checkers.lint_dockerfile(DOCKERFILE)}"
    assert "HEALTHCHECK" in DOCKERFILE and "/readyz" in DOCKERFILE, "The image carries a HEALTHCHECK that asks /readyz (Compose's service_healthy relies on it)."


def test_the_compose_file_passes_the_checker_and_has_the_chapters_shape(checkers):
    assert checkers.check_compose(COMPOSE) == [], f"The compose file must pass the checker of p009; findings: {checkers.check_compose(COMPOSE)}"
    services = yaml.safe_load(COMPOSE)["services"]
    assert "build" in services["api"] and "ports" not in services["api"], "The API is built here and is NOT published (only the proxy is)."
    assert "max-size" in str(services["api"].get("logging")), "Rotate the container logs (chapter 8.6): logging.options.max-size."
    assert services["nginx"]["ports"] and all(p.startswith("127.0.0.1:") for p in services["nginx"]["ports"]), "The proxy publishes only on 127.0.0.1."
    assert services["nginx"]["depends_on"]["api"]["condition"] == "service_healthy", "nginx waits for a healthy API."


def test_the_workflow_passes_the_linter(checkers):
    workflow = yaml.safe_load(WORKFLOW)
    assert isinstance(workflow, dict), "WORKFLOW must be YAML for a mapping."
    assert checkers.check_workflow(workflow) == [], f"The workflow must pass the linter of p023 with no errors and no warnings; findings: {checkers.check_workflow(workflow)}"
