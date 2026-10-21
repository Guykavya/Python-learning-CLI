from solution import parse_date


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


SHAPE = "date must look like YYYY-MM-DD, for example 2025-03-14, got "
DIGITS = "date must use digits only, like 2025-03-14, got "


def test_valid_dates():
    assert parse_date("2025-03-14") == (2025, 3, 14), "Return a tuple of three ints."
    assert parse_date(" 2024-02-29 ") == (2024, 2, 29), "Strip spaces first; 2024 is a leap year."
    assert parse_date("2000-02-29") == (2000, 2, 29), "2000 is divisible by 400, so it is a leap year."
    assert parse_date("1999-12-31") == (1999, 12, 31)


def test_bad_shape():
    for text in ["14/03/2025", "2025-3-14", "2025-03", "", "2025-03-14-01", "25-03-14"]:
        expect_raise(ValueError, parse_date, text, match=SHAPE + repr(text),
                     why="Check: 3 parts with lengths 4, 2, 2. Show the original text with !r.")


def test_bad_digits_and_from_none():
    err = expect_raise(ValueError, parse_date, "2025-O3-14", match=DIGITS + "'2025-O3-14'",
                       why="Catch the ValueError from int() and raise the clear message instead.")
    assert err.__cause__ is None and err.__suppress_context__, (
        "Raise the digits error `from None`, so the int() error is not printed before your message.")
    expect_raise(ValueError, parse_date, "abcd-01-01", match=DIGITS)


def test_month_range():
    expect_raise(ValueError, parse_date, "2025-13-01", match="month must be from 1 to 12, got 13")
    expect_raise(ValueError, parse_date, "2025-00-10", match="month must be from 1 to 12, got 0")


def test_day_range():
    expect_raise(ValueError, parse_date, "2023-02-29", match="day must be from 1 to 28 for 2023-02, got 29",
                 why="2023 is not a leap year.")
    expect_raise(ValueError, parse_date, "1900-02-29", match="from 1 to 28 for 1900-02",
                 why="1900 is a century year not divisible by 400: not a leap year.")
    expect_raise(ValueError, parse_date, "2025-04-31", match="day must be from 1 to 30 for 2025-04, got 31")
    expect_raise(ValueError, parse_date, "2025-01-00", match="got 0")


def test_month_checked_before_day():
    expect_raise(ValueError, parse_date, "2025-13-45", match="month",
                 why="Check the month before the day: the day's limit depends on the month.")
