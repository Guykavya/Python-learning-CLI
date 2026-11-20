import pytest

from solution import User, create_app, db


@pytest.fixture
def app():
    return create_app({"TESTING": True, "PROPAGATE_EXCEPTIONS": False})


def register(client, name):
    return client.post("/register", json={"username": name})


def count_users(app):
    with app.app_context():
        return db.session.scalar(db.select(db.func.count()).select_from(User))


def test_first_registration(app):
    r = register(app.test_client(), "asha")
    assert r.status_code == 201 and r.get_json() == {"id": 1, "username": "asha"}


@pytest.mark.parametrize("name", ["", "ab", "Asha", "a b", "x" * 21, None, 5])
def test_invalid_names_are_400(app, name):
    r = register(app.test_client(), name)
    assert r.status_code == 400, f"{name!r} is not a valid username: expected 400, got {r.status_code}."


def test_duplicate_is_409_with_suggestions(app):
    client = app.test_client()
    register(client, "asha")
    r = register(client, "asha")
    assert r.status_code == 409, (
        f"A taken name must answer 409, got {r.status_code}: {r.get_data(as_text=True)[:120]}. "
        "After the failed commit call db.session.rollback() before you query again.")
    assert r.get_json() == {"error": "username 'asha' is taken", "suggestions": ["asha1", "asha2"]}


def test_suggestions_skip_names_that_exist_too(app):
    client = app.test_client()
    for name in ("asha", "asha1", "asha3"):
        assert register(client, name).status_code == 201
    r = register(client, "asha")
    assert r.get_json()["suggestions"] == ["asha2", "asha4"], f"got {r.get_json()}: suggest the first two FREE names."


def test_next_request_still_works(app):
    client = app.test_client()
    register(client, "asha")
    register(client, "asha")
    assert register(client, "ravi").status_code == 201, "The request after a duplicate must work."
    assert count_users(app) == 2, "The failed insert must leave no row behind."


def test_next_request_works_inside_one_long_app_context(app):
    """Many test suites keep an app context open: then the session is NOT removed between requests."""
    client = app.test_client()
    with app.app_context():
        assert register(client, "asha").status_code == 201
        assert register(client, "asha").status_code == 409
        r = register(client, "ravi")
        assert r.status_code == 201, (
            f"After the duplicate the next request got {r.status_code}. The session stayed in the 'needs rollback' "
            "state: roll it back in the except branch, do not rely on the end of the request.")
        assert db.session.scalar(db.select(db.func.count()).select_from(User)) == 2


def test_two_duplicates_in_a_row(app):
    client = app.test_client()
    register(client, "asha")
    assert register(client, "asha").status_code == 409
    assert register(client, "asha").status_code == 409, "A second duplicate must also give 409."
