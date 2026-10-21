from solution import squares_of_evens, parse_positive
import ast
from pathlib import Path

SOURCE = Path(__file__).with_name("solution.py").read_text()
TREE = ast.parse(SOURCE)


def called_names():
    """Names of every plain function called in your code, e.g. {'print', 'len'}."""
    return {n.func.id for n in ast.walk(TREE) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def test_squares():
    assert squares_of_evens([1, 2, 3, 4, 5, 6]) == [4, 16, 36]
    assert squares_of_evens([-2, 7]) == [4], "-2 is even, and its square is 4."
    assert squares_of_evens([]) == []


def test_returns_list():
    assert isinstance(squares_of_evens([2]), list), "Wrap the result in list(...); map returns a lazy iterator."
    assert isinstance(parse_positive("1"), list)


def test_parse():
    assert parse_positive("4 -2 0 7") == [4, 7], "Convert with int first, then keep n > 0 (0 is not positive)."
    assert parse_positive("  10\t-1  3 ") == [10, 3]
    assert parse_positive("") == []


def test_uses_map_and_filter():
    for fname in ("squares_of_evens", "parse_positive"):
        func = next(n for n in TREE.body if isinstance(n, ast.FunctionDef) and n.name == fname)
        names = {c.func.id for c in ast.walk(func) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)}
        assert {"map", "filter"} <= names, f"{fname} must call both map and filter for this exercise."
