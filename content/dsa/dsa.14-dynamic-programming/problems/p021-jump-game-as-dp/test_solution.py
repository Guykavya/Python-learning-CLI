import pathlib
import random
import subprocess
import sys

from solution import min_jumps

HERE = pathlib.Path(__file__).parent


def brute(nums, i=0):
    """Plain recursion: fewest jumps from i to the end, or None. Exponential; small inputs only."""
    last = len(nums) - 1
    if i == last:
        return 0
    best = None
    for j in range(i + 1, min(last, i + nums[i]) + 1):
        rest = brute(nums, j)
        if rest is not None and (best is None or rest + 1 < best):
            best = rest + 1
    return best


def run_big(code, timeout=10):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=timeout, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_examples():
    assert min_jumps([2, 3, 1, 1, 4]) == 2, "Expected 2 (0 -> 1 -> 4)."
    assert min_jumps([3, 2, 1, 0, 4]) == -1, (
        "Expected -1: every route lands on index 3, which has jump 0. Return -1 when f[last] is still INF.")
    assert min_jumps([1, 0, 5]) == -1, "Expected -1: index 1 has jump 0, so index 2 is never reached."


def test_small_edges():
    assert min_jumps([0]) == 0, "One element: you already stand on the last index, 0 jumps (base case f[0] = 0)."
    assert min_jumps([1, 1]) == 1, "Expected 1 jump."
    assert min_jumps([0, 1]) == -1, "Index 0 has jump 0: the last index is unreachable, so -1."
    assert min_jumps([5, 0, 0]) == 1, (
        "Expected 1: a jump of length 2 is allowed (any length up to 5). Do not index past the end of the list: "
        "stop j at min(last, i + nums[i]).")


def test_unreachable_index_sends_nothing():
    assert min_jumps([1, 0, 9, 1]) == -1, (
        "Index 2 has a big jump but is never reached. If you relax from an index whose f is INF, "
        "INF + 1 stays INF, so the answer must still be -1, not a number.")


def test_random_against_recursion():
    rng = random.Random(21)
    for _ in range(500):
        nums = [rng.randint(0, 3) for _ in range(rng.randint(1, 11))]
        want = brute(nums)
        want = -1 if want is None else want
        got = min_jumps(list(nums))
        assert got == want, (
            f"nums={nums}: expected {want}, got {got}. f[j] must be the minimum of f[i] + 1 over every i "
            "that can reach j; and -1 when the last cell stays INF.")


def test_big_needs_memo_or_table():
    code = (
        "from solution import min_jumps\n"
        "a = [3] * 400\n"
        "b = [2] * 200 + [1, 0, 0] + [5] * 197\n"
        "c = [1] * 400\n"
        "print(min_jumps(a), min_jumps(b), min_jumps(c))\n"
    )
    r = run_big(code)
    assert r is not None, (
        "Time limit (10 s) on 400 elements. exponential: add a memo. A recursion that tries every jump "
        "solves the same index again and again; fill a table f[0..n-1] from left to right instead.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["133", "-1", "399"], (
        f"Large inputs: expected 133, -1 and 399; got {r.stdout.split()}.")
