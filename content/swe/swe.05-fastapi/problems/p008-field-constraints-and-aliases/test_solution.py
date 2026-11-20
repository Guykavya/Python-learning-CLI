import pytest
from fastapi.testclient import TestClient

from solution import SignupIn, app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def errors(response):
    assert response.status_code == 422, f"Expected a 422, got {response.status_code}: {response.text}"
    return [(e["loc"], e["type"]) for e in response.json()["detail"]]


def test_camel_case_name_is_accepted(client):
    r = client.post("/signups", json={"userName": "asha_k", "age": 21})
    assert r.status_code == 201, f"'userName' is the alias and must be accepted; got {r.status_code}: {r.text}"
    assert r.json() == {"user_name": "asha_k", "age": 21, "bio": ""}, f"Got {r.json()}"


def test_python_name_is_accepted_too(client):
    r = client.post("/signups", json={"user_name": "ravi", "age": 30, "bio": "hi"})
    assert r.status_code == 201, (
        f"'user_name' must work as well; got {r.status_code}: {r.text}. "
        "An alias alone accepts ONLY the alias: add model_config = ConfigDict(populate_by_name=True).")
    assert r.json() == {"user_name": "ravi", "age": 30, "bio": "hi"}


def test_model_in_python_accepts_both_names():
    assert SignupIn(userName="abc", age=20).user_name == "abc"
    assert SignupIn(user_name="abc", age=20).user_name == "abc", "populate_by_name lets Python code use the field name."


def test_boundaries_are_allowed(client):
    for body in [{"userName": "abc", "age": 13}, {"userName": "a" * 20, "age": 120, "bio": "b" * 50}]:
        r = client.post("/signups", json=body)
        assert r.status_code == 201, f"{body} is exactly on the limits and must be accepted (ge/le and min/max_length include the limit); got {r.text}"


@pytest.mark.parametrize("body, loc, kind, why", [
    ({"age": 20}, ["body", "userName"], "missing", "user_name is required; the error uses the alias"),
    ({"userName": "ab", "age": 20}, ["body", "userName"], "string_too_short", "user_name needs at least 3 characters"),
    ({"userName": "a" * 21, "age": 20}, ["body", "userName"], "string_too_long", "user_name has at most 20 characters"),
    ({"userName": "abc", "age": 12}, ["body", "age"], "greater_than_equal", "age must be at least 13: ge=13"),
    ({"userName": "abc", "age": 121}, ["body", "age"], "less_than_equal", "age must be at most 120: le=120"),
    ({"userName": "abc", "age": 20, "bio": "b" * 51}, ["body", "bio"], "string_too_long", "bio has at most 50 characters"),
])
def test_each_rule_gives_its_422(client, body, loc, kind, why):
    found = errors(client.post("/signups", json=body))
    assert (loc, kind) in found, f"{body}: expected {loc} {kind!r} ({why}); got {found}"


def test_two_broken_rules_give_two_errors(client):
    found = errors(client.post("/signups", json={"userName": "ab", "age": 12}))
    assert len(found) == 2, f"Pydantic collects every error: expected 2, got {found}"
