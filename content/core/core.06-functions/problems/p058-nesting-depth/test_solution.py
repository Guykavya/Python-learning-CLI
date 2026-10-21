import pytest
from solution import depth
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


@pytest.mark.parametrize("data, expected", [
    (5, 0), ("abc", 0), (None, 0), ([], 1), ((), 1), ([1, 2, 3], 1), ([1, [2, [3]], 4], 3),
    ([[], [[]]], 3), ((1, [2, (3, [])]), 4), ([[1], [[2]], [3]], 3), (["abc", ["de"]], 2),
])
def test_depth(data, expected):
    assert depth(data) == expected, (
        f"depth({data!r}) should be {expected}: 1 + the DEEPEST item; an empty container is 1; "
        "non-containers (including strings) are 0.")


def test_deep_chain():
    data = []
    for _ in range(200):
        data = [data]
    assert depth(data) == 201


def test_is_recursive():
    assert calls_itself("depth")
