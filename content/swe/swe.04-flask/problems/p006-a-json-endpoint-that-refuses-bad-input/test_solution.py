import pytest

from solution import create_app


@pytest.fixture
def client():
    return create_app({"TESTING": True}).test_client()


def post(client, **kwargs):
    return client.post("/api/notes", **kwargs)


def test_not_json_is_415(client):
    r = post(client, data="title=Milk", content_type="application/x-www-form-urlencoded")
    assert r.status_code == 415, f"A request that is not JSON must give 415 Unsupported Media Type, got {r.status_code}."
    assert r.is_json and "error" in r.get_json(), "Even the error must be JSON: {'error': '...'}."


def test_broken_json_is_400(client):
    r = post(client, data='{"title": "Milk"', content_type="application/json")
    assert r.status_code == 400, f"Unparsable JSON is 400, got {r.status_code}. Use get_json(silent=True) and check for None."
    assert r.is_json and "error" in r.get_json()


@pytest.mark.parametrize("payload", [[1, 2], 5, "text"])
def test_json_that_is_not_an_object_is_400(client, payload):
    r = post(client, json=payload)
    assert r.status_code == 400, f"The JSON {payload!r} is not an object; that is a 400, not a crash ({r.status_code})."
    assert r.is_json and "error" in r.get_json()


def test_missing_title_lists_the_field(client):
    r = post(client, json={"body": "x"})
    assert r.status_code == 422
    data = r.get_json()
    assert data["error"] == "validation failed"
    assert set(data["fields"]) == {"title"}, f"fields should name only the bad field(s), got {sorted(data['fields'])}"


@pytest.mark.parametrize("title", ["", "   ", 5, None, "x" * 101])
def test_bad_titles(client, title):
    r = post(client, json={"title": title})
    assert r.status_code == 422, f"title={title!r:.20} is invalid: expected 422, got {r.status_code}."
    assert "title" in r.get_json()["fields"]


def test_all_bad_fields_are_listed_together(client):
    r = post(client, json={"title": "", "body": 5})
    assert r.status_code == 422
    assert set(r.get_json()["fields"]) == {"title", "body"}, "List every bad field in one answer, not only the first one."


def test_success(client):
    r = post(client, json={"title": "  Milk  ", "body": "2 litres"})
    assert r.status_code == 201, f"Success is 201 Created, got {r.status_code}."
    assert r.get_json() == {"id": 1, "title": "Milk", "body": "2 litres"}, f"got {r.get_json()}; the title is stored stripped."
    assert r.headers["Location"] == "/api/notes/1", "Add the header Location: /api/notes/<id>."
    assert client.get(r.headers["Location"]).get_json()["title"] == "Milk"


def test_body_defaults_and_ids_grow(client):
    post(client, json={"title": "a"})
    r = post(client, json={"title": "b"})
    assert r.get_json() == {"id": 2, "title": "b", "body": ""}


def test_title_of_exactly_100_is_fine(client):
    assert post(client, json={"title": "x" * 100}).status_code == 201
