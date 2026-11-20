import random

import pytest

from solution import children, left, parent, right


def test_left_and_right_of_the_first_nodes():
    assert (left(0), right(0)) == (1, 2), (
        f"The root (index 0) has its children at 1 and 2, you gave {(left(0), right(0))}. "
        "With a list that starts at index 0 the formulas are 2*i + 1 and 2*i + 2.")
    assert (left(1), right(1)) == (3, 4), "The children of index 1 are 3 and 4 (2*i + 1 and 2*i + 2)."
    assert (left(2), right(2)) == (5, 6), "The children of index 2 are 5 and 6 (2*i + 1 and 2*i + 2)."
    assert (left(10), right(10)) == (21, 22), "left(10) is 21 and right(10) is 22."


@pytest.mark.parametrize("i, expected", [(1, 0), (2, 0), (3, 1), (4, 1), (5, 2), (6, 2), (7, 3), (8, 3), (9, 4), (100, 49), (101, 50)])
def test_parent_values(i, expected):
    got = parent(i)
    assert got == expected, (
        f"parent({i}) should be {expected}, got {got!r}. The formula is (i - 1) // 2: "
        "subtract 1 first, then use integer division (//).")
    assert isinstance(got, int), f"parent({i}) must be an int, got {got!r}. Use // and not /."


def test_parent_undoes_left_and_right():
    for i in range(0, 600):
        assert parent(left(i)) == i, f"parent(left({i})) should give {i}, got {parent(left(i))}. One of the two formulas is off."
        assert parent(right(i)) == i, f"parent(right({i})) should give {i}, got {parent(right(i))}. One of the two formulas is off."


def test_every_index_is_the_child_of_exactly_one_parent():
    seen = set()
    for i in range(0, 300):
        seen.update((left(i), right(i)))
    assert seen == set(range(1, 601)), (
        "The children of the indexes 0..299 must be exactly the indexes 1..600, each once. "
        "Your formulas skip an index or give one twice.")


@pytest.mark.parametrize("i, n, expected", [
    (0, 7, [1, 2]),
    (1, 7, [3, 4]),
    (2, 7, [5, 6]),
    (2, 6, [5]),
    (0, 2, [1]),
    (0, 1, []),
    (3, 7, []),
    (6, 7, []),
])
def test_children_examples(i, n, expected):
    got = children(i, n)
    assert got == expected, (
        f"children({i}, {n}) should be {expected}, got {got!r}. A child exists only if its index is "
        f"smaller than n = {n}; the left child comes first.")


def test_children_returns_a_list():
    assert isinstance(children(0, 7), list), "children must return a list (left child first), not a tuple or a generator."


def test_children_matches_the_definition_on_random_inputs():
    rng = random.Random(1)
    for _ in range(500):
        n = rng.randint(1, 60)
        i = rng.randint(0, 70)
        want = [c for c in (2 * i + 1, 2 * i + 2) if c < n]
        got = children(i, n)
        assert got == want, f"children({i}, {n}) should be {want}, got {got!r}."


def test_the_last_parent_and_the_first_leaf():
    for n in range(1, 40):
        last_parent = n // 2 - 1
        if last_parent >= 0:
            assert children(last_parent, n) != [], f"With n = {n} the index {last_parent} is the last parent: it must have a child."
        assert children(n // 2, n) == [], f"With n = {n} the index {n // 2} is already a leaf: it has no children."
