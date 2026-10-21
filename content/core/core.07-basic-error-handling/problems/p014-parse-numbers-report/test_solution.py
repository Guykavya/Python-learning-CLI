from solution import parse_numbers


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


def test_example():
    numbers, errors = parse_numbers(["3.5", "abc", " 7 ", "", "nan", "-2"])
    assert numbers == [3.5, 7.0, -2.0], f"Got numbers {numbers}. Keep every finite number, in order."
    assert errors == [
        "item 2: 'abc' is not a number",
        "item 4: '' is not a number",
        "item 5: 'nan' is not a finite number",
    ], f"Got errors {errors}. Count positions from 1 (enumerate(items, start=1)) and show items with !r."


def test_all_good():
    assert parse_numbers(["1", "2.5", "1e3"]) == ([1.0, 2.5, 1000.0], []), "No bad items: errors is empty."


def test_empty():
    assert parse_numbers([]) == ([], []), "Return ([], []) for no items."


def test_infinity():
    numbers, errors = parse_numbers(["inf", "-Infinity", "5"])
    assert numbers == [5.0], "Infinite values are not kept."
    assert errors == ["item 1: 'inf' is not a finite number", "item 2: '-Infinity' is not a finite number"], (
        f"Got {errors}. float('inf') succeeds; use math.isfinite to reject it with the 'finite' message.")


def test_one_bad_item_does_not_stop_the_rest():
    numbers, errors = parse_numbers(["x", "y", "4"])
    assert numbers == [4.0], "Put the try INSIDE the loop so later items are still processed."
    assert len(errors) == 2


def test_type_error_propagates():
    expect_raise(TypeError, parse_numbers, ["1", None],
                 why="float(None) is a bug in the caller: catch ValueError only.")


def test_returns_tuple():
    result = parse_numbers(["1"])
    assert isinstance(result, tuple) and len(result) == 2, "Return a tuple (numbers, errors)."
