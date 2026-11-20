import pathlib
import random
import subprocess
import sys

from solution import max_subarray

HERE = pathlib.Path(__file__).parent


def brute(nums):
    """Try every block i..j (O(n^2), small inputs only)."""
    best = nums[0]
    for i in range(len(nums)):
        total = 0
        for j in range(i, len(nums)):
            total += nums[j]
            best = max(best, total)
    return best


def run_big(code, limit):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=limit, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_chapter_example():
    got = max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4])
    assert got != (6, [-2, 1, -2, 4, 3, 5, 6, 1, 5]), "Return only the best sum, not (best, table)."
    assert got == 6, f"Expected 6 (block [4, -1, 2, 1]), got {got}."


def test_all_negative():
    assert max_subarray([-3, -1, -2]) == -1, (
        "All negative: the answer is the largest single item, -1. If you got 0, you started from 0 "
        "(an empty block); start from nums[0].")
    assert max_subarray([-7]) == -7, "One item: the block is that item."


def test_answer_does_not_end_at_the_last_item():
    assert max_subarray([5, -9, 6]) == 6, "Expected 6: the block [6]. Restart when the old block is negative."
    assert max_subarray([3, 4, -10]) == 7, (
        "Expected 7 (block [3, 4]). The best block may end before the last item: return the max over all i, "
        "not f(n - 1).")


def test_random_against_brute_force():
    rng = random.Random(1313)
    for _ in range(500):
        nums = [rng.randint(-10, 10) for _ in range(rng.randint(1, 15))]
        want = brute(nums)
        got = max_subarray(list(nums))
        assert got == want, (
            f"nums={nums}: expected {want} (all blocks tried), got {got}. "
            "f(i) = max(nums[i], f(i-1) + nums[i]); answer = max of all f(i).")


def test_large_input_is_linear():
    code = (
        "import random\n"
        "from solution import max_subarray\n"
        "rng = random.Random(1313)\n"
        "a = [rng.randint(-1000, 1000) for _ in range(10**5)]\n"
        "b = [-(i % 997) - 1 for i in range(10**5)]\n"
        "c = [(-1) ** i * i for i in range(10**5)]\n"
        "print(max_subarray(a), max_subarray(b), max_subarray(c))\n"
    )
    r = run_big(code, 10)
    assert r is not None, (
        "Time limit (10 s) for 100,000 items: trying every block is O(n^2). Keep only the best block "
        "ending at the current index (one pass).")
    if "RecursionError" in r.stderr:
        assert False, "RecursionError on 100,000 items: use one loop, not recursion."
    assert r.returncode == 0, "Your code crashed on 100,000 items:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["373004", "-1", "99998"], (
        f"Large inputs: expected 373004 -1 99998, got {r.stdout.split()}.")
