import pytest
from solution import sum_digits
import ast
from pathlib import Path

SOURCE = Path(__file__).with_name("solution.py").read_text()
TREE = ast.parse(SOURCE)


def called_names():
    """Names of every plain function called in your code, e.g. {'print', 'len'}."""
    return {n.func.id for n in ast.walk(TREE) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def function_node(name):
    return next(n for n in ast.walk(TREE) if isinstance(n, ast.FunctionDef) and n.name == name)


def calls_itself(name):
    """True if the function with this name contains a call to itself."""
    fn = function_node(name)
    return any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == name
               for c in ast.walk(fn))


def has_loop(name):
    return any(isinstance(n, (ast.For, ast.While)) for n in ast.walk(function_node(name)))


@pytest.mark.parametrize("n, expected", [(4729, 22), (5, 5), (0, 0), (10, 1), (999, 27), (10**30, 1)])
def test_values(n, expected):
    assert sum_digits(n) == expected


@pytest.mark.parametrize("n, expected", [(-305, 8), (-7, 7), (-10, 1)])
def test_negative(n, expected):
    assert sum_digits(n) == expected, (
        f"sum_digits({n}) should be {expected}: ignore the sign. Turn n positive first, before the base case.")


def test_rules():
    assert calls_itself("sum_digits"), "sum_digits must call itself."
    assert "str" not in called_names(), "Use % 10 and // 10, not str()."
