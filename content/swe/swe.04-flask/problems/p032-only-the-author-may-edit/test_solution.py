import pytest
from werkzeug.exceptions import Forbidden, NotFound

from solution import create_app, get_post_for_edit


@pytest.fixture
def app():
    return create_app({"TESTING": True, "PROPAGATE_EXCEPTIONS": False})


def client_for(app, user_id):
    client = app.test_client()
    if user_id:
        with client.session_transaction() as s:
            s["user_id"] = user_id
    return client


def titles(app):
    return {i: p["title"] for i, p in app.extensions["posts"].items()}


def test_author_can_edit(app):
    r = client_for(app, 1).post("/posts/1/edit", data={"title": "New title"})
    assert r.status_code == 200 and r.get_data(as_text=True) == "updated"
    assert titles(app)[1] == "New title"


def test_other_user_cannot_edit(app):
    r = client_for(app, 1).post("/posts/2/edit", data={"title": "Hacked"})
    assert r.status_code == 403, f"Asha is not the author of post 2: expected 403 Forbidden, got {r.status_code}. Check g.user['id'] == post['author_id']."
    assert titles(app)[2] == "Ravi's post", "The forbidden edit must not change the post."


def test_author_can_delete_and_others_cannot(app):
    assert client_for(app, 1).post("/posts/2/delete").status_code == 403
    assert 2 in app.extensions["posts"], "The post of another user was deleted!"
    assert client_for(app, 2).post("/posts/2/delete").status_code == 204
    assert 2 not in app.extensions["posts"]


def test_missing_post_is_404_before_403(app):
    assert client_for(app, 1).post("/posts/99/edit", data={"title": "x"}).status_code == 404, "A missing post is 404 (not a KeyError/500)."
    assert client_for(app, 1).post("/posts/99/delete").status_code == 404


def test_anonymous_is_sent_to_login(app):
    r = client_for(app, None).post("/posts/1/edit", data={"title": "x"})
    assert r.status_code == 302 and r.headers["Location"].startswith("/auth/login"), "Anonymous users are redirected by login_required."
    assert titles(app)[1] == "Asha's post"


def test_the_helper_holds_the_check(app):
    with app.test_request_context("/"):
        from flask import g
        g.user = {"id": 1, "name": "asha"}
        assert get_post_for_edit(1)["id"] == 1
        with pytest.raises(Forbidden):
            get_post_for_edit(2)
        with pytest.raises(NotFound):
            get_post_for_edit(42)


def test_helper_refuses_when_nobody_is_logged_in(app):
    with app.test_request_context("/"):
        from flask import g
        g.user = None
        with pytest.raises(Forbidden):
            get_post_for_edit(1)


def test_a_second_user_can_edit_their_own_post(app):
    r = client_for(app, 2).post("/posts/2/edit", data={"title": "Mine"})
    assert r.status_code == 200 and titles(app)[2] == "Mine"
