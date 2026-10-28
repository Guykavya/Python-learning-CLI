import pytest

from solution import fallback, parse_price


def test_parse_price_returns_a_number():
    result = parse_price("Rs 12.50")
    assert not callable(result), (
        "parse_price returned a function, not a price. `@fallback` without brackets passes parse_price "
        "in as `default`. A decorator factory must be called: @fallback(0.0)."
    )
    assert result == 12.5, "A good price must come back as a float. Does the wrapper RETURN func(...)?"
    assert parse_price(" 99 ") == 99.0, "Spaces around the number are fine."


def test_parse_price_bad_text():
    assert parse_price("free") == 0.0, "Bad text raises ValueError inside float(); the wrapper must return the default 0.0."


def test_metadata():
    assert parse_price.__name__ == "parse_price", "The report shows 'wrapper'. Add @functools.wraps(func) to the wrapper."
    assert parse_price.__doc__ == "Turn a price like 'Rs 12.50' into a float.", "wraps also keeps the docstring."


def test_result_is_returned():
    @fallback(-1)
    def to_int(text):
        return int(text)

    assert to_int("42") == 42, "The wrapper calls func but throws the result away. Write `return func(*args, **kwargs)`."
    assert to_int("x") == -1, "On ValueError, return the default."


def test_falsy_results_kept():
    @fallback(99)
    def zero():
        return 0

    assert zero() == 0, "A result of 0 is a real result. Return it; do not replace it with the default."


def test_other_errors_not_hidden():
    @fallback(0)
    def broken(x):
        return x["key"]

    with pytest.raises(KeyError):
        broken({})
