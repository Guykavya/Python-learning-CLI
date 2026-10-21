from solution import validate_username

def expect_raise(exc_type, func, *args, match=None, why=""):
    """Call func(*args). It must raise exc_type, with match in its message if match is given."""
    try:
        result = func(*args)
    except exc_type as e:
        if match is not None:
            assert match in str(e), (
                f"The {exc_type.__name__} message should contain {match!r}, but it was {str(e)!r}. {why}")
        return e
    except Exception as e:
        raise AssertionError(
            f"Expected {exc_type.__name__}, but {type(e).__name__} was raised: {e}. {why}") from e
    raise AssertionError(f"Expected {exc_type.__name__}, but the call returned {result!r}. {why}")


def test_valid_names_returned():
    for name in ["asha_99", "Ravi", "abc", "a" * 15, "_hidden"]:
        assert validate_username(name) == name, f"{name!r} is valid: return it unchanged."


def test_wrong_type_is_type_error():
    why = "A value that is not a str is the wrong TYPE: raise TypeError, not ValueError."
    expect_raise(TypeError, validate_username, 42, match="username must be text (str), got int", why=why)
    expect_raise(TypeError, validate_username, None, match="got NoneType", why=why)


def test_length():
    why = "Check 3 <= len(name) <= 15 and put the actual length in the message."
    expect_raise(ValueError, validate_username, "ab", match="3 to 15 characters long, got 2", why=why)
    expect_raise(ValueError, validate_username, "a" * 16, match="got 16", why=why)
    expect_raise(ValueError, validate_username, "", match="got 0", why=why)


def test_bad_character_named():
    why = "Name the FIRST bad character, shown with repr (!r) so a space is visible."
    expect_raise(ValueError, validate_username, "ravi kumar", match="letters, digits and _, found ' '", why=why)
    expect_raise(ValueError, validate_username, "a-b!c", match="found '-'", why=why)


def test_leading_digit():
    expect_raise(ValueError, validate_username, "7up", match="must not start with a digit")


def test_rule_order():
    why = "Check the rules in the order of the table: type, length, characters, first digit."
    expect_raise(ValueError, validate_username, "7!", match="characters long", why=why)
    expect_raise(ValueError, validate_username, "7up!", match="found '!'", why=why)


def test_prints_nothing(capsys):
    try:
        validate_username("ab")
    except ValueError:
        pass
    assert capsys.readouterr().out == "", "Raise the exception; do not print anything."
