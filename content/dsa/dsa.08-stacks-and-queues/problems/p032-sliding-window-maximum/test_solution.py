import random
import subprocess
import sys
from pathlib import Path

import pytest

from solution import window_max

HERE = Path(__file__).parent


def run_code(code, timeout, what):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{what} took more than {timeout} seconds.") from None
    assert r.returncode == 0, f"Your code crashed:\n{r.stderr[-800:]}"
    return r.stdout.strip()


def slow(nums, k):
    return [max(nums[i:i + k]) for i in range(len(nums) - k + 1)]


@pytest.mark.parametrize("nums, k, want, why", [
    ([1, 3, -1, -3, 5, 3, 6, 7], 3, [3, 3, 5, 5, 6, 7], "the chapter example"),
    ([9, 3, 2, 1], 2, [9, 3, 2], "the 9 must leave from the FRONT when it is outside the window"),
    ([4, 2], 1, [4, 2], "k = 1: every value is its own window"),
    ([4, 2], 3, [], "k larger than the list: no window at all"),
    ([], 1, [], "empty list"),
    ([2, 7, 1], 3, [7], "k = n: one window"),
    ([1, 2, 3, 4, 5], 2, [2, 3, 4, 5], "increasing: the deque never holds more than one index"),
    ([5, 4, 3, 2, 1], 2, [5, 4, 3, 2], "decreasing: only the front check removes anything"),
    ([5, 4, 3, 2, 1], 3, [5, 4, 3], "decreasing with k = 3"),
    ([2, 2, 2, 2], 2, [2, 2, 2], "equal values"),
])
def test_cases(nums, k, want, why):
    got = window_max(list(nums), k)
    assert got == want, f"window_max({nums}, {k}) should be {want}, got {got}: {why}."


def test_random_against_slow():
    rng = random.Random(32)
    for _ in range(1000):
        n = rng.randint(0, 12)
        nums = [rng.randint(-3, 3) for _ in range(n)]
        k = rng.randint(1, n + 1)
        assert window_max(list(nums), k) == slow(nums, k), f"window_max({nums}, {k}) should be {slow(nums, k)}."


def test_big_in_time():
    code = (
        "from solution import window_max\n"
        "nums = list(range(200000, 0, -1))\n"
        "out = window_max(nums, 100000)\n"
        "print(len(out), out[0], out[-1])\n"
    )
    out = run_code(code, 20, "window_max on 200,000 numbers with k = 100,000 (O(n) deque, not max() of every window)")
    assert out == "100001 200000 100000", f"Expected '100001 200000 100000', got {out!r}."
