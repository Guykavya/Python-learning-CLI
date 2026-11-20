import pytest
from fastapi.testclient import TestClient

from solution import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_everything_sent(client):
    headers = [
        ("User-Agent", "demo/1.0"),
        ("X-Request-ID", "abc-1"),
        ("X-Token", "t1"),
        ("X-Token", "t2"),
        ("Cookie", "session=s123"),
    ]
    body = client.get("/whoami", headers=headers).json()
    assert body.get("user_agent") == "demo/1.0", (
        f"user_agent should come from the User-Agent header, got {body.get('user_agent')!r}. "
        "Without Header() a str parameter is read from the query string.")
    assert body.get("request_id") == "abc-1", f"x_request_id: Annotated[str | None, Header()] matches X-Request-ID; got {body.get('request_id')!r}"
    assert body.get("tokens") == ["t1", "t2"], (
        f"X-Token was sent twice; read it with list[str] | None and Header(). Got {body.get('tokens')!r}")
    assert body.get("session") == "s123", f"session comes from the cookie: Annotated[str | None, Cookie()]; got {body.get('session')!r}"
    assert body.get("logged_in") is True


def test_header_names_are_case_insensitive(client):
    body = client.get("/whoami", headers={"x-request-id": "lower-1"}).json()
    assert body.get("request_id") == "lower-1", "HTTP header names are case-insensitive: x-request-id is the same header as X-Request-ID."


def test_query_string_is_not_a_header(client):
    body = client.get("/whoami?x_request_id=from-query&session=from-query").json()
    assert body.get("request_id") is None and body.get("session") is None, (
        f"Values in the QUERY string must be ignored: these parameters come from headers and cookies. Got {body}")


def test_missing_values_are_none(client):
    del client.headers["user-agent"]          # TestClient adds 'User-Agent: testclient' by default
    body = client.get("/whoami").json()
    assert body == {"user_agent": None, "request_id": None, "tokens": [], "session": None, "logged_in": False}, (
        f"With nothing sent every value is None (tokens an empty list) and logged_in is False; got {body}")


def test_default_user_agent_of_testclient(client):
    body = client.get("/whoami").json()
    assert body.get("user_agent") == "testclient", (
        f"TestClient sends 'User-Agent: testclient' by itself; your endpoint should see it. Got {body.get('user_agent')!r}")


def test_other_cookies_do_not_count(client):
    body = client.get("/whoami", headers={"Cookie": "theme=dark"}).json()
    assert body.get("session") is None and body.get("logged_in") is False, (
        f"Only the cookie named 'session' logs you in; got {body}")
