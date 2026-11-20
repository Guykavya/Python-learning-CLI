import itertools
import pathlib
import random
import subprocess
import sys

import pytest

import solution
from solution import subset_sum

HERE = pathlib.Path(__file__).parent


def brute(nums, target):
    """Try every subset (small inputs only)."""
    return any(sum(c) == target for r in range(len(nums) + 1) for c in itertools.combinations(nums, r))


def test_examples():
    assert subset_sum([3, 34, 4, 12, 5, 2], 9) is True, "Expected True: 4 + 5 = 9."
    assert subset_sum([3, 34, 4, 12, 5, 2], 30) is False, "Expected False: no subset makes 30."
    assert subset_sum([], 0) is True, "The empty subset sums to 0: f[0] = True."
    assert subset_sum([], 1) is False, "No numbers cannot make 1."


def test_each_number_once():
    assert subset_sum([2], 4) is False, (
        "subset_sum([2], 4) must be False: 2 + 2 uses the same element twice. Loop s DOWNWARDS so f[s - x] "
        "is still the value from before x.")
    assert subset_sum([3, 3], 6) is True, "Two different 3s may both be used: True."


def test_whole_number_and_zero():
    assert subset_sum([7], 7) is True, (
        "subset_sum([7], 7) must be True: the loop must also update s = x (stop at x - 1 in range).")
    assert subset_sum([0, 0], 0) is True, "Target 0 is always reachable."
    assert subset_sum([0, 5], 5) is True, "A zero changes nothing: 5 is reachable."


def test_returns_a_bool():
    got = subset_sum([1, 2], 3)
    assert got is True, f"Return True or False (a bool), got {got!r}."


def test_random_against_brute_force():
    rng = random.Random(4040)
    for _ in range(300):
        nums = [rng.randint(0, 15) for _ in range(rng.randint(0, 9))]
        target = rng.randint(0, 40)
        want = brute(nums, target)
        got = subset_sum(list(nums), target)
        assert got == want, (
            f"nums={nums}, target={target}: expected {want}, got {got}. f[0] = True; for each x, for s from "
            "target DOWN to x: f[s] = f[s] or f[s - x].")


def test_large_list_version():
    code = (
        "import random\n"
        "from solution import subset_sum\n"
        "rng = random.Random(40)\n"
        "nums = [rng.randint(0, 10**4) for _ in range(300)]\n"
        "evens = [rng.randrange(2, 10**4, 2) for _ in range(300)]\n"
        "print(subset_sum(nums, 10**4), subset_sum(evens, 9999))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=20, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, "Time limit (20 s) for 300 numbers and target 10**4: 2**300 subsets is impossible. Fill f."
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["True", "False"], (
        f"Large input: expected True, and False (even numbers cannot make the odd 9999); got {r.stdout.split()}.")


def test_bonus_bitset():
    if not hasattr(solution, "subset_sum_bits"):
        pytest.skip("Bonus: write subset_sum_bits(nums, target) with bits |= bits << x (optional).")
    from solution import subset_sum_bits
    rng = random.Random(404)
    for _ in range(200):
        nums = [rng.randint(0, 15) for _ in range(rng.randint(0, 9))]
        target = rng.randint(0, 40)
        want = brute(nums, target)
        got = subset_sum_bits(list(nums), target)
        assert got == want, (
            f"subset_sum_bits(nums={nums}, target={target}): expected {want}, got {got}. Start with bits = 1; "
            "for each x: bits |= bits << x; answer = (bits >> target) & 1 == 1.")
    code = (
        "import random\n"
        "from solution import subset_sum_bits\n"
        "rng = random.Random(4040)\n"
        "nums = [rng.randint(1, 10**4) for _ in range(2000)]\n"
        "print(subset_sum_bits(nums, 10**5), subset_sum_bits([2 * x for x in nums], 10**5 - 1))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Bonus: time limit (10 s) for 2,000 numbers and target 10**5. Use one integer as the whole row: "
        "no Python loop over the sums.")
    assert r.returncode == 0, "Bonus: your code crashed:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["True", "False"], (
        f"Bonus: expected True, and False (even numbers cannot make an odd target); got {r.stdout.split()}.")
