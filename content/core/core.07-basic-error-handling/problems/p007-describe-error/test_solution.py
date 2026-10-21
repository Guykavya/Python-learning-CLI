from solution import describe_error


def caught(func):
    """Run func and return the exception it raises."""
    try:
        func()
    except Exception as e:
        return e
    raise AssertionError("test setup: func did not raise")


def test_simple_message():
    got = describe_error(ValueError("age must be positive"))
    assert got == "ValueError: age must be positive", (
        f"Got {got!r}. Start with type(err).__name__, then ': ', then the message.")


def test_no_arguments():
    got = describe_error(ValueError())
    assert got == "ValueError", f"Got {got!r}. With no args, return just the type name, no colon."
    assert describe_error(ZeroDivisionError()) == "ZeroDivisionError"


def test_key_error_without_quotes():
    got = describe_error(KeyError("cake"))
    assert got == "KeyError: missing key cake", (
        f"Got {got!r}. str(KeyError('cake')) is \"'cake'\" WITH quotes; use err.args[0] for the key itself.")
    assert describe_error(KeyError(42)) == "KeyError: missing key 42", "Convert the key with str()."


def test_several_arguments():
    got = describe_error(ValueError("bad row", 3))
    assert got == "ValueError: bad row, 3", f"Got {got!r}. Join str() of every arg with ', '."


def test_real_caught_exceptions():
    assert describe_error(caught(lambda: 1 / 0)) == "ZeroDivisionError: division by zero"
    assert describe_error(caught(lambda: {}["x"])) == "KeyError: missing key x"
    assert describe_error(caught(lambda: [][0])) == "IndexError: list index out of range"


def test_type_name_not_repr():
    got = describe_error(TypeError("bad"))
    assert not got.startswith("<class"), "Use type(err).__name__, not str(type(err))."
