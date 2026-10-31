import random

from solution import k_smallest, pop_k_smallest, top_k_by


def test_k_smallest_basic():
    assert k_smallest([5, 1, 4, 1, 9], 3) == [1, 1, 4], "The 3 smallest, ascending, duplicates included."
    assert k_smallest([5, 1], 10) == [1, 5], "k bigger than the input: everything, sorted."
    assert k_smallest([5, 1], 0) == [], "k = 0: nothing."
    assert k_smallest([5, 1], -1) == [], "Negative k: nothing."


def test_k_smallest_any_iterable():
    assert k_smallest((x * x for x in range(10, 0, -1)), 2) == [1, 4], "nums may be a generator: nsmallest accepts any iterable."


def test_top_k_by():
    recs = [{"n": "a", "s": 3}, {"n": "b", "s": 9}, {"n": "c", "s": 3}, {"n": "d", "s": 1}]
    got = top_k_by(recs, 2, "s")
    assert got == [{"n": "b", "s": 9}, {"n": "a", "s": 3}], "Largest first; with equal 's', the record that came first in the input wins."
    got3 = top_k_by(recs, 3, "s")
    assert [r["n"] for r in got3] == ["b", "a", "c"], "Ties keep input order: 'a' before 'c'."


def test_top_k_by_field_and_bounds():
    recs = [{"x": 1, "y": 5}, {"x": 2, "y": 4}]
    assert top_k_by(recs, 1, "y") == [{"x": 1, "y": 5}], "Use the field named by the argument."
    assert top_k_by(recs, 1, "x") == [{"x": 2, "y": 4}], "Use the field named by the argument."
    assert top_k_by(recs, 0, "x") == [], "k = 0: nothing."
    assert top_k_by([], 3, "x") == [], "No records: nothing."


def test_top_k_by_does_not_compare_dicts():
    recs = [{"v": 1}, {"v": 1}, {"v": 1}]
    assert top_k_by(recs, 2, "v") == [{"v": 1}, {"v": 1}], (
        "Equal keys must not make Python compare the dicts themselves (TypeError). Use key=, not (value, record) tuples."
    )


def test_pop_k_smallest_matches():
    rng = random.Random(17)
    nums = [rng.randint(-50, 50) for _ in range(200)]
    for k in (1, 5, 50, 200, 250):
        assert pop_k_smallest(nums, k) == sorted(nums)[:k], f"pop_k_smallest(nums, {k}) must equal sorted(nums)[:k]: heappop returns the smallest each time."


def test_pop_k_smallest_does_not_mutate():
    nums = [3, 2, 1]
    assert pop_k_smallest(nums, 2) == [1, 2], "The two smallest: [1, 2]."
    assert nums == [3, 2, 1], "heapify works IN PLACE. Copy the list first (heap = list(nums)) so the caller's list is untouched."


def test_pop_k_smallest_bounds():
    assert pop_k_smallest([4, 2], 0) == [], "k = 0: pop nothing."
    assert pop_k_smallest([4, 2], -3) == [], "Negative k: pop nothing."
    assert pop_k_smallest([4, 2], 5) == [2, 4], "k too big: stop when the heap is empty instead of raising IndexError."
    assert pop_k_smallest([], 1) == [], "Empty input: nothing to pop."
