import pytest
from bs4 import BeautifulSoup

from solution import create_app


@pytest.fixture
def app():
    return create_app({"TESTING": True, "PROPAGATE_EXCEPTIONS": False})


@pytest.fixture
def client(app):
    return app.test_client()


def token_from(client):
    html = client.get("/form").get_data(as_text=True)
    field = BeautifulSoup(html, "html.parser").find("input", attrs={"name": "csrf_token"})
    assert field is not None, "The form must contain <input type='hidden' name='csrf_token' value='...'>."
    return field["value"]


def balance(app):
    return app.extensions["bank"]["balance"]


def test_form_contains_a_long_random_token(client):
    token = token_from(client)
    assert len(token) >= 32, f"Use secrets.token_urlsafe(32): the token is too short ({len(token)} chars)."


def test_token_is_stable_inside_a_session_and_differs_between_sessions(app):
    a, b = app.test_client(), app.test_client()
    assert token_from(a) == token_from(a), "The token must stay the same during the session (store it in session['csrf_token'])."
    assert token_from(a) != token_from(b), "Two sessions must have different tokens."


def test_valid_post_works(client, app):
    token = token_from(client)
    r = client.post("/deposit", data={"amount": "50", "csrf_token": token})
    assert r.status_code == 200 and r.get_data(as_text=True) == "Deposited 50", f"A POST with the right token must work, got {r.status_code}."
    assert balance(app) == 50


def test_missing_token_is_400(client, app):
    token_from(client)
    r = client.post("/deposit", data={"amount": "50"})
    assert r.status_code == 400, f"A POST without a token must be refused with 400, got {r.status_code}."
    assert balance(app) == 0, "The view must not run when the token is missing."


def test_post_without_any_session_is_400(client, app):
    r = client.post("/deposit", data={"amount": "50", "csrf_token": "anything"})
    assert r.status_code == 400 and balance(app) == 0, "No session token exists: a guessed token must fail (do not compare '' with ... )."


def test_empty_token_is_400_even_without_a_session(client, app):
    r = client.post("/deposit", data={"amount": "50", "csrf_token": ""})
    assert r.status_code == 400 and balance(app) == 0, "'' == '' must NOT count as a match."


@pytest.mark.parametrize("wrong", ["wrong", "x" * 43, "é" * 10, "Zk3"])
def test_wrong_token_is_400(client, app, wrong):
    token_from(client)
    r = client.post("/deposit", data={"amount": "50", "csrf_token": wrong})
    assert r.status_code == 400, (
        f"A wrong token must give 400, got {r.status_code}. "
        "If it is 500, hmac.compare_digest raised TypeError on a non-ASCII str: compare .encode() bytes.")
    assert balance(app) == 0


def test_token_from_another_session_is_refused(app):
    victim, attacker = app.test_client(), app.test_client()
    stolen = token_from(attacker)
    token_from(victim)
    r = victim.post("/deposit", data={"amount": "50", "csrf_token": stolen})
    assert r.status_code == 400 and balance(app) == 0, "A token is valid only for the session that received it."


def test_header_token_for_javascript(client, app):
    token = token_from(client)
    r = client.post("/deposit", data={"amount": "7"}, headers={"X-CSRF-Token": token})
    assert r.status_code == 200 and balance(app) == 7, "Accept the token also in the X-CSRF-Token header."


@pytest.mark.parametrize("method", ["put", "patch", "delete"])
def test_every_unsafe_method_is_checked(client, method):
    token_from(client)
    r = getattr(client, method)("/deposit")
    assert r.status_code == 400, f"{method.upper()} changes data too: the CSRF check must run before the routing error (405) for it ({r.status_code})."


def test_get_never_changes_data(client, app):
    token_from(client)
    for _ in range(3):
        assert client.get("/balance").get_data(as_text=True) == "0"
    assert client.get("/deposit?amount=99").status_code == 405, "Deposits must exist only as POST; a GET must not be able to change the balance."
    assert balance(app) == 0
