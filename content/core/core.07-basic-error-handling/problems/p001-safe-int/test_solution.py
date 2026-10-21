import ast
from pathlib import Path

from solution import to_int

TREE = ast.parse(Path(__file__).with_name("solution.py").read_text())

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


def test_valid_numbers():
    assert to_int("42") == 42, "to_int('42') should be 42."
    assert to_int("  -7 ") == -7, "int() accepts a sign and surrounding spaces; just call int(text)."
    assert to_int("0") == 0


def test_invalid_text_gives_default():
    assert to_int("abc") == 0, "For text that is not a number, catch ValueError and return default."
    assert to_int("") == 0, "An empty string also raises ValueError: return default."
    assert to_int("3.5") == 0, "'3.5' is not a whole number, so int('3.5') raises ValueError: return default."


def test_custom_default():
    assert to_int("abc", None) is None, "Return the default the caller passed, not a fixed 0."
    assert to_int("x", default=-1) == -1


def test_type_error_is_not_caught():
    why = ("int(None) raises TypeError: a bug in the caller. Catch ValueError only, "
           "not a bare except or Exception.")
    expect_raise(TypeError, to_int, None, why=why)
    expect_raise(TypeError, to_int, [1, 2], why=why)


def test_no_broad_except():
    for node in ast.walk(TREE):
        if isinstance(node, ast.ExceptHandler):
            assert node.type is not None, "Do not use a bare `except:`. Catch ValueError only."
            assert ast.unparse(node.type) not in ("Exception", "BaseException"), (
                "Catch ValueError only. `except Exception` would also hide the TypeError bug.")
