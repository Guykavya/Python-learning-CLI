from solution import product
import ast
from pathlib import Path

SOURCE = Path(__file__).with_name("solution.py").read_text()
TREE = ast.parse(SOURCE)


def called_names():
    """Names of every plain function called in your code, e.g. {'print', 'len'}."""
    return {n.func.id for n in ast.walk(TREE) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def test_values():
    assert product([3, 5, 2, 4]) == 120
    assert product([7]) == 7
    assert product([2, -3]) == -6


def test_empty():
    assert product([]) == 1, "Give reduce the initial value 1, so an empty list gives 1 instead of an error."


def test_zero():
    assert product([5, 0, 9]) == 0


def test_uses_reduce():
    names = called_names() | {n.func.attr for n in ast.walk(TREE)
                              if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert "reduce" in names, "Use functools.reduce for this exercise."
