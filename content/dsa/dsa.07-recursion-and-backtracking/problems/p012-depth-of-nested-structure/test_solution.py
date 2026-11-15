import copy

import pytest

from solution import depth


@pytest.mark.parametrize("xs, want, why", [
    ([], 1, "the empty list is one level deep"),
    ([1, 2, 3], 1, "a flat list has depth 1"),
    ([[]], 2, "a list holding an empty list"),
    ([1, [2, [3]], 4], 3, "the example"),
    ([[], [[]]], 3, "the deepest child decides, not the first one"),
    ([[[[1]]], 2, [3]], 4, "the deepest list is the first item"),
    ([1, [2], [[3]], [[[4]]]], 4, "the deepest list is the last item"),
    ([[1], [2], [3]], 2, "several children at the same depth: take the max, do not add"),
    (["abc", ("x", ["y"])], 1, "strings and tuples are plain values, even if a tuple holds a list"),
])
def test_cases(xs, want, why):
    assert depth(xs) == want, f"depth({xs!r}) should be {want}: {why}."


def test_deep_100():
    xs = []
    for _ in range(99):
        xs = [xs]
    assert depth(xs) == 100, "A list nested 100 levels deep (the innermost one is empty)."


def test_not_changed():
    xs = [1, [2, [3]], []]
    before = copy.deepcopy(xs)
    depth(xs)
    assert xs == before, "depth must not change the list."
