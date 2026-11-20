import pytest

import solution
from solution import create_app


@pytest.fixture
def client():
    return create_app({"TESTING": True}).test_client()


def login(client, user, password, next=None):
    url = "/auth/login" + (f"?next={next}" if next is not None else "")
    return client.post(url, data={"username": user, "password": password})


def test_normal_login_still_works(client):
    r = login(client, "asha", "correct horse")
    assert r.status_code == 302 and r.headers["Location"] == "/", f"A correct login redirects to '/', got {r.status_code} {r.headers.get('Location')}"
    assert client.get("/").get_data(as_text=True) == "Hello asha"


def test_wrong_password_is_401_and_does_not_log_in(client):
    r = login(client, "asha", "bad")
    assert r.status_code == 401
    assert client.get("/").get_data(as_text=True) == "Hello anonymous"


def test_unknown_user_and_wrong_password_look_the_same(client):
    unknown = login(client, "nobody", "whatever")
    wrong = login(client, "asha", "whatever")
    assert unknown.status_code == wrong.status_code == 401, "Both failures answer 401."
    assert unknown.get_data() == wrong.get_data(), (
        f"The body must be identical, or an attacker learns which names exist: {unknown.get_data(as_text=True)!r} vs {wrong.get_data(as_text=True)!r}")


def test_unknown_user_costs_the_same_work(client, monkeypatch):
    calls = []
    real = solution.check_password_hash
    monkeypatch.setattr(solution, "check_password_hash", lambda h, p: calls.append(h) or real(h, p))
    login(client, "nobody", "x")
    login(client, "asha", "x")
    assert len(calls) == 2, (
        f"Each attempt must run check_password_hash exactly once (got {len(calls)} calls for 2 attempts). "
        "For an unknown user compare against DUMMY_HASH, so the response time does not reveal that the name does not exist.")


def test_an_unknown_user_with_the_dummy_password_is_still_refused(client):
    assert login(client, "nobody", "not-a-real-password").status_code == 401, "Comparing with the dummy hash must never log anybody in."


def test_login_starts_a_fresh_session(client):
    with client.session_transaction() as s:
        s["cart"] = "3 items"
        s["csrf_token"] = "old-token"
    login(client, "asha", "correct horse")
    with client.session_transaction() as s:
        assert "cart" not in s and "csrf_token" not in s, (
            f"The old session content survived the login ({dict(s)}): call session.clear() first (session fixation).")
        assert s["user"] == "asha"


@pytest.mark.parametrize("target", ["/dashboard", "/dashboard?tab=2", "/a/b/c", "/"])
def test_local_next_is_followed(client, target):
    r = login(client, "asha", "correct horse", next=target)
    assert r.status_code == 302 and r.headers["Location"] == target, f"next={target!r} is a local path and must be followed; got {r.headers.get('Location')!r}"


@pytest.mark.parametrize("target", [
    "https://evil.example/", "http://evil.example", "//evil.example", "/\\evil.example",
    "javascript:alert(1)", "evil.example", "///evil.example", "http:evil.example", " //evil.example",
])
def test_foreign_next_is_ignored(client, target):
    r = login(client, "asha", "correct horse", next=target)
    assert r.status_code == 302 and r.headers["Location"] == "/", (
        f"next={target!r} must not be followed (open redirect); expected '/', got {r.headers.get('Location')!r}")


def test_empty_next_goes_home(client):
    r = login(client, "asha", "correct horse", next="")
    assert r.headers["Location"] == "/"
