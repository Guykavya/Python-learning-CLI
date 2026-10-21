import ast
from pathlib import Path

from solution import ratio

TREE = ast.parse(Path(__file__).with_name("solution.py").read_text())
NUMBERS = "Both values must be numbers, like 3 or 2.5."
ZERO = "The second value must not be zero."

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


def test_results():
    assert ratio("7", "2") == "3.50", "Format with two decimals: f'{value:.2f}'."
    assert ratio("1", "3") == "0.33"
    assert ratio("-9", " 4.5 ") == "-2.00", "float() accepts signs and surrounding spaces."


def test_not_numbers():
    assert ratio("seven", "2") == NUMBERS, "float('seven') raises ValueError: return the numbers message."
    assert ratio("4", "") == NUMBERS, "An empty box is not a number either."
    assert ratio("abc", "0") == NUMBERS, (
        "When the first value is not a number, that is the problem to report, even if the second is zero.")


def test_zero_divisor():
    assert ratio("4", "0") == ZERO, "Dividing by zero raises ZeroDivisionError: return the zero message."
    assert ratio("4", "0.0") == ZERO
    assert ratio("0", "0") == ZERO


def test_type_error_propagates():
    expect_raise(TypeError, ratio, None, "2",
                 why="float(None) is the caller's bug. Catch ValueError and ZeroDivisionError only.")


def test_two_specific_handlers():
    handlers = [n for n in ast.walk(TREE) if isinstance(n, ast.ExceptHandler)]
    names = [ast.unparse(h.type) if h.type is not None else "bare" for h in handlers]
    assert "bare" not in names and "Exception" not in names, "Catch the two specific types, nothing broader."
    assert len(handlers) >= 2, "Use two except clauses, one for ValueError and one for ZeroDivisionError."
