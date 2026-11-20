import pytest
from werkzeug.datastructures import MultiDict

from solution import validate_signup

GOOD = {"username": "asha_k", "email": "asha@example.com", "password": "long enough pw", "confirm": "long enough pw"}


def errors_of(**changes):
    form = {**GOOD, **changes}
    clean, errors = validate_signup(form)
    return errors


def test_valid_form():
    clean, errors = validate_signup(GOOD)
    assert errors == {}, f"A valid form must give no errors, got {errors}"
    assert clean == {"username": "asha_k", "email": "asha@example.com"}, f"clean must hold the username and email only, got {clean}"


def test_values_are_stripped():
    clean, errors = validate_signup({**GOOD, "username": "  asha_k ", "email": " asha@example.com\n"})
    assert errors == {}, "Strip the username and the email BEFORE validating them."
    assert clean["username"] == "asha_k" and clean["email"] == "asha@example.com"


@pytest.mark.parametrize("name", ["ab", "x" * 21, "Asha", "asha k", "asha-k", "", "ashá"])
def test_bad_usernames(name):
    assert "username" in errors_of(username=name), f"{name!r} must be rejected (3-20 chars of a-z, 0-9, _)."


@pytest.mark.parametrize("name", ["abc", "x" * 20, "a_1", "007"])
def test_good_usernames(name):
    assert "username" not in errors_of(username=name), f"{name!r} is a valid username."


def test_username_is_matched_as_a_whole():
    assert "username" in errors_of(username="asha\n"[:-1] + "!"), "'asha!' has a character outside the allowed set."
    assert "username" in errors_of(username="ok_name!!"), "Use fullmatch: a partial match would accept this."


@pytest.mark.parametrize("email", ["nope", "a@b", "a b@c.com", "a@@b.com", "@b.com", "a@.com", ""])
def test_bad_emails(email):
    assert "email" in errors_of(email=email), f"{email!r} is not a valid address."


@pytest.mark.parametrize("email", ["a@b.co", "first.last@mail.example.org", "x+tag@domain.io"])
def test_good_emails(email):
    assert "email" not in errors_of(email=email), f"{email!r} is a valid address."


def test_password_length():
    assert "password" in errors_of(password="123456789", confirm="123456789"), "9 characters are not enough; 10 are needed."
    assert "password" not in errors_of(password="1234567890", confirm="1234567890")


def test_spaces_count_in_the_password():
    assert errors_of(password="   a   b   ", confirm="   a   b   ") == {}, "A password is not stripped: spaces are characters."


def test_confirm_is_independent():
    errors = errors_of(password="short", confirm="short")
    assert set(errors) == {"password"}, f"Equal but short: only the password error; got {sorted(errors)}"
    errors = errors_of(confirm="another long password")
    assert set(errors) == {"confirm"}, f"Long enough but different: only the confirm error; got {sorted(errors)}"


def test_missing_keys_are_empty():
    clean, errors = validate_signup({})
    assert set(errors) == {"username", "email", "password"}, f"An empty form fails username, email and password (confirm '' == password ''); got {sorted(errors)}"
    assert clean == {"username": "", "email": ""}


def test_works_with_a_multidict():
    clean, errors = validate_signup(MultiDict(GOOD))
    assert errors == {} and clean["username"] == "asha_k", "request.form is a MultiDict: use .get(), not []."


def test_passwords_are_not_returned():
    clean, _ = validate_signup(GOOD)
    assert "password" not in clean and "confirm" not in clean, "Never put passwords into the dict you may send back to the page."
