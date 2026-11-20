import ast
import math
import pathlib
import random

import pytest

from solution import heap_sort

SOLUTION = pathlib.Path(__file__).with_name("solution.py")


def test_no_library_heap_or_sort():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    bad = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in ("sorted", "heapq"):
            bad.add(node.id)
        if isinstance(node, ast.Attribute) and node.attr == "sort":
            bad.add(".sort")
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [alias.name for alias in node.names] + [getattr(node, "module", None) or ""]
            if any(name.split(".")[0] == "heapq" for name in names):
                bad.add("heapq")
    assert not bad, (
        f"This problem is about writing the heap sort yourself: found {sorted(bad)} in your code. "
        "Use sift_down loops by hand; heapq, sorted() and .sort() are not allowed here.")


class Counted:
    """A number that counts every comparison made with it."""
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


def test_the_example_both_ways():
    a = [4, 10, 3, 5, 1]
    heap_sort(a)
    assert a == [1, 3, 4, 5, 10], f"Ascending: expected [1, 3, 4, 5, 10], got {a}. The list you pass in must be sorted after the call (in place)."
    heap_sort(a, reverse=True)
    assert a == [10, 5, 4, 3, 1], f"reverse=True: expected [10, 5, 4, 3, 1], got {a}. For the descending order use a min-heap (or flip the comparison)."


@pytest.mark.parametrize("data", [[], [7], [2, 1], [1, 2], [3, 3], [2, 1, 3], [5, 4, 3, 2, 1], [1, 2, 3, 4, 5], [4, 4, 4, 4], [2, 1, 2, 1, 2, 1]])
def test_small_cases(data):
    a = list(data)
    heap_sort(a)
    assert a == sorted(data), f"heap_sort({data}) should leave {sorted(data)}, got {a}. Check the last rounds of phase 2 (end = 1) and the root of phase 1."
    b = list(data)
    heap_sort(b, reverse=True)
    assert b == sorted(data, reverse=True), f"heap_sort({data}, reverse=True) should leave {sorted(data, reverse=True)}, got {b}."


def test_it_changes_the_same_list():
    a = [3, 1, 2]
    same = a
    heap_sort(a)
    assert a is same and a == [1, 2, 3], "Sort the list you are given in place; do not rebind the name to a new list (the caller would not see it)."


def test_negative_numbers_floats_and_strings():
    a = [3, -1, 0, -7, 2.5, 2, -0.5]
    heap_sort(a)
    assert a == [-7, -1, -0.5, 0, 2, 2.5, 3], f"Negative numbers and floats must be sorted too, got {a}."
    s = ["pear", "apple", "fig", "mango", "apple"]
    heap_sort(s)
    assert s == ["apple", "apple", "fig", "mango", "pear"], f"Strings must be sorted too, got {s}."


def test_random_lists_against_sorted():
    rng = random.Random(6)
    for _ in range(400):
        data = [rng.randint(-20, 20) for _ in range(rng.randint(0, 40))]
        a = list(data)
        heap_sort(a)
        assert a == sorted(data), f"Ascending sort of {data}: expected {sorted(data)}, got {a}."
        b = list(data)
        heap_sort(b, reverse=True)
        assert b == sorted(data, reverse=True), f"Descending sort of {data}: expected {sorted(data, reverse=True)}, got {b}."


def test_the_sorted_tail_is_never_touched_again():
    rng = random.Random(7)
    data = rng.sample(range(10_000), 3000)
    a = list(data)
    heap_sort(a)
    assert a == sorted(data), (
        "A big random list is not sorted. Does sift_down in phase 2 stop at the end of the heap part (index < end)? "
        "If it uses len(a), it pulls the sorted items back into the heap.")


def test_it_is_n_log_n_not_n_squared():
    n = 2000
    rng = random.Random(8)
    limit = 3 * n * math.log2(n)
    for name, data in (("random", rng.sample(range(10 ** 6), n)), ("ascending", list(range(n))), ("descending", list(range(n, 0, -1)))):
        for reverse in (False, True):
            a = [Counted(v) for v in data]
            Counted.comparisons = 0
            heap_sort(a, reverse)
            used = Counted.comparisons
            assert [c.v for c in a] == sorted(data, reverse=reverse), f"{name} data, reverse={reverse}: the result is not sorted."
            assert used <= limit, (
                f"{n} {name} items (reverse={reverse}) took {used} comparisons; heap sort needs about {int(2 * n * math.log2(n))}. "
                "Are you scanning for the largest item (selection sort) instead of sifting down?")


def test_a_hundred_thousand_items():
    rng = random.Random(9)
    data = [rng.randint(0, 10 ** 9) for _ in range(100_000)]
    a = list(data)
    heap_sort(a)
    assert a == sorted(data), "100,000 random numbers must come out sorted."
