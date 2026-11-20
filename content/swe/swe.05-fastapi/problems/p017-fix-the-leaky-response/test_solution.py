import pytest
from fastapi.testclient import TestClient

import solution
from solution import app

PASSWORD = "correct horse"


@pytest.fixture
def client():
    solution.FAKE_DB.clear()
    with TestClient(app) as c:
        yield c
    solution.FAKE_DB.clear()


def secret_keys(data, path="response"):
    """Every key, at any depth, whose name contains 'password' or 'hash'."""
    found = []
    if isinstance(data, dict):
        for key, value in data.items():
            if "password" in key.lower() or "hash" in key.lower():
                found.append(f"{path}[{key!r}]")
            found += secret_keys(value, f"{path}[{key!r}]")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            found += secret_keys(item, f"{path}[{i}]")
    return found


def assert_no_leak(response, where):
    leaks = secret_keys(response.json())
    assert not leaks, f"{where} leaks secret fields: {leaks}. Only fields declared in UserOut may leave the server."
    assert PASSWORD not in response.text and PASSWORD[::-1] not in response.text, (
        f"{where}: the password or its hash appears in the response text: {response.text}")


def register(client, email="asha@example.com", password=PASSWORD):
    return client.post("/users", json={"email": email, "password": password})


def test_register_is_201_without_secrets(client):
    r = register(client)
    assert r.status_code == 201, f"Creating a user answers 201 Created (status_code=201); got {r.status_code}"
    assert_no_leak(r, "POST /users")
    assert r.json() == {"id": 1, "email": "asha@example.com"}, f"Expected exactly id and email, got {r.json()}"


def test_get_one_user_without_secrets(client):
    register(client)
    r = client.get("/users/1")
    assert r.status_code == 200, r.text
    assert_no_leak(r, "GET /users/1")
    assert r.json() == {"id": 1, "email": "asha@example.com"}, (
        f"Got {r.json()}. response_model=UserOut only removes fields UserOut does NOT declare: "
        "remove password_hash from UserOut.")


def test_list_without_secrets(client):
    register(client)
    register(client, email="ravi@example.com", password="battery staple")
    r = client.get("/users")
    assert r.status_code == 200, r.text
    assert_no_leak(r, "GET /users")
    assert r.json() == [{"id": 1, "email": "asha@example.com"}, {"id": 2, "email": "ravi@example.com"}], (
        f"Got {r.json()}. A list endpoint needs response_model=list[UserOut].")


def test_the_hash_is_still_stored(client):
    register(client)
    row = solution.FAKE_DB[1]
    assert row.password_hash == "pbkdf2$" + PASSWORD[::-1], (
        "The fix is in what is SENT, not what is stored: FAKE_DB must keep password_hash for logins.")


def test_unknown_user_is_404(client):
    r = client.get("/users/9")
    assert r.status_code == 404 and r.json() == {"detail": "user not found"}, f"Got {r.status_code} {r.text}"


def test_short_password_is_still_refused(client):
    r = register(client, password="short")
    assert r.status_code == 422, "UserCreate still requires at least 8 characters."
    assert solution.FAKE_DB == {}, "A refused registration stores nothing."
