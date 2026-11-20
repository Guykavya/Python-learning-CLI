import pytest

from solution import Post, User, create_app, db


@pytest.fixture
def app():
    app = create_app({"TESTING": True})
    with app.app_context():
        db.session.add_all([User(username="asha"), User(username="ravi")])
        db.session.commit()
    return app


def client_for(app, user_id=None):
    client = app.test_client()
    if user_id:
        with client.session_transaction() as s:
            s["user_id"] = user_id
    return client


def assert_error(r, status, code):
    assert r.status_code == status, f"expected {status}, got {r.status_code}: {r.get_data(as_text=True)[:120]}"
    assert r.is_json, f"An API error must be JSON, got {r.content_type}."
    error = r.get_json()["error"]
    assert error["code"] == code and isinstance(error["message"], str) and error["message"], (
        f"Use the shape {{'error': {{'code': '{code}', 'message': '...'}}}} (api_error); got {r.get_json()}")
    return error


def make_post(app, user_id=1, title="Hello", body="text"):
    r = client_for(app, user_id).post("/api/posts", json={"title": title, "body": body})
    assert r.status_code == 201, f"setup failed: {r.status_code} {r.get_data(as_text=True)[:100]}"
    return r.get_json()


def test_create(app):
    r = client_for(app, 1).post("/api/posts", json={"title": "  Hello  ", "body": "text"})
    assert r.status_code == 201, f"Creating answers 201, got {r.status_code}."
    assert r.get_json() == {"id": 1, "title": "Hello", "body": "text", "author_id": 1}
    assert r.headers["Location"] == "/api/posts/1", "Add the Location header of the new post (url_for)."


def test_create_requires_login_and_gives_json_not_a_redirect(app):
    r = app.test_client().post("/api/posts", json={"title": "x"})
    assert_error(r, 401, "unauthorized")


def test_create_envelope_errors(app):
    c = client_for(app, 1)
    assert_error(c.post("/api/posts", data="title=x", content_type="text/plain"), 415, "unsupported_media_type")
    assert_error(c.post("/api/posts", json=[1, 2]), 400, "bad_request")
    assert_error(c.post("/api/posts", data="{broken", content_type="application/json"), 400, "bad_request")


def test_create_validation_lists_the_fields(app):
    error = assert_error(client_for(app, 1).post("/api/posts", json={"title": "", "body": 5}), 422, "validation_error")
    assert set(error["fields"]) == {"title", "body"}, f"List every bad field under error.fields; got {error.get('fields')}"
    assert_error(client_for(app, 1).post("/api/posts", json={"title": "x" * 101}), 422, "validation_error")


def test_list_is_newest_first(app):
    for t in ("a", "b", "c"):
        make_post(app, title=t)
    items = app.test_client().get("/api/posts").get_json()["items"]
    assert [p["title"] for p in items] == ["c", "b", "a"]


def test_show_and_404(app):
    make_post(app, title="Hello")
    assert app.test_client().get("/api/posts/1").get_json()["title"] == "Hello"
    error = assert_error(app.test_client().get("/api/posts/99"), 404, "not_found")
    assert "99" in error["message"]


def test_patch_changes_only_given_fields(app):
    make_post(app, title="Hello", body="old body")
    c = client_for(app, 1)
    r = c.patch("/api/posts/1", json={"body": "new body"})
    assert r.status_code == 200 and r.get_json() == {"id": 1, "title": "Hello", "body": "new body", "author_id": 1}, (
        f"PATCH changes only the fields that are present; got {r.get_json()}")
    r = c.patch("/api/posts/1", json={"title": "New"})
    assert r.get_json()["title"] == "New" and r.get_json()["body"] == "new body"
    assert c.patch("/api/posts/1", json={}).get_json()["title"] == "New", "An empty patch changes nothing."


def test_patch_validates_given_fields_only(app):
    make_post(app)
    c = client_for(app, 1)
    assert_error(c.patch("/api/posts/1", json={"title": ""}), 422, "validation_error")
    assert c.patch("/api/posts/1", json={"body": "ok"}).status_code == 200, "A missing title is fine in a PATCH."


def test_patch_and_delete_by_another_user_are_403(app):
    make_post(app, user_id=1, title="Asha's")
    other = client_for(app, 2)
    assert_error(other.patch("/api/posts/1", json={"title": "Hacked"}), 403, "forbidden")
    assert_error(other.delete("/api/posts/1"), 403, "forbidden")
    assert app.test_client().get("/api/posts/1").get_json()["title"] == "Asha's"


def test_anonymous_patch_delete_are_401(app):
    make_post(app)
    assert_error(app.test_client().patch("/api/posts/1", json={"title": "x"}), 401, "unauthorized")
    assert_error(app.test_client().delete("/api/posts/1"), 401, "unauthorized")


def test_missing_post_is_404_for_patch_and_delete(app):
    c = client_for(app, 1)
    assert_error(c.patch("/api/posts/42", json={"title": "x"}), 404, "not_found")
    assert_error(c.delete("/api/posts/42"), 404, "not_found")


def test_delete(app):
    make_post(app)
    r = client_for(app, 1).delete("/api/posts/1")
    assert r.status_code == 204 and r.get_data() == b""
    assert_error(app.test_client().get("/api/posts/1"), 404, "not_found")
