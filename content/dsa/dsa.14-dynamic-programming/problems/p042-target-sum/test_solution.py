import pathlib
import random
import subprocess
import sys
from itertools import product

from solution import target_sum

HERE = pathlib.Path(__file__).parent


def brute(nums, target):
    """Try every sign pattern (only for short lists)."""
    count = 0
    for signs in product((1, -1), repeat=len(nums)):
        if sum(s * x for s, x in zip(signs, nums)) == target:
            count += 1
    return count


def dict_count(nums, target):
    ways = {0: 1}
    for x in nums:
        new = {}
        for s, c in ways.items():
            new[s + x] = new.get(s + x, 0) + c
            new[s - x] = new.get(s - x, 0) + c
        ways = new
    return ways.get(target, 0)


def test_chapter_examples():
    assert target_sum([1, 1, 1, 1, 1], 3) == 5, (
        "Five ones, target 3: choose which one gets the minus sign, 5 ways. P = (5 + 3) / 2 = 4.")
    assert target_sum([1], 2) == 0, "2 is out of reach with a single 1."
    assert target_sum([1, 2], 0) == 0, (
        "[1, 2] can make 3, -1, 1, -3 but never 0. If you got 1, you forgot the parity check: "
        "total + target = 3 is odd, so P is not a whole number.")


def test_single_number():
    assert target_sum([1], 1) == 1, "+1 is the only way."
    assert target_sum([1], -1) == 1, "-1 is the only way. A negative target is allowed."
    assert target_sum([5], 0) == 0, "+5 or -5, never 0."


def test_negative_target():
    assert target_sum([2, 3], -1) == 1, "+2 - 3 = -1: one way."
    assert target_sum([1, 1, 1, 1, 1], -3) == 5, "By symmetry, -3 has as many ways as +3: 5."
    assert target_sum([1, 2, 3], -7) == 0, (
        "-7 is below -6 (all minus). Check abs(target) > total, not only target > total: "
        "otherwise P = (6 - 7) / 2 is negative.")


def test_zeros_count_twice():
    assert target_sum([0, 1], 1) == 2, "+0+1 and -0+1 are two different sign patterns: 2 ways."
    assert target_sum([0, 0, 0], 0) == 8, "Three zeros: 2 * 2 * 2 = 8 sign patterns, all give 0."
    assert target_sum([0], 0) == 2, "+0 and -0: 2 ways."


def test_random_against_brute_force():
    rng = random.Random(42)
    for _ in range(400):
        nums = [rng.randint(0, 6) for _ in range(rng.randint(1, 10))]
        target = rng.randint(-sum(nums) - 3, sum(nums) + 3)
        want = brute(nums, target)
        got = target_sum(list(nums), target)
        assert got == want, (
            f"nums={nums}, target={target}: expected {want} (tried every sign pattern), got {got}. "
            "Check the guards (abs and parity), zeros, and that the s loop goes downwards.")


def test_big_input_is_fast():
    rng = random.Random(4242)
    nums = [rng.randint(0, 100) for _ in range(100)]
    t1 = 10
    nums2 = [1] * 100
    want = [dict_count(nums, t1), dict_count(nums2, 0)]
    code = (
        "from solution import target_sum\n"
        f"print(target_sum({nums!r}, {t1}), target_sum({nums2!r}, 0))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on 100 numbers. Trying every sign pattern is 2**100: exponential: add a memo, "
        "or count subsets with sum P in a table.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == [str(w) for w in want], (
        f"Large inputs: expected {want}, got {r.stdout.split()}.")
