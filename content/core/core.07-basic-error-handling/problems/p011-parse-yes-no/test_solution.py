from solution import parse_yes_no

MESSAGE = "answer must be yes or no (also y/n, true/false, 1/0), got "

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


def test_yes_words():
    for text in ["yes", "Yes", "Y", "true", "TRUE", "1", "  yes  "]:
        assert parse_yes_no(text) is True, f"{text!r} means yes: return True (the bool, not a string)."


def test_no_words():
    for text in ["no", "N", "False", "0", "\tno\n"]:
        assert parse_yes_no(text) is False, f"{text!r} means no: return False."


def test_other_text_raises_value_error():
    expect_raise(ValueError, parse_yes_no, "maybe", match=MESSAGE + "'maybe'",
                 why="Unknown answers must raise ValueError with the exact message.")


def test_message_shows_original_text():
    why = "Show the ORIGINAL text with repr (!r), not the cleaned word."
    expect_raise(ValueError, parse_yes_no, " Maybe ", match=MESSAGE + "' Maybe '", why=why)
    expect_raise(ValueError, parse_yes_no, "", match=MESSAGE + "''", why=why)


def test_not_a_string():
    why = "Check isinstance(text, str) first and raise TypeError."
    expect_raise(TypeError, parse_yes_no, None, match="answer must be text (str), got NoneType", why=why)
    expect_raise(TypeError, parse_yes_no, 1, match="got int", why=why)


def test_does_not_return_none_for_unknown():
    try:
        result = parse_yes_no("perhaps")
    except ValueError:
        return
    raise AssertionError(f"Returned {result!r} for 'perhaps'. Raise ValueError instead of returning.")
