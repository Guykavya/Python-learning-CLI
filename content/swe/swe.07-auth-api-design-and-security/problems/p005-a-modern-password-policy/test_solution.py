import pytest

from solution import check_password_policy

BAD = frozenset({"password1234", "qwertyuiop12", "iloveyou2024"})


def test_good_passphrase_is_accepted():
    assert check_password_policy("correct horse battery staple", "ada") == [], \
        "A long passphrase with spaces must pass: spaces are allowed and no composition rules apply."


@pytest.mark.parametrize("pw", ["abcdefghijkl", "ABCDEFGHIJKL", "123456789012", "lowercase only words", "пароль-длинный-очень"])
def test_no_composition_rules(pw):
    assert check_password_policy(pw) == [], f"{pw!r} is long enough and not bad: do not demand capitals, digits or symbols (chapter 2.4)."


def test_length_boundaries():
    assert check_password_policy("abcdefghijk") == ["too_short"], "11 characters are too short."
    assert check_password_policy("abcdefghijkl") == [], "12 characters are enough: the minimum is 12, so use < 12 for 'too short'."
    assert check_password_policy("ab" * 128) == [], "256 characters are allowed."
    assert check_password_policy("ab" * 128 + "c") == ["too_long"], "257 characters are too long (the maximum is 256)."


def test_empty_password():
    assert check_password_policy("") == ["too_short"], "The empty password is only 'too_short' (it has no repeated character, so no 'one_character')."


def test_length_counts_characters_not_bytes():
    assert check_password_policy("é" * 6 + "abcde") == ["too_short"], "11 characters, even though more bytes: count characters with len(password)."


def test_breached_list_is_case_insensitive():
    assert check_password_policy("password1234", breached=BAD) == ["breached"], "A password in the breached set must be 'breached'."
    assert check_password_policy("PassWord1234", breached=BAD) == ["breached"], "The set holds lower-case passwords: compare password.lower()."
    assert check_password_policy("password12345", breached=BAD) == [], "Only exact matches are breached; a longer different password is fine."


def test_breached_default_is_empty():
    assert check_password_policy("password1234") == [], "With no breached set given nothing is breached."


def test_username_inside_password():
    assert check_password_policy("ada-lovelace-rules", "ada") == ["contains_username"], "The username inside the password is a problem."
    assert check_password_policy("ILOVE-ADA-so-much", "ada") == ["contains_username"], "Ignore case when looking for the username."


def test_empty_username_is_ignored():
    assert check_password_policy("correct horse battery staple", "") == [], \
        "An empty username must not count: '' in any string is True in Python, so test `if username and ...`."


def test_one_character_repeated():
    assert check_password_policy("aaaaaaaaaaaa") == ["one_character"], "A single repeated character is rejected."
    assert check_password_policy("aaaaaaaaaaab") == [], "Not every character is the same here: accepted."


def test_several_problems_in_order():
    assert check_password_policy("aaa") == ["too_short", "one_character"], "Report every failing rule, in the table's order."
    both = check_password_policy("adaadaadaada", "ada", breached=frozenset({"adaadaadaada"}))
    assert both == ["breached", "contains_username"], f"Order is too_short, too_long, breached, contains_username, one_character; got {both}"
    assert check_password_policy("a" * 300) == ["too_long", "one_character"], "300 repeated characters: too_long first, then one_character."


def test_returns_a_list():
    assert isinstance(check_password_policy("correct horse battery staple"), list), "Return a list (an empty list means accepted)."
