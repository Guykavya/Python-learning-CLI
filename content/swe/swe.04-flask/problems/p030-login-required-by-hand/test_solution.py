from urllib.parse import parse_qs, urlsplit

import pytest

from solution import create_app, login_required


@pytest.fixture
def app():
    return create_app({"TESTING": True})


@pytest.fixture
def client(app):
    return app.test_client()


def log_in(client, user_id):
    with client.session_transaction() as s:
        s["user_id"] = user_id


def test_public_pages_stay_public(client):
    assert client.get("/").get_data(as_text=True) == "home"
    assert client.get("/auth/login").get_data(as_text=True) == "login page"


def test_anonymous_is_redirected_with_next(client):
    r = client.get("/dashboard")
    assert r.status_code == 302, f"An anonymous visitor must be redirected (302), got {r.status_code}."
    parts = urlsplit(r.headers["Location"])
    assert parts.path == "/auth/login", f"Redirect to the login page, got {r.headers['Location']!r}"
    assert parse_qs(parts.query) == {"next": ["/dashboard"]}, f"Add next=<the wanted path> (url_for('login', next=request.path)); got query {parts.query!r}"


def test_logged_in_user_sees_the_page(client):
    log_in(client, 1)
    r = client.get("/dashboard")
    assert r.status_code == 200 and r.get_data(as_text=True) == "Dashboard of asha"
    log_in(client, 2)
    assert client.get("/settings").get_data(as_text=True) == "Settings of ravi", "g.user must be the user of the session."


def test_view_arguments_are_passed_on(client):
    log_in(client, 1)
    assert client.get("/posts/5/private").get_data(as_text=True) == "Private post 5 for asha", "The wrapper must pass *args and **kwargs to the view."
    with client.session_transaction() as s:
        s.clear()
    r = client.get("/posts/5/private")
    assert r.status_code == 302 and parse_qs(urlsplit(r.headers["Location"]).query) == {"next": ["/posts/5/private"]}


def test_unknown_user_id_counts_as_anonymous(client):
    log_in(client, 999)
    r = client.get("/dashboard")
    assert r.status_code == 302, "A session pointing at a user that does not exist is not a login."


def test_g_user_is_none_for_anonymous_visitors(app):
    seen = []

    @app.get("/who")
    def who():
        from flask import g
        seen.append(g.user)
        return "ok"

    app.test_client().get("/who")
    assert seen == [None], "Set g.user = None when nobody is logged in (so views can test 'g.user is None')."


def test_wraps_keeps_the_function_names(app):
    assert {"dashboard", "settings", "private_post"} <= set(app.view_functions), (
        f"functools.wraps keeps the endpoint names; found {sorted(app.view_functions)}")


def test_decorator_keeps_metadata():
    def sample():
        """doc text"""

    wrapped = login_required(sample)
    assert wrapped.__name__ == "sample" and wrapped.__doc__ == "doc text", "Use @functools.wraps(view) on the inner function."
    assert getattr(wrapped, "__wrapped__", None) is sample
