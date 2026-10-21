import math
from solution import permutations, anagrams
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


def test_three_in_order():
    assert permutations([1, 2, 3]) == [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]], (
        "Orderings starting with items[0] first, then items[1], ... recursively.")


def test_small():
    assert permutations([]) == [[]], "The empty list has exactly one ordering: [[]]."
    assert permutations(["x"]) == [["x"]]


def test_repeated_items_by_position():
    assert permutations([1, 1]) == [[1, 1], [1, 1]], "Items are distinct by position: [1, 1] has 2 orderings."


def test_count():
    for n in range(7):
        assert len(permutations(list(range(n)))) == math.factorial(n)


def test_input_unchanged():
    data = ["a", "b", "c"]
    permutations(data)
    assert data == ["a", "b", "c"], "Do not remove items from the caller's list; build `rest` with slicing."


def test_anagrams():
    assert anagrams("abc") == ["abc", "acb", "bac", "bca", "cab", "cba"]
    assert anagrams("aab") == ["aab", "aba", "baa"], "Remove duplicates and sort."
    assert anagrams("") == [""]
    assert anagrams("zz") == ["zz"]


def test_rules():
    assert calls_itself("permutations"), "permutations must be recursive."
    assert "itertools" not in SOURCE, "Do not use itertools for this exercise."
