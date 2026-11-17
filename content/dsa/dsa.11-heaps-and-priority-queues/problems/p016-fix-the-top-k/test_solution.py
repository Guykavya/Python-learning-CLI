import random

import pytest

from solution import top_scores


class Counted:
    """A number that counts every comparison made with it. It can be compared but not negated."""
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


def test_the_classmates_own_tests_still_pass():
    assert top_scores([5, 1, 9], 3) == [9, 5, 1], "k equal to the number of scores: [9, 5, 1]."
    assert top_scores([4, 4, 4], 3) == [4, 4, 4], "Equal scores are all kept."


def test_the_example_returns_the_highest_not_the_lowest():
    scores = [3, 1, 5, 12, 2, 11, 7]
    got = top_scores(scores, 3)
    lowest = sorted(scores)[:3][::-1]
    assert got != lowest, (
        f"You return {got}, the 3 LOWEST scores. A heap of negated numbers has the BEST kept score at its root, so the code throws "
        "the best scores away. To keep the k highest scores the root must be the weakest kept score: a min-heap of the scores themselves.")
    assert got == [12, 11, 7], f"Expected [12, 11, 7] (the 3 highest, highest first), got {got}."


def test_k_zero_and_negative():
    try:
        got = top_scores([3, 1, 5], 0)
    except IndexError:
        pytest.fail("IndexError for k = 0: with k = 0 the heap stays empty, and heap[0] fails. Return [] before the loop.")
    assert got == [], f"k = 0 gives an empty list, got {got}."
    assert top_scores([3, 1, 5], -2) == [], "A negative k gives an empty list."
    assert top_scores([], 0) == [], "No scores, k = 0."


def test_k_one_is_the_maximum_and_k_larger_than_n():
    assert top_scores([4, 9, 2], 1) == [9], "k = 1 gives only the maximum."
    assert top_scores([4, 9, 2], 10) == [9, 4, 2], "k larger than the number of scores gives all of them, highest first."
    assert top_scores([], 3) == [], "No scores: empty list."


def test_the_order_is_highest_first():
    got = top_scores([1, 8, 3, 9, 5], 4)
    assert got == [9, 8, 5, 3], f"Expected [9, 8, 5, 3] (highest first), got {got}."


def test_duplicates_negatives_and_floats():
    assert top_scores([7, 7, 3, 7, 1], 2) == [7, 7], "Equal scores are all kept: two of the three 7s."
    assert top_scores([-5, -1, -9, -1], 2) == [-1, -1], "Negative scores: the highest are the ones closest to zero."
    assert top_scores([2.5, 0.5, 3.25, 1.0], 2) == [3.25, 2.5], "Floats work too."


def test_any_iterable_and_the_input_is_not_changed():
    data = [3, 1, 5, 12, 2, 11, 7]
    copy = list(data)
    top_scores(data, 3)
    assert data == copy, "Do not change the list you receive."
    assert top_scores((x for x in data), 3) == [12, 11, 7], "A generator must work: read the scores once, with a for loop."
    assert top_scores(tuple(data), 2) == [12, 11], "A tuple must work."


def test_random_inputs_against_sorting():
    rng = random.Random(16)
    for _ in range(500):
        data = [rng.randint(-15, 15) for _ in range(rng.randint(0, 25))]
        k = rng.randint(-1, 30)
        want = sorted(data, reverse=True)[:max(k, 0)]
        got = top_scores(data, k)
        assert got == want, f"top_scores({data}, {k}) should be {want}, got {got}."


def test_it_stays_a_bounded_heap_not_a_full_sort():
    n, k = 50_000, 10
    rng = random.Random(20)
    values = rng.sample(range(10 ** 7), n)
    items = [Counted(v) for v in values]
    Counted.comparisons = 0
    try:
        got = top_scores(items, k)
    except TypeError as error:
        pytest.fail(f"TypeError: {error}. The scores in this test can be compared but not negated: keep the scores themselves in the heap (a min-heap of size k).")
    used = Counted.comparisons
    assert [c.v for c in got] == sorted(values, reverse=True)[:k], "The 10 highest of 50,000 scores are wrong or not highest first."
    assert used <= 10 * n, (
        f"{n} scores and k = {k} used {used} comparisons ({used // n} per score); a size-k heap needs between 1 and about 7, a full sort about 14. "
        "Keep a heap of at most k scores; do not sort everything.")
