import pytest
from flask import url_for

from solution import create_app


@pytest.fixture
def client():
    return create_app().test_client()


def text(r):
    return r.get_data(as_text=True)


def test_user(client):
    r = client.get("/user/asha")
    assert r.status_code == 200 and text(r) == "User: asha", f"expected 'User: asha', got {r.status_code} {text(r)!r}"


def test_post_id_is_an_int(client):
    r = client.get("/post/7")
    assert text(r) == "Post 7 (int)", f"the int converter passes a real int to the view; got {text(r)!r}"


def test_post_with_letters_is_404(client):
    assert client.get("/post/abc").status_code == 404, "Use <int:post_id>: a non-number must be a 404, not a 500 or a 200."


def test_negative_number_is_404(client):
    assert client.get("/post/-3").status_code == 404, "The int converter accepts digits only (no minus sign)."


def test_path_converter_keeps_slashes(client):
    r = client.get("/files/a/b/c.txt")
    assert r.status_code == 200 and text(r) == "File: a/b/c.txt", (
        f"<path:subpath> must match slashes too; got {r.status_code} {text(r)!r}")


def test_user_without_name_is_404(client):
    assert client.get("/user/").status_code == 404


def test_url_for_builds_the_url():
    app = create_app()
    with app.test_request_context():
        assert url_for("show_post", post_id=7) == "/post/7", "url_for('show_post', post_id=7) must build /post/7."
        assert url_for("user_profile", username="asha") == "/user/asha"
        assert url_for("show_file", subpath="x/y.txt") == "/files/x/y.txt"
