import ast
from pathlib import Path

from solution import subsets

SOLUTION = Path(__file__).with_name("solution.py")


def norm(result):
    return sorted(sorted(s) for s in result)


def test_example():
    want = [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]
    got = subsets([1, 2, 3])
    assert all(isinstance(s, list) for s in got), "Every subset must be a list."
    assert [] in got and len(got) != 0, "The empty subset [] is part of the answer."
    assert norm(got) == want, (
        f"subsets([1, 2, 3]) should have the 8 subsets {want}; got {norm(got)}. "
        "If every subset is [], you appended the path itself instead of a copy (path[:]).")


def test_empty_input():
    assert subsets([]) == [[]], "The empty list has exactly one subset: [[]]."


def test_one_item():
    assert norm(subsets([7])) == [[], [7]], "One item: [] and [7]."


def test_count_and_unique():
    nums = list(range(10))
    got = subsets(nums)
    assert len(got) == 2 ** 10, f"10 items have 2^10 = 1024 subsets, got {len(got)}."
    assert len({tuple(sorted(s)) for s in got}) == 1024, "Some subsets appear twice. Recurse with i + 1, not start + 1."


def test_strings_and_order_inside():
    got = norm(subsets(["b", "a"]))
    assert got == [[], ["a"], ["a", "b"], ["b"]], "Items can be any values, not only numbers."


def test_no_itertools():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mods = [a.name for a in node.names] + [getattr(node, "module", None) or ""]
            assert "itertools" not in mods, "itertools is not allowed here: write the backtracking yourself."
