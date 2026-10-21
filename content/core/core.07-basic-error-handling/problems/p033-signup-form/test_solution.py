import ast
from pathlib import Path

from solution import validate_signup

TREE = ast.parse(Path(__file__).with_name("solution.py").read_text())
GOOD = {"username": "asha_99", "age": "21", "email": "asha@mail.in", "password": "tiger2024"}


def with_(**changes):
    form = dict(GOOD)
    form.update(changes)
    return form


def errors_for(field, value):
    return validate_signup(with_(**{field: value})).get(field)


def test_valid_form():
    assert validate_signup(GOOD) == {}, "A valid form has no errors: return {}."
    assert validate_signup(with_(extra="ignored")) == {}, "Ignore fields that are not in the table."


def test_example_reports_every_field():
    got = validate_signup({"username": "as", "age": "twelve", "email": "asha.mail.in", "password": "tiger"})
    assert got == {"username": "use 3 to 15 letters, digits or _",
                   "age": "age must be a whole number, like 21",
                   "email": "email must look like name@example.com",
                   "password": "password must be at least 8 characters"}, (
        f"Got {got}. Every field must be checked, even after an earlier field failed: catch each "
        "field's ValueError separately and keep going.")


def test_required():
    assert validate_signup({}) == {f: "this field is required" for f in ["username", "age", "email", "password"]}, (
        "Missing fields are 'this field is required', not a KeyError.")
    assert errors_for("email", "   ") == "this field is required", "A blank value counts as missing."


def test_values_are_stripped():
    assert validate_signup(with_(username="  asha_99 ", age=" 21 ")) == {}, "Strip values before checking."


def test_username_rules():
    assert errors_for("username", "a" * 16) == "use 3 to 15 letters, digits or _"
    assert errors_for("username", "asha k") == "use 3 to 15 letters, digits or _"
    assert errors_for("username", "abc") is None


def test_age_rules():
    assert errors_for("age", "21.5") == "age must be a whole number, like 21"
    assert errors_for("age", "12") == "age must be from 13 to 120"
    assert errors_for("age", "121") == "age must be from 13 to 120"
    assert errors_for("age", "13") is None and errors_for("age", "120") is None, "13 and 120 are allowed."


def test_email_rules():
    for bad in ["asha.mail.in", "@mail.in", "asha@", "a@b@c.in", "asha@mailin", "asha@.in", "asha@mail."]:
        assert errors_for("email", bad) == "email must look like name@example.com", f"{bad!r} is not a valid email."
    assert errors_for("email", "a@b.co") is None


def test_password_rules_in_order():
    assert errors_for("password", "short1") == "password must be at least 8 characters"
    assert errors_for("password", "longenough") == "password must contain a digit"
    got = errors_for("password", "xASHA_99x1")
    assert got == "password must not contain your username", (
        f"Got {got!r}. The username 'asha_99' appears in the password, ignoring case.")


def test_username_rule_skipped_when_username_invalid():
    got = validate_signup(with_(username="as", password="has2as"))
    assert got.get("password") == "password must be at least 8 characters"
    got = validate_signup(with_(username="as", password="xxasxx12"))
    assert "password" not in got, (
        "The 'contains your username' rule applies only when the username itself is valid.")
    got = validate_signup(with_(username="", password="anything12"))
    assert "password" not in got, "No username given: skip the username rule."


def test_no_broad_except():
    for node in ast.walk(TREE):
        if isinstance(node, ast.ExceptHandler):
            assert node.type is not None, "No bare `except:`. Validators raise ValueError: catch that."
            assert ast.unparse(node.type) not in ("Exception", "BaseException"), (
                "Catch ValueError only. A bug in a validator must not become a message for the user.")
