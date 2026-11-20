import heapq
import random

import pytest

from solution import is_min_heap


def brute(a):
    """The definition, written the other way round: every parent against its children."""
    n = len(a)
    for p in range(n):
        for c in (2 * p + 1, 2 * p + 2):
            if c < n and a[c] < a[p]:
                return False
    return True


@pytest.mark.parametrize("a", [[], [5], [2, 2, 2], [1, 3, 2], [1, 3, 2, 7, 4, 5, 6], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]])
def test_valid_heaps(a):
    assert is_min_heap(a) is True, f"{a} is a valid min-heap. Equal items are allowed, and so are lists of 0 or 1 item. Return True."


def test_empty_and_single_are_heaps():
    assert is_min_heap([]) is True, "An empty list has no pairs to break the rule: it is a heap."
    assert is_min_heap([42]) is True, "One item has no parent and no children: it is a heap."


@pytest.mark.parametrize("a", [
    [2, 1],
    [3, 2, 1],
    [1, 3, 2, 7, 4, 5, 0],
    [1, 3, 2, 7, 4, 0, 6],
    [1, 3, 2, 0, 4, 5, 6],
    [9, 8, 7, 6, 5, 4, 3, 2, 1],
])
def test_broken_heaps(a):
    assert is_min_heap(a) is False, (
        f"{a} is not a min-heap: some item is smaller than its parent (the parent of index i is (i - 1) // 2). "
        "Check BOTH children of every parent, including the right one and the last parent.")


def test_only_the_right_child_is_wrong():
    assert is_min_heap([1, 5, 5, 6, 7, 4]) is False, (
        "In [1, 5, 5, 6, 7, 4] only the item 4 (index 5) is wrong: its parent is index 2 (value 5). "
        "Do you check the right children as well as the left ones?")


def test_the_last_parent_has_only_a_left_child():
    assert is_min_heap([1, 2, 3, 4]) is True, "[1, 2, 3, 4] is a heap (index 1 has only a left child, 4)."
    assert is_min_heap([1, 2, 3, 0]) is False, "In [1, 2, 3, 0] the last item 0 is smaller than its parent 2 (index 1)."
    assert is_min_heap([1, 5, 3, 4]) is False, "In [1, 5, 3, 4] the last parent (index 1, value 5) is larger than its only child 4."


def test_a_sorted_list_is_a_heap_but_a_heap_is_not_always_sorted():
    assert is_min_heap([1, 3, 2, 7, 4, 5, 6]) is True, (
        "[1, 3, 2, 7, 4, 5, 6] is a heap although it is not sorted (3 comes before 2). "
        "Do not compare neighbours: compare every item with its PARENT.")
    assert is_min_heap(list(range(100))) is True, "A list sorted from small to large is always a heap."


def test_equal_items_are_allowed():
    assert is_min_heap([4, 4, 4, 4, 4, 4]) is True, "Equal items are allowed: the rule is parent <= child, not parent < child."
    assert is_min_heap([1, 1, 2, 1]) is True, "In [1, 1, 2, 1] the item at index 3 (value 1) equals its parent (index 1, value 1): that is allowed."
    assert is_min_heap([2, 2, 1]) is False, "In [2, 2, 1] the item 1 is smaller than its parent 2, equal items elsewhere do not matter."


def test_strings_work_too():
    assert is_min_heap(["ant", "bee", "cat", "dog"]) is True, "Strings compare too: ['ant', 'bee', 'cat', 'dog'] is a heap."
    assert is_min_heap(["cat", "ant", "bee"]) is False, "'ant' is smaller than its parent 'cat'."


def test_the_list_is_not_changed():
    a = [1, 5, 3, 4]
    copy = list(a)
    is_min_heap(a)
    assert a == copy, "is_min_heap must only look at the list. Do not heapify, sort or pop the list you are given."


def test_random_lists_against_the_definition():
    rng = random.Random(7)
    for _ in range(600):
        n = rng.randint(0, 20)
        a = [rng.randint(0, 6) for _ in range(n)]
        assert is_min_heap(a) is brute(a), f"{a}: the correct answer is {brute(a)}."


def test_heapified_lists_and_one_broken_item():
    rng = random.Random(8)
    for _ in range(400):
        n = rng.randint(1, 25)
        a = [rng.randint(0, 50) for _ in range(n)]
        heapq.heapify(a)
        assert is_min_heap(a) is True, f"{a} was made by heapq.heapify: it is a heap."
        i = rng.randint(1, n - 1) if n > 1 else 0
        if i > 0:
            b = list(a)
            b[i] = b[(i - 1) // 2] - 1            # now smaller than its parent
            assert is_min_heap(b) is False, f"{b}: the item at index {i} is smaller than its parent at index {(i - 1) // 2}."


def test_long_list_is_fast():
    a = list(range(100000))
    assert is_min_heap(a) is True, "A sorted list of 100000 items is a heap."
    a[99999] = -1
    assert is_min_heap(a) is False, "The last item -1 is smaller than its parent."
