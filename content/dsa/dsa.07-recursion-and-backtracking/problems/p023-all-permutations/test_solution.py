import ast
import itertools
from pathlib import Path

import pytest

from solution import permute

SOLUTION = Path(__file__).with_name("solution.py")


def test_empty():
    assert permute([]) == [[]], "There is exactly one ordering of nothing: return [[]]."


def test_one():
    assert permute([5]) == [[5]], "One item has one ordering."


def test_example():
    want = [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]
    got = permute([1, 2, 3])
    assert sorted(got) == want, (
        f"permute([1, 2, 3]) should have the 6 orderings {want}; got {sorted(got)}. "
        "If items are missing, check that you reset used[i] = False after the call.")


@pytest.mark.parametrize("n, count", [(4, 24), (5, 120), (7, 5040)])
def test_counts(n, count):
    nums = list(range(10, 10 + n))
    got = permute(nums)
    assert len(got) == count, f"{n} items have {n}! = {count} orderings, got {len(got)}."
    assert sorted(got) == sorted(list(p) for p in itertools.permutations(nums)), \
        "Some orderings are wrong, missing or repeated."


def test_input_unchanged():
    nums = [3, 1, 2]
    permute(nums)
    assert nums == [3, 1, 2], "permute must not change its input list."


def test_no_itertools():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mods = [a.name for a in node.names] + [getattr(node, "module", None) or ""]
            assert "itertools" not in mods, "itertools is not allowed here: write the backtracking yourself."
