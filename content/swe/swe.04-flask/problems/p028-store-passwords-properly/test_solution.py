import pytest
from sqlalchemy import text

from solution import User, create_app, db


@pytest.fixture
def app():
    return create_app({"TESTING": True})


def add_user(name, password):
    user = User(username=name)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def test_correct_and_wrong_password(app):
    with app.app_context():
        user = add_user("asha", "correct horse")
        assert user.check_password("correct horse") is True
        assert user.check_password("wrong") is False, "A wrong password must give False."
        assert user.check_password("Correct horse") is False, "Passwords are case-sensitive."
        assert user.check_password("") is False


def test_the_plain_password_is_not_stored(app):
    with app.app_context():
        add_user("asha", "correct horse")
        row = db.session.execute(text("SELECT * FROM user")).one()
        assert all("correct horse" not in str(value) for value in row), f"The plain password is in the database row: {tuple(row)}. Store generate_password_hash(...)."


def test_the_hash_has_werkzeugs_format(app):
    with app.app_context():
        user = add_user("asha", "correct horse")
        method = user.password_hash.split(":")[0]
        assert method in {"scrypt", "pbkdf2"}, f"Use werkzeug.security.generate_password_hash; got a hash starting with {user.password_hash[:12]!r}."
        assert user.password_hash.count("$") == 2, "Werkzeug hashes look like 'method$salt$hash'."


def test_same_password_gives_different_hashes(app):
    with app.app_context():
        a = add_user("asha", "same password")
        b = add_user("ravi", "same password")
        assert a.password_hash != b.password_hash, "Two equal passwords must not give equal hashes: a random salt is part of each hash."
        assert a.check_password("same password") and b.check_password("same password")


def test_set_password_rejects_bad_values(app):
    with app.app_context():
        user = User(username="x")
        for bad in ("", None, 12345, b"bytes"):
            with pytest.raises(ValueError):
                user.set_password(bad)
        assert user.password_hash is None, "A rejected password must not change the stored hash."


def test_user_without_a_hash_never_matches(app):
    with app.app_context():
        user = User(username="nohash")
        assert user.check_password("anything") is False
        assert user.check_password("") is False, "An empty password must not match a missing hash."


def test_non_string_input_is_false(app):
    with app.app_context():
        user = add_user("asha", "correct horse")
        assert user.check_password(None) is False
        assert user.check_password(123) is False


def test_the_hash_is_not_exposed(app):
    with app.app_context():
        user = add_user("asha", "correct horse")
        data = user.to_dict()
        assert data == {"id": 1, "username": "asha"}, f"to_dict() is what you send to clients: id and username only, got {data}"


def test_changing_the_password(app):
    with app.app_context():
        user = add_user("asha", "old password")
        user.set_password("new password")
        db.session.commit()
        assert user.check_password("new password") and not user.check_password("old password")
