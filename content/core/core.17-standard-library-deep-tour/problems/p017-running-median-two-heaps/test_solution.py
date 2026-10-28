import inspect
import random
import statistics

import pytest

import solution
from solution import MedianKeeper, running_medians


def brute(nums):
    return [statistics.median(nums[: i + 1]) for i in range(len(nums))]


def test_example():
    assert running_medians([5, 15, 1, 3]) == [5, 10.0, 5, 4.0], (
        "After 5: 5. After 5, 15: (5 + 15) / 2. After 1, 5, 15: 5. After 1, 3, 5, 15: (3 + 5) / 2."
    )


def test_types():
    got = running_medians([4, 8, 6])
    assert got == [4, 6.0, 6], "Medians: 4, then 6.0, then 6."
    assert type(got[0]) is int and type(got[2]) is int, "An odd count returns the middle value itself: an int stays an int."
    assert type(got[1]) is float, "An even count returns (a + b) / 2, a float."


def test_empty():
    k = MedianKeeper()
    assert len(k) == 0, "A new keeper is empty."
    with pytest.raises(ValueError):
        k.median()
    assert running_medians([]) == [], "No numbers, no medians."


def test_descending_and_ascending():
    assert running_medians([5, 4, 3, 2, 1]) == [5, 4.5, 4, 3.5, 3], (
        "Descending input: every new number goes to the low half, so you must move the top of low into high."
    )
    assert running_medians([1, 2, 3, 4, 5]) == [1, 1.5, 2, 2.5, 3], (
        "Ascending input: every new number goes to the high half, so you must move the top of high into low."
    )


def test_duplicates_and_negatives():
    nums = [2, 2, -1, 2, -1, -1, 0]
    assert running_medians(nums) == brute(nums), "Duplicates and negative numbers: remember to negate when pushing to and reading from the max-heap."


def test_floats():
    nums = [0.5, 2.25, -1.0, 7.75]
    assert running_medians(nums) == brute(nums), "Floats work the same way."


def test_random_against_statistics():
    rng = random.Random(1717)
    for size in (1, 2, 3, 10, 101, 500):
        nums = [rng.randint(-1000, 1000) for _ in range(size)]
        assert running_medians(nums) == brute(nums), f"Random list of {size}: every running median must equal statistics.median of the prefix."


def test_keeper_len_and_interleaving():
    k = MedianKeeper()
    for x in [10, 20, 30]:
        k.add(x)
    assert len(k) == 3, "len counts every number added, in both heaps."
    assert k.median() == 20, "Median of 10, 20, 30."
    k.add(0)
    assert k.median() == 15.0, "Median of 0, 10, 20, 30 is (10 + 20) / 2."
    k.add(100)
    assert k.median() == 20, "Median of 0, 10, 20, 30, 100."


def test_works_on_generator():
    gen = (x % 7 for x in range(50))
    expected = brute([x % 7 for x in range(50)])
    assert running_medians(gen) == expected, "nums may be a generator: walk it once."


def test_uses_heapq_not_sort():
    src = inspect.getsource(solution)
    assert "heappush" in src or "heappushpop" in src, "Use heapq to keep the two halves."
    assert "sorted(" not in src and ".sort(" not in src, "Do not sort: the point is O(log n) per number."


def test_keepers_independent():
    a = MedianKeeper()
    b = MedianKeeper()
    a.add(1)
    assert len(b) == 0, "Create the two heaps in __init__ so each keeper has its own."
