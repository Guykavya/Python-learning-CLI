import random
import tracemalloc

import pytest

from solution import find_duplicate


@pytest.mark.parametrize("nums, want", [
    ([1, 3, 4, 2, 2], 2),
    ([3, 1, 3, 4, 2], 3),
    ([1, 1], 1),
    ([1, 1, 2], 1),
    ([2, 2, 2, 2, 2], 2),
    ([2, 5, 9, 6, 9, 3, 8, 9, 7, 1], 9),
])
def test_cases(nums, want):
    copy = list(nums)
    got = find_duplicate(nums)
    assert nums == copy, (
        f"find_duplicate changed nums to {nums}. The array must stay as it was: walk it as a linked list instead "
        "of sorting it or marking values.")
    assert got == want, (
        f"find_duplicate({copy}) should be {want}, got {got!r}. Return the VALUE where the cycle starts "
        "(phase 2 of Floyd, starting again from index 0), not the meeting point of phase 1.")


def test_random():
    rng = random.Random(22)
    for _ in range(300):
        n = rng.randint(1, 30)
        dup = rng.randint(1, n)
        others = list(range(1, n + 1))
        others.remove(dup)
        k = rng.randint(2, n + 1)                    # dup appears k times
        rng.shuffle(others)
        nums = others[:n + 1 - k] + [dup] * k
        rng.shuffle(nums)
        assert find_duplicate(list(nums)) == dup, f"find_duplicate({nums}) should be {dup}."


def test_large_and_memory():
    n = 10**5
    nums = list(range(1, n + 1)) + [77_777]
    random.Random(5).shuffle(nums)
    copy = list(nums)
    tracemalloc.start()
    try:
        tracemalloc.reset_peak()
        got = find_duplicate(nums)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert nums == copy, "nums must not be changed."
    assert got == 77_777, f"The duplicate is 77777, got {got!r}."
    assert peak < 100_000, (
        f"find_duplicate used about {peak:,} bytes of extra memory for 100,001 numbers. A set, a counting list or "
        "a sorted copy grows with n; Floyd's pointers need only a few variables.")
