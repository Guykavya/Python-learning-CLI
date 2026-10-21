import ast
from pathlib import Path

import pytest

from solution import error_family as _error_family


def error_family(func, *args):
    """Call the solution; turn an escaping exception into a clear test failure."""
    try:
        return _error_family(func, *args)
    except (LookupError, ArithmeticError, ValueError, TypeError) as e:
        raise AssertionError(
            f"error_family let {type(e).__name__} escape, but it belongs to one of the four families "
            f"({type(e).__mro__[1].__name__} is its parent). Catch the PARENT classes from chapter section 4.") from e

TREE = ast.parse(Path(__file__).with_name("solution.py").read_text())


def test_ok():
    assert error_family(len, "abc") == "ok", "No exception was raised: return 'ok'."
    assert error_family(abs, -3) == "ok", "abs(-3) works: return 'ok'."


def test_lookup_family():
    assert error_family(lambda: {}["x"]) == "lookup", "KeyError is a LookupError."
    assert error_family(lambda: [1][3]) == "lookup", (
        "IndexError is a LookupError too. Catch the parent class LookupError, not just KeyError.")
    assert error_family(lambda: "abc"[10]) == "lookup"


def test_arithmetic_family():
    assert error_family(lambda: 1 / 0) == "arithmetic", "ZeroDivisionError is an ArithmeticError."
    assert error_family(lambda: 2.0 ** 10000) == "arithmetic", (
        "OverflowError is also an ArithmeticError. Catch the parent class, not only ZeroDivisionError.")


def test_value_family():
    assert error_family(int, "x") == "value", "int('x') raises ValueError."
    assert error_family(lambda: b"\xff".decode("utf-8")) == "value", (
        "UnicodeDecodeError is a subclass of ValueError, so it belongs to the 'value' family.")
    assert error_family(lambda: [3, 1].index(2)) == "value", "list.index raises ValueError, not IndexError."


def test_type_family():
    assert error_family(len, 5) == "type", "len(5) raises TypeError."
    assert error_family(lambda: "a" + 1) == "type"


def test_passes_arguments_through():
    assert error_family(int, "12") == "ok", "Call func(*args): pass the arguments on."
    assert error_family(divmod, 7, 0) == "arithmetic", "Pass every argument: divmod(7, 0)."


def test_other_errors_propagate():
    with pytest.raises(NameError):
        error_family(lambda: missing_name)  # noqa: F821

    def interrupted():
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        error_family(interrupted)


def test_no_broad_except():
    for node in ast.walk(TREE):
        if isinstance(node, ast.ExceptHandler):
            assert node.type is not None, "No bare `except:`. NameError and KeyboardInterrupt must propagate."
            assert ast.unparse(node.type) not in ("Exception", "BaseException"), (
                "Do not catch Exception: NameError must propagate. Catch the four parent classes.")
