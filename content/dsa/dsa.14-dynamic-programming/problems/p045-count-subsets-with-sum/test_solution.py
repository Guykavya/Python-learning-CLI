import pathlib
import random
import subprocess
import sys

from solution import count_subsets

HERE = pathlib.Path(__file__).parent


def brute(nums, target):
    """Count every subset by bitmask (only for short lists)."""
    n = len(nums)
    count = 0
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += nums[i]
        if s == target:
            count += 1
    return count


def counts_dict(nums, target):
    ways = {0: 1}
    for x in nums:
        new = dict(ways)
        for s, c in ways.items():
            if s + x <= target:
                new[s + x] = new.get(s + x, 0) + c
        ways = new
    return ways.get(target, 0)


def test_chapter_examples():
    assert count_subsets([1, 2, 3, 3], 6) == 3, (
        "Expected 3: {1, 2, 3} twice (two different 3s) and {3, 3}. Count positions, not distinct values.")
    assert count_subsets([0, 0, 1], 1) == 4, (
        "Expected 4: {1}, {0, 1}, {0', 1}, {0, 0', 1}. Every zero doubles the count.")


def test_target_zero_and_empty():
    assert count_subsets([2, 4], 0) == 1, "Only the empty subset sums to 0: 1. Did you start with f[0] = 1?"
    assert count_subsets([], 0) == 1, "No numbers: the empty subset still sums to 0."
    assert count_subsets([], 3) == 0, "No numbers: nothing sums to 3."
    assert count_subsets([0, 0], 0) == 4, "{}, {0}, {0'}, {0, 0'}: 4 subsets sum to 0."


def test_zero_after_reaching_the_target():
    assert count_subsets([1, 0], 1) == 2, (
        "[1, 0] with target 1: {1} and {1, 0}. If you got 1, your recursion returns as soon as the sum "
        "hits the target and never considers the 0 after it. The base case is 'no numbers left'.")


def test_each_number_once():
    assert count_subsets([2], 4) == 0, (
        "Only one 2: nothing sums to 4. If you got 1, the s loop goes upwards and reuses the 2.")
    assert count_subsets([5], 3) == 0, "5 is bigger than 3: 0 subsets."


def test_random_against_brute_force():
    rng = random.Random(45)
    for _ in range(400):
        nums = [rng.choice([0, 0, 1, 2, 3, 4, 5]) for _ in range(rng.randint(0, 10))]
        target = rng.randint(0, 12)
        want = brute(nums, target)
        got = count_subsets(list(nums), target)
        assert got == want, (
            f"nums={nums}, target={target}: expected {want} (counted every subset), got {got}. "
            "Check f[0] = 1, the downward loop, and that zeros double the counts.")


def test_big_input_is_fast():
    rng = random.Random(4545)
    nums = [rng.randint(0, 50) for _ in range(200)]
    want = [counts_dict(nums, 1000), counts_dict([1] * 60, 30)]
    code = (
        "from solution import count_subsets\n"
        f"print(count_subsets({nums!r}, 1000), count_subsets([1] * 60, 30))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on 200 numbers. Listing subsets is 2**200: exponential: add a memo, "
        "or fill the count table f[s] for s up to target.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    got = r.stdout.split()
    assert got == [str(w) for w in want], (
        f"Large inputs: expected {[str(w)[:20] + '...' for w in want]}, got {[g[:20] + '...' for g in got]}. "
        "The second is C(60, 30): choose which 30 of the 60 ones.")
