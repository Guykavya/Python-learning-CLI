import pytest

from solution import create_app


@pytest.fixture
def client():
    app = create_app({"TESTING": True, "PROPAGATE_EXCEPTIONS": False})
    return app.test_client()


def test_create_and_show(client):
    r = client.post("/posts", json={"title": "Hello", "body": "First"})
    assert r.status_code == 201, f"Creating a post answers 201, got {r.status_code}."
    assert r.get_json() == {"id": 1, "title": "Hello", "body": "First"}
    assert client.get("/posts/1").get_json() == {"id": 1, "title": "Hello", "body": "First"}


def test_body_is_optional(client):
    assert client.post("/posts", json={"title": "x"}).get_json()["body"] == ""


@pytest.mark.parametrize("payload", [{}, {"title": ""}, {"title": "   "}, {"body": "only body"}])
def test_title_is_required(client, payload):
    r = client.post("/posts", json=payload)
    assert r.status_code == 400 and r.get_json() == {"error": "title is required"}, f"{payload}: expected 400 title is required, got {r.status_code} {r.get_data(as_text=True)[:80]}"
    assert client.get("/posts").get_json() == [], "A rejected post must not be stored."


def test_list_is_ordered(client):
    for title in ("a", "b", "c"):
        client.post("/posts", json={"title": title})
    assert [p["title"] for p in client.get("/posts").get_json()] == ["a", "b", "c"]


def test_missing_post_is_404_not_500(client):
    r = client.get("/posts/99")
    assert r.status_code == 404, f"A post that does not exist is a 404, got {r.status_code}. Use db.get_or_404(Post, post_id)."


def test_delete(client):
    client.post("/posts", json={"title": "x"})
    r = client.delete("/posts/1")
    assert r.status_code == 204 and r.get_data() == b"", "DELETE answers 204 and an empty body."
    assert client.get("/posts/1").status_code == 404, "The post must really be gone."
    assert client.get("/posts").get_json() == []


def test_delete_missing_is_404(client):
    assert client.delete("/posts/5").status_code == 404, "Deleting something that does not exist is a 404, not a 500."


def test_two_apps_have_separate_databases():
    a, b = create_app({"TESTING": True}), create_app({"TESTING": True})
    a.test_client().post("/posts", json={"title": "only in a"})
    assert b.test_client().get("/posts").get_json() == [], "Each app must have its own in-memory database."
