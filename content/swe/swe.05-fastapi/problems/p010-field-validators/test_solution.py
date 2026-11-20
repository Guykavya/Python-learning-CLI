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


def test_everything_is_cleaned(client):
    r = client.post("/signups", json={"name": "  asha rao ", "email": " Asha@Example.COM ", "interests": "python, sql,,"})
    assert r.status_code == 201, f"A valid signup must give 201, got {r.status_code}: {r.text}"
    body = r.json()
    assert body.get("name") == "Asha Rao", (
        f"name: strip then title-case; got {body.get('name')!r}. If it is None, your validator forgot 'return v'.")
    assert body.get("email") == "asha@example.com", f"email: strip and lower-case; got {body.get('email')!r}"
    assert body.get("interests") == ["python", "sql"], (
        f"A comma string must become a list of stripped, non-empty pieces; got {body.get('interests')!r}. "
        "This needs mode='before': in the default 'after' mode Pydantic refuses a str for list[str] first.")


def test_list_interests_still_work(client):
    r = client.post("/signups", json={"name": "Ravi", "email": "ravi@example.com", "interests": ["chess", "go"]})
    assert r.status_code == 201, r.text
    assert r.json()["interests"] == ["chess", "go"], "A real JSON list must pass through the before-validator unchanged."


def test_interests_default_is_empty(client):
    r = client.post("/signups", json={"name": "Ravi", "email": "ravi@example.com"})
    assert r.status_code == 201, r.text
    assert r.json()["interests"] == []


def test_validators_work_without_fastapi():
    s = SignupIn(name="meera   iyer", email="M@X.IO", interests="a,b")
    assert (s.name, s.email, s.interests) == ("Meera   Iyer", "m@x.io", ["a", "b"]), (
        f"The model itself does the cleaning, got {(s.name, s.email, s.interests)}")


@pytest.mark.parametrize("email", [
    "ravi@mailinator.com", "ravi@Mailinator.com", " X@MAILINATOR.COM ", "a@tempmail.dev", "a@10minutemail.com",
])
def test_disposable_domains_are_refused(client, email):
    found = errors(client.post("/signups", json={"name": "Ravi", "email": email}))
    assert (["body", "email"], "value_error") in found, (
        f"{email!r} uses a disposable domain (compare AFTER lower-casing and stripping); got {found}")


@pytest.mark.parametrize("email", ["ravi", "@example.com", "ravi@", "a@b@c.com"])
def test_malformed_emails_are_refused(client, email):
    found = errors(client.post("/signups", json={"name": "Ravi", "email": email}))
    assert (["body", "email"], "value_error") in found, (
        f"{email!r} needs exactly one @ with text on both sides; raise ValueError. Got {found}")


def test_blank_name_is_refused(client):
    found = errors(client.post("/signups", json={"name": "   ", "email": "a@b.co"}))
    assert (["body", "name"], "value_error") in found, f"A name of only spaces is empty after strip: raise ValueError. Got {found}"


def test_type_errors_still_come_from_pydantic(client):
    found = errors(client.post("/signups", json={"name": "Ravi", "email": "a@b.co", "interests": 5}))
    assert (["body", "interests"], "list_type") in found, (
        f"A before-validator must return non-str values unchanged so Pydantic can still refuse 5; got {found}")
