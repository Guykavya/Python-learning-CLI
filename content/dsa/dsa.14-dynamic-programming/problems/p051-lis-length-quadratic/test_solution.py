import pathlib
import random
import subprocess
import sys
from bisect import bisect_left

from solution import lis_length

HERE = pathlib.Path(__file__).parent


def brute(nums):
    """Check every subsequence (only for short lists)."""
    n = len(nums)
    best = 0
    for mask in range(1 << n):
        picked = [nums[i] for i in range(n) if mask >> i & 1]
        if all(picked[k] < picked[k + 1] for k in range(len(picked) - 1)):
            best = max(best, len(picked))
    return best


def fast(nums):
    tails = []
    for x in nums:
        k = bisect_left(tails, x)
        if k == len(tails):
            tails.append(x)
        else:
            tails[k] = x
    return len(tails)


def test_chapter_examples():
    assert lis_length([10, 9, 2, 5, 3, 7, 101, 18]) == 4, "Expected 4, for example 2, 3, 7, 18."
    assert lis_length([0, 1, 0, 3, 2, 3]) == 4, "Expected 4: 0, 1, 2, 3."


def test_equal_values_do_not_count():
    assert lis_length([7, 7, 7, 7]) == 1, (
        "Strictly increasing: equal values do not extend each other. If you got 4, use < not <=.")
    assert lis_length([2, 2, 3, 3, 1]) == 2, "Strictly increasing: 2, 3. Got 4? That is non-decreasing."


def test_empty_and_single():
    assert lis_length([]) == 0, "An empty list has no subsequence: 0. (max of an empty f raises ValueError.)"
    assert lis_length([5]) == 1, "One item is an increasing subsequence of length 1."


def test_best_does_not_end_at_the_last_item():
    assert lis_length([1, 2, 3, 0]) == 3, (
        "Expected 3 (1, 2, 3). The answer is max(f), not f[-1]: the best subsequence may end anywhere.")
    assert lis_length([1, 5, 2, 3]) == 3, (
        "Expected 3 (1, 2, 3). A subsequence may skip items; this is not the longest increasing run.")
    assert lis_length([3, 2, 1]) == 1, "Decreasing list: 1. Counting distinct values gives 3."


def test_random_against_brute_force():
    rng = random.Random(51)
    for _ in range(400):
        nums = [rng.randint(-5, 8) for _ in range(rng.randint(0, 11))]
        want = brute(nums)
        got = lis_length(list(nums))
        assert got == want, (
            f"nums={nums}: expected {want} (checked every subsequence), got {got}. "
            "f[i] = 1 + max f[j] over j < i with nums[j] < nums[i]; the answer is max(f).")


def test_big_input_is_fast():
    rng = random.Random(5151)
    cases = [[rng.randint(-10**6, 10**6) for _ in range(800)], list(range(800)), list(range(800, 0, -1))]
    want = [fast(c) for c in cases]
    code = (
        "from solution import lis_length\n"
        f"cases = {cases!r}\n"
        "print(*[lis_length(c) for c in cases])\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on 800 numbers. Trying every subsequence (or a recursion that does not remember "
        "results) is exponential: add a memo, or fill f[i] for i = 0 .. n-1.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == [str(w) for w in want], (
        f"Large inputs: expected {want}, got {r.stdout.split()}.")
