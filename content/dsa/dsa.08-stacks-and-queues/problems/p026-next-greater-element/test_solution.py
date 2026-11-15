import random
import subprocess
import sys
from pathlib import Path

import pytest

from solution import next_greater

HERE = Path(__file__).parent


def run_code(code, timeout, what):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{what} took more than {timeout} seconds.") from None
    assert r.returncode == 0, f"Your code crashed:\n{r.stderr[-800:]}"
    return r.stdout.strip()


def slow(nums):
    ans = []
    for i, x in enumerate(nums):
        ans.append(next((y for y in nums[i + 1:] if y > x), -1))
    return ans


@pytest.mark.parametrize("nums, want, why", [
    ([2, 1, 2, 4, 3], [4, 2, 4, -1, -1], "the chapter example"),
    ([2, 2, 3], [3, 3, -1], "equal is not greater: pop with <, not <="),
    ([5, 4, 3], [-1, -1, -1], "decreasing: nobody finds a greater number"),
    ([1, 2, 3], [2, 3, -1], "increasing: each answer is the next number"),
    ([], [], "empty list"),
    ([7], [-1], "one number"),
    ([3, 3, 3], [-1, -1, -1], "all equal: nothing is strictly greater"),
    ([-5, -1, -3], [-1, -1, -1], "-1 is a real value here, and -5's answer is -1 (the value), the others have none"),
    ([1, 5, 2, 3, 4, 6], [5, 6, 3, 4, 6, -1], "5 waits a long time for 6"),
])
def test_cases(nums, want, why):
    got = next_greater(list(nums))
    assert got == want, f"next_greater({nums}) should be {want}, got {got}: {why}."


def test_random_against_slow():
    rng = random.Random(26)
    for _ in range(1000):
        nums = [rng.randint(-3, 5) for _ in range(rng.randint(0, 12))]
        assert next_greater(list(nums)) == slow(nums), f"next_greater({nums}) should be {slow(nums)}."


def test_big_in_time():
    code = (
        "from solution import next_greater\n"
        "nums = list(range(100000, 0, -1))\n"
        "nums[-1] = 10 ** 9\n"
        "ans = next_greater(nums)\n"
        "print(ans.count(10 ** 9), ans[-1])\n"
    )
    out = run_code(code, 20, "next_greater on 100,000 numbers (use the O(n) monotonic stack, not a double loop)")
    assert out == "99999 -1", f"Every number except the last has 10**9 as its next greater; expected '99999 -1', got {out!r}."
