import random
import subprocess
import sys
from pathlib import Path

import pytest

from solution import count_subsets

HERE = Path(__file__).parent

def run_code(code, timeout, what):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{what} took more than {timeout} seconds.") from None
    assert r.returncode == 0, f"Your code crashed:\n{r.stderr[-800:]}"
    return r.stdout.strip()


def expected(nums, target):
    ways = {0: 1}
    for x in nums:
        new = dict(ways)
        for s, c in ways.items():
            new[s + x] = new.get(s + x, 0) + c
        ways = new
    return ways.get(target, 0)


@pytest.mark.parametrize("nums, target, want, why", [
    ([1, 2, 3, 4, 5], 5, 3, "[5], [1, 4] and [2, 3]"),
    ([1, 1], 1, 2, "subsets are counted by position: the first 1 or the second 1"),
    ([2, 4], 0, 1, "only the empty subset has sum 0"),
    ([], 0, 1, "the empty list still has the empty subset"),
    ([], 3, 0, "no items, no sum 3"),
    ([5, 5, 5], 10, 3, "three ways to pick two of the three 5s"),
    ([3, 7], 11, 0, "no subset reaches 11"),
    ([1, 2, 3], 6, 1, "only the whole list"),
])
def test_cases(nums, target, want, why):
    got = count_subsets(list(nums), target)
    assert got == want, f"count_subsets({nums}, {target}) should be {want} ({why}), got {got}."


def test_random_small():
    rng = random.Random(18)
    for _ in range(60):
        nums = [rng.randint(1, 9) for _ in range(rng.randint(0, 10))]
        target = rng.randint(0, 30)
        want = expected(nums, target)
        got = count_subsets(list(nums), target)
        assert got == want, (
            f"count_subsets({nums}, {target}) should be {want}, got {got}. "
            "If you got more, you probably keep recursing after reaching 0; if fewer, check equal numbers.")


def test_twenty_items_in_time():
    rng = random.Random(20)
    nums = [rng.randint(1, 50) for _ in range(20)]
    target = sum(nums) // 2
    want = expected(nums, target)
    code = f"from solution import count_subsets\nprint(count_subsets({nums}, {target}))\n"
    out = run_code(code, 40, "Counting the subsets of 20 numbers (about a million)")
    assert out == str(want), f"For 20 numbers the count should be {want}, got {out}."
