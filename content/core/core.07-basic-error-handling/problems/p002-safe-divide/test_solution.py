import ast
from pathlib import Path

from solution import safe_divide

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


def test_normal_division():
    assert safe_divide(6, 3) == 2.0, "6 / 3 is 2.0. Use true division /."
    assert safe_divide(0, 5) == 0.0, "0 / 5 is 0.0: a zero numerator is fine."
    assert safe_divide(7, 2) == 3.5, "Use /, not //."


def test_zero_divisor():
    assert safe_divide(1, 0) is None, "Dividing by 0 raises ZeroDivisionError: catch it and return None."
    assert safe_divide(-3, 0.0) is None, "0.0 is zero too; the same exception is raised."


def test_type_error_propagates():
    expect_raise(TypeError, safe_divide, "6", 2,
                 why="'6' / 2 is a bug in the caller. Catch ZeroDivisionError only.")


def test_uses_try_with_zero_division_error():
    handlers = [n for n in ast.walk(TREE) if isinstance(n, ast.ExceptHandler)]
    assert handlers, "Use try/except around the division (EAFP), not an if test on b."
    for h in handlers:
        assert h.type is not None, "Do not use a bare `except:`. Name ZeroDivisionError."
        assert "ZeroDivisionError" in ast.unparse(h.type) or "ArithmeticError" in ast.unparse(h.type), (
            "Catch ZeroDivisionError, the exception that division by zero raises.")
