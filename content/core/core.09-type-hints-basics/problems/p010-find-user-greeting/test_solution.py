from typing import get_type_hints

from solution import find_user, greeting, shout_name

USERS = {"u1": "Asha", "u2": "Ravi", "u3": ""}


def test_hints():
    users_hint = dict[str, str]
    assert get_type_hints(find_user) == {"users": users_hint, "user_id": str, "return": str | None}, (
        "find_user returns the name or None: -> str | None."
    )
    assert get_type_hints(greeting) == {"users": users_hint, "user_id": str, "return": str}, (
        "greeting always returns text (guest when missing): -> str."
    )
    assert get_type_hints(shout_name) == {"users": users_hint, "user_id": str, "return": str | None}, (
        "shout_name returns None for a missing user: -> str | None."
    )


def test_find_user():
    assert find_user(USERS, "u1") == "Asha", "Return the name stored under the id."
    assert find_user(USERS, "u9") is None, "A missing id gives None, not KeyError."


def test_empty_name_is_still_a_name():
    assert find_user(USERS, "u3") == "", "An empty name is a real value, not 'missing'."


def test_greeting():
    assert greeting(USERS, "u2") == "Hello, Ravi!", "Greet known users by name."
    assert greeting(USERS, "u9") == "Hello, guest!", "Greet unknown users as guest."


def test_greeting_empty_name():
    assert greeting(USERS, "u3") == "Hello, !", (
        "u3 exists with an empty name. Check 'name is None', not 'if not name'."
    )


def test_shout_name():
    assert shout_name(USERS, "u1") == "ASHA", "Return the name in upper case."
    assert shout_name(USERS, "u9") is None, "A missing user gives None."
    assert shout_name(USERS, "u3") == "", "The empty name shouts as the empty string, not None."
