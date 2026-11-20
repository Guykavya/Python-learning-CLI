import pytest
from flask import url_for

from solution import auth, blog, create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app):
    return app.test_client()


def text(r):
    return r.get_data(as_text=True)


def test_blueprints_are_registered(app):
    assert set(app.blueprints) == {"auth", "blog"}, f"register both blueprints; found {sorted(app.blueprints)}"
    assert auth.name == "auth" and blog.name == "blog"


def test_endpoint_names_have_the_blueprint_prefix(app):
    assert "auth.login" in app.view_functions and "blog.index" in app.view_functions and "blog.show" in app.view_functions, (
        f"Endpoints are '<blueprint>.<function>'; found {sorted(app.view_functions)}")
    assert "login" not in app.view_functions


def test_url_for(app):
    with app.test_request_context():
        assert url_for("auth.login") == "/auth/login", "The auth blueprint has url_prefix='/auth'."
        assert url_for("blog.index") == "/"
        assert url_for("blog.show", post_id=1) == "/post/1"


def test_auth_routes(client):
    assert text(client.get("/auth/login")) == "login page"
    assert text(client.get("/auth/profile/asha")) == "profile asha"


def test_logout_redirects_to_the_blog_home(client):
    r = client.post("/auth/logout")
    assert r.status_code == 302 and r.headers["Location"] == "/", f"Redirect with url_for('blog.index'); got {r.status_code} {r.headers.get('Location')}"
    assert client.get("/auth/logout").status_code == 405, "Logout is POST only."


def test_blog_routes(client):
    assert text(client.get("/")) == "home"
    assert text(client.get("/post/2")) == "Flask"


def test_auth_view_404_uses_the_auth_handler(client):
    r = client.get("/auth/profile/ravi")
    assert r.status_code == 404 and text(r) == "auth 404", f"abort(404) inside an auth view must reach auth's handler; got {r.status_code} {text(r)!r}"


def test_blog_view_404_uses_the_blog_handler(client):
    r = client.get("/post/99")
    assert r.status_code == 404 and text(r) == "blog 404", f"got {r.status_code} {text(r)!r}"


def test_unmatched_url_uses_the_app_handler(client):
    for path in ("/auth/nothing", "/xyz", "/post/abc"):
        r = client.get(path)
        assert r.status_code == 404 and text(r) == "app 404", (
            f"{path} matches no route, so there is no blueprint: the APP's 404 handler answers (blueprint handlers only see errors raised in their own views). Got {text(r)!r}")
