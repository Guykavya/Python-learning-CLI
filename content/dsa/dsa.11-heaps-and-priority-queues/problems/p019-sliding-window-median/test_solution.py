import random
import statistics
import subprocess
import sys
from pathlib import Path

import pytest

from solution import sliding_median

HERE = Path(__file__).parent


def brute(nums, k):
    if k < 1 or k > len(nums):
        return []
    return [statistics.median(nums[i:i + k]) for i in range(len(nums) - k + 1)]


def test_the_examples():
    assert sliding_median([1, 3, -1, -3, 5, 3, 6, 7], 3) == [1, -1, -1, 3, 5, 6], (
        "windows of 3 over [1, 3, -1, -3, 5, 3, 6, 7]: medians 1, -1, -1, 3, 5, 6.")
    assert sliding_median([1, 2, 3, 4, 2, 3, 1, 4, 2], 2) == [1.5, 2.5, 3.5, 3.0, 2.5, 2.0, 2.5, 3.0], (
        "even k: each median is the average of the two middle numbers, (a + b) / 2.")


def test_window_of_one_and_full_window():
    assert sliding_median([5], 1) == [5], "one number, one window: the number itself."
    assert sliding_median([4, 1, 7, 2], 1) == [4, 1, 7, 2], "k = 1: every number is its own median."
    assert sliding_median([4, 1, 7, 2], 4) == [3.0], "k = len(nums): one window, median (2 + 4) / 2 = 3.0."
    assert sliding_median([4, 1, 7], 3) == [4], "k = len(nums) = 3: one window, the middle of 1, 4, 7 is 4."


def test_empty_and_impossible_windows_give_an_empty_list():
    assert sliding_median([], 3) == [], "no numbers: no windows."
    assert sliding_median([1, 2], 3) == [], "k bigger than len(nums): no window fits."
    assert sliding_median([1, 2], 0) == [], "k = 0 is not a window: return []."


def test_odd_k_returns_numbers_from_the_data():
    got = sliding_median([3, 1, 2, 5, 4], 3)
    assert got == [2, 2, 4], f"expected [2, 2, 4], got {got}."
    assert all(type(v) is int for v in got), "for odd k the median is an item of nums (an int), not a float."


def test_even_k_uses_true_division():
    assert sliding_median([1, 2, 3, 4], 2) == [1.5, 2.5, 3.5], "(1 + 2) / 2 = 1.5: do not use integer division."
    assert sliding_median([-3, 4, -1, 2], 2) == [0.5, 1.5, 0.5], "negative numbers: (-3 + 4) / 2 = 0.5."


def test_duplicates_leaving_the_window():
    # Equal values can sit in both halves; the live counts must stay right when one of them leaves.
    assert sliding_median([2, 2, 2, 1, 1, 1], 3) == [2, 2, 1, 1], (
        "equal numbers can be in different halves. When one of them leaves, only ONE copy is gone: do not mark every number with that value as gone.")
    assert sliding_median([1, 1, 1, 1, 1], 2) == [1.0, 1.0, 1.0, 1.0], "all equal: every median is 1."


def test_the_input_list_is_not_changed():
    nums = [5, 2, 9, 1, 7, 3]
    keep = list(nums)
    sliding_median(nums, 3)
    assert nums == keep, "your function changed `nums` (did you sort it?). Work on copies."


@pytest.mark.parametrize("seed", range(60))
def test_random_inputs_match_the_brute_force(seed):
    rng = random.Random(seed)
    n = rng.randint(1, 40)
    spread = rng.choice([1, 2, 5, 50, 10 ** 9])         # small spread = many duplicates
    nums = [rng.randint(-spread, spread) for _ in range(n)]
    k = rng.randint(1, n)
    got = sliding_median(nums, k)
    want = brute(nums, k)
    assert got == want, (
        f"nums = {nums}, k = {k}:\nexpected {want}\ngot      {got}\n"
        "Check the live counts of the two halves, stale tops that are not popped, and which copy of a duplicate leaves.")


def test_ascending_descending_and_constant_inputs():
    for nums in (list(range(30)), list(range(30, 0, -1)), [7] * 30, [0, 1] * 15):
        for k in (1, 2, 3, 4, 7, 10, 29, 30):
            assert sliding_median(nums, k) == brute(nums, k), f"nums = {nums}, k = {k}"


BIG = """
import random
from solution import sliding_median
rng = random.Random(11)
nums = [rng.randint(-10**6, 10**6) for _ in range(100000)]
out = sliding_median(nums, 20000)
print(len(out), sum(out), out[0], out[-1])
"""

BIG_CHECK = """
import bisect, random
rng = random.Random(11)
nums = [rng.randint(-10**6, 10**6) for _ in range(100000)]
k = 20000
win = sorted(nums[:k])
out = []
for i in range(k, len(nums) + 1):
    out.append((win[k // 2 - 1] + win[k // 2]) / 2)
    if i == len(nums):
        break
    del win[bisect.bisect_left(win, nums[i - k])]
    bisect.insort(win, nums[i])
print(len(out), sum(out), out[0], out[-1])
"""


def run_code(code, seconds):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=seconds)
    except subprocess.TimeoutExpired:
        return None
    assert r.returncode == 0, "your code crashed on the big case:\n" + r.stderr[-600:]
    return r.stdout.strip()


def test_big_input_in_time():
    got = run_code(BIG, 10)
    assert got is not None, (
        "100,000 numbers with k = 20000 did not finish in 10 seconds. Sorting every window costs O(k log k) per step, and "
        "deleting the leaving number from a heap with list.remove costs O(k). Use two heaps with lazy deletion: each step is O(log n).")
    want = run_code(BIG_CHECK, 60)
    assert got == want, f"big case: expected {want}, got {got}."
