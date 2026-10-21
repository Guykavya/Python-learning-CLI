import pytest
from solution import binary_search
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


DATA = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]


@pytest.mark.parametrize("i", range(len(DATA)))
def test_finds_every_item(i):
    assert binary_search(DATA, DATA[i]) == i, f"{DATA[i]} is at index {i} of the ORIGINAL list."


@pytest.mark.parametrize("target", [1, 7, 13, 60, 100])
def test_absent(target):
    assert binary_search(DATA, target) == -1


def test_small_lists():
    assert binary_search([], 1) == -1, "Empty list: lo >= hi at once, return -1."
    assert binary_search([4], 4) == 0
    assert binary_search([4], 5) == -1
    assert binary_search([1, 3], 3) == 1


def test_duplicates():
    items = [1, 2, 2, 2, 3]
    i = binary_search(items, 2)
    assert items[i] == 2


def test_large():
    items = list(range(0, 2_000_000, 2))
    assert binary_search(items, 1_999_998) == 999_999
    assert binary_search(items, 7) == -1


def test_rules():
    assert calls_itself("binary_search"), "binary_search must be recursive."
    assert not any(isinstance(n, ast.Slice) for n in ast.walk(TREE)), (
        "Do not slice the list; pass lo and hi to the recursive call.")
    assert not has_loop("binary_search"), "No loops: recursion only."
