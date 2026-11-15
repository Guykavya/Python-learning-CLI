import functools
import random
import subprocess
import sys
from pathlib import Path

import pytest

from solution import can_partition_k

HERE = Path(__file__).parent

def run_code(code, timeout, what):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{what} took more than {timeout} seconds.") from None
    assert r.returncode == 0, f"Your code crashed:\n{r.stderr[-800:]}"
    return r.stdout.strip()


def brute(nums, k):
    total = sum(nums)
    if total % k:
        return False
    side = total // k
    n = len(nums)

    @functools.cache
    def f(mask, cur):
        if mask == (1 << n) - 1:
            return True
        for i in range(n):
            if not mask >> i & 1 and cur + nums[i] <= side:
                if f(mask | 1 << i, (cur + nums[i]) % side):
                    return True
        return False

    return f(0, 0)


@pytest.mark.parametrize("nums, k, want, why", [
    ([4, 3, 2, 3, 5, 2, 1], 4, True, "the example: [5], [1, 4], [2, 3], [2, 3]"),
    ([1, 2, 3, 4], 3, False, "the total 10 is not divisible by 3"),
    ([1, 2, 3, 4], 2, True, "[1, 4] and [2, 3]"),
    ([2, 2, 2, 2, 3, 4, 5], 4, False, "the total 20 gives 5 per group, but the 2s cannot pair up"),
    ([10, 1, 1, 1], 2, False, "the total 13 is odd"),
    ([6, 1, 1, 1, 1, 2], 2, True, "[6] and [1, 1, 1, 1, 2]"),
    ([9, 1, 1, 1], 2, False, "the total 12 is even, but 9 is bigger than one group (6)"),
    ([5], 1, True, "k = 1: the whole list is one group"),
    ([3, 3, 3], 3, True, "each number is its own group"),
    ([2, 2, 3, 7, 8, 4], 2, True, "[8, 3, 2] and [7, 4, 2]; the first placements fail, so a wrong guess must be undone (buckets[b] -= nums[i])"),
    ([2, 2, 3, 3, 2, 4], 2, True, "total 16, groups of 8: [4, 2, 2] and [3, 3, 2]; a wrong first guess must be undone"),
])
def test_cases(nums, k, want, why):
    got = can_partition_k(list(nums), k)
    assert got is want, f"can_partition_k({nums}, {k}) should be {want}: {why}."


def test_input_unchanged():
    nums = [4, 3, 2, 3, 5, 2, 1]
    can_partition_k(nums, 4)
    assert nums == [4, 3, 2, 3, 5, 2, 1], "Do not change the caller's list: sort a copy (sorted(nums, reverse=True))."


def test_random_against_brute_force():
    rng = random.Random(29)
    for _ in range(80):
        n = rng.randint(1, 9)
        nums = [rng.randint(1, 9) for _ in range(n)]
        k = rng.randint(1, n)
        want = brute(nums, k)
        got = can_partition_k(list(nums), k)
        assert got is want, f"can_partition_k({nums}, {k}) should be {want}."


def test_hard_no_answer_in_time():
    nums = [6, 22, 8, 6, 24, 28, 4, 14, 30, 13, 26, 18, 30, 27, 10, 18]
    code = f"from solution import can_partition_k\nprint(can_partition_k({nums}, 4))\n"
    out = run_code(code, 20, "16 numbers into 4 groups with no answer (sort descending and try only one of the buckets "
                   "that currently have the same sum)")
    assert out == "False", f"can_partition_k({nums}, 4) is False (checked by a bit-mask search), got {out}."


def test_sixteen_with_answer():
    nums = [1, 2, 3, 4, 5, 6, 7, 8, 8, 7, 6, 5, 4, 3, 2, 1]
    code = f"from solution import can_partition_k\nprint(can_partition_k({nums}, 8))\n"
    out = run_code(code, 20, "16 numbers into 8 groups of 9")
    assert out == "True", "1..8 twice can be split into 8 pairs with sum 9."
