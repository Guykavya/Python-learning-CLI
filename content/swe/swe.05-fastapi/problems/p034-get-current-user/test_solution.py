import jwt
import pytest
from fastapi.testclient import TestClient

from solution import app, get_clock, get_current_user, make_token

T0 = 1_700_000_000


@pytest.fixture
def env():
    clock = {"now": T0}
    app.dependency_overrides[get_clock] = lambda: clock["now"]
    try:
        with TestClient(app) as client:
            yield client, clock
    finally:
        app.dependency_overrides.clear()


def login(client, username, password):
    return client.post("/token", data={"username": username, "password": password})


def bearer(token):
    return {"Authorization": "Bearer " + token}


def assert_401(r, detail):
    assert r.status_code == 401, f"Expected 401, got {r.status_code}: {r.text}"
    assert r.json() == {"detail": detail}, f"Expected detail {detail!r}, got {r.json()}"
    assert r.headers.get("www-authenticate") == "Bearer", (
        f"A 401 for a bearer-token API must send 'WWW-Authenticate: Bearer'; got {r.headers.get('www-authenticate')!r}. "
        "Pass headers={'WWW-Authenticate': 'Bearer'} to the HTTPException.")


def test_login_gives_a_bearer_token(env):
    client, _ = env
    r = login(client, "asha", "asha-pass")
    assert r.status_code == 200, f"A correct form login answers 200, got {r.status_code}: {r.text}"
    body = r.json()
    assert body.get("token_type") == "bearer", f"token_type must be 'bearer'; got {body}"
    claims = jwt.decode(body["access_token"], options={"verify_signature": False})
    assert claims["sub"] == "1" and claims["exp"] == T0 + 900, (
        f"The token must be make_token(user id, now) with now from get_clock; claims are {claims}")


def test_wrong_password_and_unknown_user_look_the_same(env):
    client, _ = env
    assert_401(login(client, "asha", "wrong"), "Incorrect username or password")
    assert_401(login(client, "nobody", "asha-pass"), "Incorrect username or password")


def test_login_is_a_form_not_json(env):
    client, _ = env
    r = client.post("/token", json={"username": "asha", "password": "asha-pass"})
    assert r.status_code == 422, (
        f"POST /token reads a form (OAuth2PasswordRequestForm), so a JSON body has no form fields: 422; got {r.status_code}")
    assert ["body", "username"] in [e["loc"] for e in r.json()["detail"]]


def test_me_without_token(env):
    client, _ = env
    assert_401(client.get("/me"), "Not authenticated")


def test_me_with_another_scheme(env):
    client, _ = env
    assert_401(client.get("/me", headers={"Authorization": "Basic YXNoYTphc2hh"}), "Not authenticated")


def test_me_with_junk(env):
    client, _ = env
    assert_401(client.get("/me", headers=bearer("junk")), "Invalid or expired token")


def test_me_with_a_good_token(env):
    client, _ = env
    token = login(client, "asha", "asha-pass").json()["access_token"]
    r = client.get("/me", headers=bearer(token))
    assert r.status_code == 200, f"A fresh token must work, got {r.status_code}: {r.text}"
    assert r.json() == {"id": 1, "username": "asha"}, f"/me returns only id and username (never the hash); got {r.json()}"
    token = login(client, "ben", "ben-pass").json()["access_token"]
    assert client.get("/me", headers=bearer(token)).json() == {"id": 2, "username": "ben"}


def test_expiry_uses_the_clock(env):
    client, clock = env
    token = login(client, "asha", "asha-pass").json()["access_token"]
    clock["now"] = T0 + 899
    assert client.get("/me", headers=bearer(token)).status_code == 200, "1 second before expiry the token still works."
    clock["now"] = T0 + 900
    assert_401(client.get("/me", headers=bearer(token)), "Invalid or expired token")


def test_token_for_a_user_that_does_not_exist(env):
    client, _ = env
    assert_401(client.get("/me", headers=bearer(make_token(99, T0))), "Invalid or expired token")


def test_get_current_user_can_be_overridden():
    app.dependency_overrides[get_current_user] = lambda: {"id": 7, "username": "test-user", "hash": "x"}
    try:
        with TestClient(app) as client:
            r = client.get("/me")
    finally:
        app.dependency_overrides.clear()
    assert r.json() == {"id": 7, "username": "test-user"}, (
        f"/me must get its user from Depends(get_current_user), so tests can replace it; got {r.status_code} {r.text}")


def test_docs_know_the_token_url():
    schemes = app.openapi().get("components", {}).get("securitySchemes", {})
    flows = [s.get("flows", {}).get("password", {}).get("tokenUrl") for s in schemes.values()]
    assert "token" in flows, f"OAuth2PasswordBearer(tokenUrl='token') tells /docs where to log in; found {flows}"
