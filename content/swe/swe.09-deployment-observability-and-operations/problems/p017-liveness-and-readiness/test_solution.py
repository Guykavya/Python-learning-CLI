import sqlite3

import pytest
from fastapi.testclient import TestClient

from solution import create_app


class Check:
    """A dependency check that counts its calls and can be broken."""

    def __init__(self, error=None):
        self.error, self.calls = error, 0

    def __call__(self):
        self.calls += 1
        if self.error is not None:
            raise self.error


def test_all_healthy():
    client = TestClient(create_app({"database": Check(), "redis": Check()}))
    assert client.get("/healthz").json() == {"status": "alive"}
    r = client.get("/readyz")
    assert (r.status_code, r.json()) == (200, {"status": "ready"}), f"Everything works: 200 and ready; got {r.status_code} {r.text}"


def test_liveness_never_calls_a_check():
    database = Check(sqlite3.OperationalError("unable to open database file"))
    client = TestClient(create_app({"database": database}))
    for _ in range(3):
        r = client.get("/healthz")
        assert (r.status_code, r.json()) == (200, {"status": "alive"}), "Liveness stays 200 even when the database is down: a restart would not fix it."
    assert database.calls == 0, "/healthz must not call any check: if liveness depended on the database, an outage would restart every container (restart storm)."


def test_readiness_names_the_failing_check():
    database = Check(sqlite3.OperationalError("unable to open database file"))
    client = TestClient(create_app({"database": database, "redis": Check()}))
    r = client.get("/readyz")
    assert r.status_code == 503, f"A failed dependency makes the service not ready: 503; got {r.status_code}"
    assert r.json() == {"status": "not ready", "problems": {"database": "unable to open database file"}}, \
        f"Answer 503 with the failing check's name and its message; got {r.text}"


def test_every_check_runs_and_all_failures_are_listed():
    a, b, c = Check(RuntimeError("a is down")), Check(), Check(ConnectionError("c is down"))
    client = TestClient(create_app({"a": a, "b": b, "c": c}))
    r = client.get("/readyz")
    assert r.json()["problems"] == {"a": "a is down", "c": "c is down"}, \
        f"Run every check, do not stop at the first failure, so the operator sees everything; got {r.text}"
    assert (a.calls, b.calls, c.calls) == (1, 1, 1), "Each check is called exactly once per request."


def test_empty_message_falls_back_to_the_class_name():
    client = TestClient(create_app({"redis": Check(TimeoutError())}))
    assert client.get("/readyz").json()["problems"] == {"redis": "TimeoutError"}, "str(TimeoutError()) is empty: use the class name."


def test_draining_turns_readiness_red_but_not_liveness():
    app = create_app({"database": Check()})
    client = TestClient(app)
    assert client.get("/readyz").status_code == 200
    app.state.draining = True
    r = client.get("/readyz")
    assert (r.status_code, r.json()) == (503, {"status": "not ready", "problems": {"draining": "shutting down"}}), \
        f"A draining instance reports 503 with a 'draining' problem; got {r.status_code} {r.text}"
    assert client.get("/healthz").status_code == 200, "A draining instance is still alive: do not restart it."


def test_draining_and_a_failure_together():
    app = create_app({"database": Check(RuntimeError("down"))})
    app.state.draining = True
    assert TestClient(app).get("/readyz").json()["problems"] == {"draining": "shutting down", "database": "down"}


def test_recovery_without_restart():
    database = Check(RuntimeError("down"))
    client = TestClient(create_app({"database": database}))
    assert client.get("/readyz").status_code == 503
    database.error = None
    assert client.get("/readyz").status_code == 200, "When the dependency returns, readiness recovers by itself (the chapter's Redis experiment)."


def test_state_is_set_at_creation():
    assert create_app({}).state.draining is False, "app.state.draining must exist and be False when the app is created."
    assert TestClient(create_app({})).get("/readyz").json() == {"status": "ready"}, "With no checks the service is ready."
