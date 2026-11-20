import ast
import pathlib
import random

import pytest

from solution import k_largest

SOLUTION = pathlib.Path(__file__).with_name("solution.py")


def test_no_sorting_and_no_nlargest():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    bad = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in ("sorted", "nlargest", "nsmallest"):
            bad.add(node.id)
        if isinstance(node, ast.Attribute) and node.attr in ("sort", "nlargest", "nsmallest"):
            bad.add("." + node.attr)
        if isinstance(node, ast.ImportFrom) and node.module == "heapq":
            for alias in node.names:
                if alias.name in ("nlargest", "nsmallest"):
                    bad.add(alias.name)
    assert not bad, (
        f"This drill is about the size-k heap itself: found {sorted(bad)} in your code. "
        "Keep a min-heap of size k, then pop the k items (smallest first) and reverse the list; "
        "sorted(), .sort(), nlargest and nsmallest are not allowed here.")


class Counted:
    """A number that counts every comparison made with it (any of < <= > >=)."""
    comparisons = 0

    def __init__(self, v):
        self.v = v

    def __lt__(self, other):
        Counted.comparisons += 1
        return self.v < other.v

    def __le__(self, other):
        Counted.comparisons += 1
        return self.v <= other.v

    def __gt__(self, other):
        Counted.comparisons += 1
        return self.v > other.v

    def __ge__(self, other):
        Counted.comparisons += 1
        return self.v >= other.v


def test_the_examples():
    assert k_largest([3, 1, 5, 12, 2, 11, 7], 3) == [12, 11, 7], "The 3 largest of [3, 1, 5, 12, 2, 11, 7] are 12, 11, 7, largest first."
    assert k_largest([4, 4, 4], 2) == [4, 4], "Equal items are all kept: two of the three 4s."
    assert k_largest([1, 2], 5) == [2, 1], "k larger than n: return all items, largest first."
    assert k_largest([1, 2], 0) == [], "k = 0: return an empty list (do not look at heap[0] of an empty heap)."


def test_the_order_is_largest_first():
    got = k_largest([5, 1, 9, 3, 7], 3)
    assert got == [9, 7, 5], f"Expected [9, 7, 5] (largest first), got {got}. The heap pops the smallest first: reverse them."


def test_edge_cases():
    assert k_largest([], 3) == [], "An empty input gives an empty list."
    assert k_largest([], 0) == [], "An empty input with k = 0 gives an empty list."
    assert k_largest([8], 1) == [8], "One item, k = 1."
    assert k_largest([8], 4) == [8], "One item, k = 4: just that item."
    assert k_largest([1, 2, 3], -1) == [], "A negative k is treated like 0."
    assert k_largest([2, 2, 2, 2], 4) == [2, 2, 2, 2], "k = n with equal items."


def test_k_equals_n_and_k_equals_one():
    assert k_largest([3, 1, 2], 3) == [3, 2, 1], "k = n: all items, largest first."
    assert k_largest([3, 1, 2, 9, -4], 1) == [9], "k = 1: only the maximum."
    assert k_largest([-5, -2, -9], 2) == [-2, -5], "Negative numbers: the largest are the ones closest to zero."


def test_the_input_is_not_changed_and_any_iterable_works():
    data = [5, 1, 9, 3, 7, 3]
    copy = list(data)
    k_largest(data, 3)
    assert data == copy, "The list you receive must stay as it was: do not heapify it or sort it."
    assert k_largest(tuple(data), 2) == [9, 7], "A tuple must work."
    assert k_largest((x for x in data), 2) == [9, 7], "A generator must work: read the input once, with a for loop, without len() or indexing."


def test_random_inputs_against_sorted():
    rng = random.Random(15)
    for _ in range(500):
        data = [rng.randint(-20, 20) for _ in range(rng.randint(0, 25))]
        k = rng.randint(-1, 30)
        want = sorted(data, reverse=True)[:max(k, 0)]
        got = k_largest(data, k)
        assert got == want, f"k_largest({data}, {k}) should be {want}, got {got}."


@pytest.mark.parametrize("k", [10, 100])
def test_comparisons_stay_small(k):
    n = 20_000
    rng = random.Random(16)
    values = rng.sample(range(10 ** 7), n)
    items = [Counted(v) for v in values]
    Counted.comparisons = 0
    got = k_largest(items, k)
    used = Counted.comparisons
    assert [c.v for c in got] == sorted(values, reverse=True)[:k], f"k = {k}: the {k} largest are wrong or not largest first."
    assert used <= 4 * n, (
        f"With n = {n} and k = {k} you used {used} comparisons; a size-k heap needs about {n + 50 * k}. "
        "Do you push every item and then pop (about 7 comparisons per item), or sort? "
        "Compare each item with heap[0] first (or use heappushpop/heapreplace): most items are weaker than the root and cost one comparison.")


def test_a_hundred_thousand_items():
    rng = random.Random(17)
    data = [rng.randint(-10 ** 9, 10 ** 9) for _ in range(100_000)]
    got = k_largest(data, 50)
    assert got == sorted(data, reverse=True)[:50], "The 50 largest of 100,000 random numbers are wrong."
