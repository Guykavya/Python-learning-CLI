import ast
from pathlib import Path

import solution
from solution import add_lists, count_equal_positions, has_negative, indexed_lines

TREE = ast.parse(Path(solution.__file__).read_text())


def _func(name):
    for node in ast.walk(TREE):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"function {name} is missing")


def test_indexed_lines():
    assert indexed_lines(["a", "b", "c"]) == ["1: a", "2: b", "3: c"], (
        "Numbering starts at 1 and the format is 'N: text'. enumerate(lines, start=1) does it."
    )
    assert indexed_lines([]) == [], "An empty list gives an empty list."


def test_add_lists():
    assert add_lists([1, 2, 3], [10, 20, 30]) == [11, 22, 33], "Add position by position."
    assert add_lists([1, 2, 3], [10]) == [11], "Stop at the shorter list (b is shorter here); zip does this."
    assert add_lists([1], [10, 20, 30]) == [11], "Stop at the shorter list (a is shorter here)."
    assert add_lists([], [1]) == [], "Empty input gives an empty list."


def test_has_negative():
    assert has_negative([3, -1, 4]) is True, "One negative number is enough."
    assert has_negative([0, 1, 2]) is False, "0 is not negative."
    assert has_negative([]) is False, "No numbers means no negative (any([]) is False)."


def test_count_equal_positions():
    assert count_equal_positions([1, 2, 3, 4], [1, 0, 3, 0]) == 2, "Count positions where both values are equal."
    assert count_equal_positions([1, 2, 3], [1]) == 1, "Only the shorter length is compared."
    assert count_equal_positions([], []) == 0, "Empty gives 0."
    assert count_equal_positions("abc", "abd") == 2, "Strings are iterables too: zip works on any iterables."


def test_returns_real_types():
    assert isinstance(count_equal_positions([1], [1]), int), "sum() of booleans is an int; return a number."


def test_no_range_len():
    for node in ast.walk(TREE):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "range"
                and any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "len"
                        for arg in node.args for n in ast.walk(arg))):
            raise AssertionError(
                "range(len(...)) found. Loop over the items (for x in items), or use enumerate() for "
                "the position and zip() for two lists at once."
            )


def test_flag_and_counter_loops_are_gone():
    for name in ("has_negative", "count_equal_positions"):
        loops = [n for n in ast.walk(_func(name)) if isinstance(n, (ast.For, ast.While))]
        assert not loops, (
            f"{name} still has a for/while statement. Use any()/all() for yes-no questions "
            "and sum() for counting, with a generator expression inside."
        )


def test_enumerate_and_zip_are_used():
    names = {n.id for n in ast.walk(TREE) if isinstance(n, ast.Name)}
    assert "enumerate" in names, "indexed_lines should use enumerate(lines, start=1)."
    assert "zip" in names, "add_lists / count_equal_positions should use zip(a, b)."
