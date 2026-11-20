import sqlite3

import pytest

import solution


class Spy:
    """Wraps a real connection and records open/close, passing everything else through."""

    def __init__(self, real, registry):
        object.__setattr__(self, "_real", real)
        object.__setattr__(self, "closed", False)
        registry.append(self)

    def close(self):
        object.__setattr__(self, "closed", True)
        self._real.close()

    def __getattr__(self, name):
        return getattr(self._real, name)

    def __setattr__(self, name, value):
        setattr(self._real, name, value)


@pytest.fixture
def opened(monkeypatch):
    registry = []
    real_connect = sqlite3.connect
    monkeypatch.setattr(sqlite3, "connect", lambda *a, **k: Spy(real_connect(*a, **k), registry))
    return registry


@pytest.fixture
def client(tmp_path):
    app = solution.create_app({"TESTING": True, "PROPAGATE_EXCEPTIONS": False, "DATABASE": str(tmp_path / "app.db")})
    return app.test_client()


def test_a_page_without_database_opens_nothing(client, opened):
    opened.clear()
    r = client.get("/")
    assert r.status_code == 200
    assert len(opened) == 0, f"The home page never calls get_db(): no connection may be opened (opened {len(opened)}). Open lazily, not in before_request."


def test_three_calls_one_connection(client, opened):
    opened.clear()
    r = client.get("/count")
    assert r.status_code == 200 and r.get_json() == {"count": 1}, f"got {r.status_code} {r.get_data(as_text=True)[:100]}"
    assert len(opened) == 1, f"get_db() was called 3 times in ONE request: it must open ONE connection, not {len(opened)}. Keep it in g."


def test_connection_is_closed_after_the_request(client, opened):
    opened.clear()
    client.get("/count")
    assert opened and all(c.closed for c in opened), "The connection must be closed when the request ends (teardown_appcontext)."


def test_each_request_gets_its_own_connection(client, opened):
    opened.clear()
    client.get("/count")
    client.get("/count")
    assert len(opened) == 2, "One connection per request: two requests, two connections."
    assert opened[0] is not opened[1] and all(c.closed for c in opened)


def test_data_is_kept_between_requests(client):
    client.get("/count")
    assert client.get("/count").get_json() == {"count": 2}, "The INSERT must be committed and visible to the next request."


def test_connection_is_closed_even_if_the_view_raises(client, opened):
    opened.clear()
    r = client.get("/boom")
    assert r.status_code == 500
    assert len(opened) == 1 and opened[0].closed, "teardown_appcontext also runs when the view raises: the connection must still be closed."


def test_row_factory_is_set(client, opened):
    opened.clear()
    client.get("/count")
    assert opened[0].row_factory is sqlite3.Row, "Set db.row_factory = sqlite3.Row so rows can be read by column name."
