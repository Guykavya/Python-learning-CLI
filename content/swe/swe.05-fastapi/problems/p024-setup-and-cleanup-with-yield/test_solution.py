import pytest
from fastapi.testclient import TestClient

from solution import SAVED, app, get_session, get_session_factory

LOG = []


class FakeSession:
    """Writes every call into LOG so the test can check the order."""

    def __init__(self):
        LOG.append("open")

    def add(self, item):
        LOG.append(f"add {item}")

    def commit(self):
        LOG.append("commit")

    def rollback(self):
        LOG.append("rollback")

    def close(self):
        LOG.append("close")


@pytest.fixture
def fake_client():
    LOG.clear()
    app.dependency_overrides[get_session_factory] = lambda: FakeSession
    try:
        with TestClient(app, raise_server_exceptions=False) as c:
            yield c
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def real_client():
    SAVED.clear()
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def test_success_commits_then_closes(fake_client):
    r = fake_client.post("/notes", json={"text": "hello"})
    assert r.status_code == 201, f"A good request answers 201, got {r.status_code}: {r.text}"
    assert LOG == ["open", "add hello", "commit", "close"], (
        f"Expected open, add, commit, close; got {LOG}. Commit after the yield, close in a finally block.")


def test_http_exception_rolls_back_and_keeps_its_status(fake_client):
    r = fake_client.post("/notes/duplicate", json={"text": "x"})
    assert r.status_code == 409, (
        f"The endpoint raised HTTPException(409); the client must still get 409, got {r.status_code}. "
        "After rolling back, re-raise the exception with a bare 'raise'.")
    assert LOG == ["open", "add x", "rollback", "close"], (
        f"An HTTPException is an exception too: roll back, never commit; got {LOG}.")


def test_a_bug_rolls_back_and_is_still_a_500(fake_client):
    r = fake_client.post("/notes/crash", json={"text": "x"})
    assert r.status_code == 500, f"An unhandled bug must still be a 500, got {r.status_code}"
    assert LOG == ["open", "add x", "rollback", "close"], f"Expected open, add, rollback, close; got {LOG}"


def test_close_happens_exactly_once(fake_client):
    for path in ("/notes", "/notes/duplicate", "/notes/crash"):
        LOG.clear()
        fake_client.post(path, json={"text": "t"})
        assert LOG.count("close") == 1, f"{path}: close must run exactly once; got {LOG}"
        assert LOG.count("open") == 1, f"{path}: open exactly one session per request; got {LOG}"
        assert LOG[-1] == "close", f"{path}: close is the last thing that happens; got {LOG}"


def test_the_factory_comes_from_the_dependency(fake_client):
    fake_client.post("/notes", json={"text": "a"})
    assert LOG and LOG[0] == "open", (
        "get_session did not use the overridden factory. Take the factory as a parameter "
        "with Depends(get_session_factory) and call it; do not create ListSession() directly.")


def test_real_session_saves_only_successful_requests(real_client):
    real_client.post("/notes", json={"text": "hello"})
    real_client.post("/notes/duplicate", json={"text": "dup"})
    real_client.post("/notes/crash", json={"text": "bug"})
    real_client.post("/notes", json={"text": "world"})
    assert SAVED == ["hello", "world"], (
        f"Only the successful requests may be saved; SAVED is {SAVED}. Commit only when the endpoint did not raise.")


def test_get_session_is_a_generator():
    import inspect
    assert inspect.isgeneratorfunction(get_session), "get_session must use yield (a generator dependency)."
