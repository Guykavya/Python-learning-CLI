import pytest
from solution import factorial
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


@pytest.mark.parametrize("n, expected", [(0, 1), (1, 1), (2, 2), (5, 120), (10, 3628800), (20, 2432902008176640000)])
def test_values(n, expected):
    assert factorial(n) == expected, (
        f"factorial({n}) should be {expected}. Base case: factorial(0) == 1.")


def test_is_recursive():
    assert calls_itself("factorial"), "factorial must call itself."
    assert not has_loop("factorial"), "Solve this one with recursion only, no for or while loop."
