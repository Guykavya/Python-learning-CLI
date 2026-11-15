import random
import subprocess
import sys
from pathlib import Path

import pytest

from solution import next_greater_circular

HERE = Path(__file__).parent


def run_code(code, timeout, what):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{what} took more than {timeout} seconds.") from None
    assert r.returncode == 0, f"Your code crashed:\n{r.stderr[-800:]}"
    return r.stdout.strip()


def slow(nums):
    n = len(nums)
    ans = []
    for i in range(n):
        ans.append(next((nums[(i + d) % n] for d in range(1, n) if nums[(i + d) % n] > nums[i]), -1))
    return ans


@pytest.mark.parametrize("nums, want, why", [
    ([1, 2, 1], [2, -1, 2], "the last 1 walks around to the 2 at the start"),
    ([1, 2, 3, 4, 3], [2, 3, 4, -1, 4], "the last 3 finds 4 on the second lap"),
    ([5, 5], [-1, -1], "equal is not greater"),
    ([], [], "empty"),
    ([9], [-1], "one number cannot be its own answer"),
    ([3, 1, 2], [-1, 2, 3], "2 wraps around to 3"),
    ([4, 3, 2, 1], [-1, 4, 4, 4], "decreasing: everybody except the maximum finds 4 at the start"),
    ([2, 1, 2], [-1, 2, -1], "both 2s are maximums"),
])
def test_cases(nums, want, why):
    got = next_greater_circular(list(nums))
    assert got == want, f"next_greater_circular({nums}) should be {want}, got {got}: {why}."


def test_random_against_slow():
    rng = random.Random(27)
    for _ in range(1000):
        nums = [rng.randint(0, 5) for _ in range(rng.randint(0, 10))]
        assert next_greater_circular(list(nums)) == slow(nums), (
            f"next_greater_circular({nums}) should be {slow(nums)}.")


def test_big_in_time():
    code = (
        "from solution import next_greater_circular\n"
        "nums = [10 ** 6] + list(range(100000, 1, -1))\n"
        "ans = next_greater_circular(nums)\n"
        "print(ans[0], ans.count(10 ** 6))\n"
    )
    out = run_code(code, 20, "100,000 numbers in a circle (O(n) with two laps, not a double loop)")
    assert out == "-1 99999", f"Every number except the first finds 10**6 at the start; expected '-1 99999', got {out!r}."
