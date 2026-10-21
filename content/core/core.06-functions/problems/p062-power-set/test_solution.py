import pytest
from solution import subsets
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


def canon(result):
    return sorted(tuple(s) for s in result)


def test_empty():
    assert subsets([]) == [[]], "The empty list has one subset, the empty list: return [[]], not []."


def test_one():
    assert canon(subsets(["a"])) == [(), ("a",)]


def test_three():
    got = subsets(["a", "b", "c"])
    assert len(got) == 8, f"3 items have 2**3 = 8 subsets; got {len(got)}."
    assert canon(got) == canon([[], ["a"], ["b"], ["c"], ["a", "b"], ["a", "c"], ["b", "c"], ["a", "b", "c"]]), (
        "Each subset keeps the items in their original order, e.g. ['a', 'c'], not ['c', 'a'].")


def test_subsets_are_separate_lists():
    got = subsets([1, 2])
    assert all(isinstance(s, list) for s in got), "Each subset should be a list."
    got[0].append("X")
    assert canon(subsets([1, 2])) == [(), (1,), (1, 2), (2,)]


def test_max_size():
    assert canon(subsets([1, 2, 3], max_size=1)) == [(), (1,), (2,), (3,)]
    assert canon(subsets([1, 2, 3], max_size=0)) == [()], "max_size=0: only the empty subset."
    assert len(subsets(list(range(6)), max_size=2)) == 1 + 6 + 15


def test_bigger():
    got = subsets(list(range(12)))
    assert len(got) == 4096 and len(set(map(tuple, got))) == 4096, "No duplicates, no missing subsets."


def test_input_unchanged():
    data = [1, 2, 3]
    subsets(data)
    assert data == [1, 2, 3]


def test_rules():
    assert calls_itself("subsets"), "subsets must be recursive."
    assert "itertools" not in SOURCE, "Do not use itertools for this exercise."


def test_max_size_keyword_only():
    with pytest.raises(TypeError):
        subsets([1], 1)
