from solution import parse_config


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


def yes_no(text):
    if text in ("yes", "no"):
        return text == "yes"
    raise ValueError("expected yes or no")


SCHEMA = {"volume": int, "difficulty": str, "fullscreen": yes_no}
GOOD = ["# game settings", "volume = 7", "difficulty = hard", "", "fullscreen = yes"]


def test_good_file():
    got = parse_config(GOOD, SCHEMA)
    assert got == {"volume": 7, "difficulty": "hard", "fullscreen": True}, f"Got {got}."


def test_spaces_and_equals_in_value():
    schema = {"title": str, "n": int}
    got = parse_config(["  title=a = b  ", "\tn=3"], schema)
    assert got == {"title": "a = b", "n": 3}, (
        f"Got {got}. Split at the FIRST '=' only (str.partition) and strip both sides.")


def test_missing_equals():
    expect_raise(ValueError, parse_config, ["volume = 7", "  difficulty hard "], SCHEMA,
                 match="line 2: expected 'key = value', got 'difficulty hard'",
                 why="Number lines from 1 and show the stripped line with !r.")


def test_line_numbers_count_blank_and_comment_lines():
    expect_raise(ValueError, parse_config, ["# c", "", "oops"], SCHEMA, match="line 3:",
                 why="Blank and comment lines still count when numbering.")


def test_unknown_key():
    expect_raise(ValueError, parse_config, ["colour = red"], SCHEMA,
                 match="line 1: unknown setting 'colour'; known settings: difficulty, fullscreen, volume",
                 why="List the schema keys sorted, joined with ', '.")


def test_duplicate_key():
    lines = ["volume = 7", "# again", "volume = 8"]
    expect_raise(ValueError, parse_config, lines, SCHEMA, match="line 3: 'volume' is set twice (first on line 1)")


def test_bad_value_chained():
    err = expect_raise(ValueError, parse_config, ["volume = loud"], SCHEMA,
                       match="line 1: bad value for 'volume': 'loud'")
    assert isinstance(err.__cause__, ValueError) and "loud" in str(err.__cause__), (
        f"__cause__ was {err.__cause__!r}. Raise the new error `from e`, where e is the converter's ValueError.")
    err = expect_raise(ValueError, parse_config, ["fullscreen = maybe"], SCHEMA,
                       match="line 1: bad value for 'fullscreen': 'maybe'")
    assert str(err.__cause__) == "expected yes or no", "The cause must be the converter's own exception."


def test_missing_settings():
    expect_raise(ValueError, parse_config, ["volume = 3"], SCHEMA,
                 match="missing settings: difficulty, fullscreen",
                 why="After all lines, report every schema key that never appeared, sorted.")
    expect_raise(ValueError, parse_config, [], SCHEMA, match="missing settings: difficulty, fullscreen, volume")


def test_first_problem_wins():
    expect_raise(ValueError, parse_config, ["bad line", "colour = red"], SCHEMA, match="line 1:",
                 why="Stop at the FIRST problem.")


def test_converter_bug_is_not_relabelled():
    def broken(text):
        return text.no_such_method()

    expect_raise(AttributeError, parse_config, ["x = 1"], {"x": broken},
                 why="Only a ValueError from the converter means a bad value. Other exceptions are bugs: "
                     "let them propagate.")
