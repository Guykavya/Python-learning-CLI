import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

import solution
from solution import TeamOut, UserOut, app, to_out


class FakeTeam:
    def __init__(self, id, name):
        self.id, self.name = id, name


class FakeUser:
    def __init__(self, id, name, email, team=None):
        self.id, self.name, self.email, self.team = id, name, email, team
        self.password_hash = "pbkdf2$" + name[::-1]
        self.is_admin = False


@pytest.fixture
def client():
    solution.USERS.clear()
    solution.USERS[1] = FakeUser(1, "Asha", "asha@example.com", team=FakeTeam(7, "Platform"))
    solution.USERS[2] = FakeUser(2, "Ravi", "ravi@example.com")
    with TestClient(app) as c:
        yield c
    solution.USERS.clear()


def convert(obj):
    try:
        return to_out(obj)
    except ValidationError as e:
        pytest.fail(
            "UserOut.model_validate refused an object with attributes. Pydantic reads only dicts by default: "
            f"add model_config = ConfigDict(from_attributes=True) to UserOut AND TeamOut.\n{e}")


def test_to_out_reads_attributes():
    out = convert(FakeUser(3, "Meera", "meera@example.com"))
    assert isinstance(out, UserOut), f"to_out must return a UserOut, got {type(out).__name__}"
    assert (out.id, out.name, out.email, out.team) == (3, "Meera", "meera@example.com", None), f"Got {out!r}"


def test_secrets_and_extras_are_not_copied():
    dumped = convert(FakeUser(3, "Meera", "meera@example.com")).model_dump()
    assert "password_hash" not in dumped and "is_admin" not in dumped, (
        f"Only declared fields are copied; got keys {sorted(dumped)}")


def test_nested_object_becomes_a_nested_model():
    out = convert(FakeUser(1, "Asha", "a@x.io", team=FakeTeam(7, "Platform")))
    assert isinstance(out.team, TeamOut), (
        f"The nested team object must become a TeamOut; got {type(out.team).__name__}. TeamOut needs from_attributes too.")
    assert (out.team.id, out.team.name) == (7, "Platform")


def test_dicts_still_work():
    out = UserOut.model_validate({"id": 5, "name": "D", "email": "d@x.io"})
    assert out.id == 5, "from_attributes adds a way in; dicts keep working."


def test_missing_attribute_is_a_validation_error():
    class NoEmail:
        id, name = 1, "x"
    with pytest.raises(ValidationError):
        UserOut.model_validate(NoEmail())


def test_endpoint_returns_filtered_object(client):
    r = client.get("/users/1")
    assert r.status_code == 200, f"GET /users/1 must work; got {r.status_code}: {r.text}"
    assert r.json() == {"id": 1, "name": "Asha", "email": "asha@example.com", "team": {"id": 7, "name": "Platform"}}, (
        f"Got {r.json()}. Return the object itself and let response_model=UserOut convert and filter it.")


def test_endpoint_user_without_team(client):
    r = client.get("/users/2")
    assert r.status_code == 200, r.text
    assert r.json() == {"id": 2, "name": "Ravi", "email": "ravi@example.com", "team": None}


def test_unknown_user_is_404(client):
    r = client.get("/users/9")
    assert r.status_code == 404, f"An unknown id must give 404 via HTTPException; got {r.status_code}"
    assert r.json() == {"detail": "user not found"}, f"Got {r.json()}"
