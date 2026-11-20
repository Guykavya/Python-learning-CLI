import pathlib
import random
import subprocess
import sys

from solution import rob

HERE = pathlib.Path(__file__).parent


def brute(nums):
    """Try every set of houses with no two neighbours (small inputs only)."""
    def go(i):
        if i >= len(nums):
            return 0
        return max(go(i + 1), nums[i] + go(i + 2))
    return go(0)


def run_big(code, limit):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=limit, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_chapter_examples():
    got = rob([2, 7, 9, 3, 1])
    assert got != (12, [0, 2, 7, 11, 11, 12]), "Return only the best total, not (best, table)."
    assert got == 12, f"Expected 12 (2 + 9 + 1), got {got}. Robbing the richest house 7 first gives only 10."
    assert rob([1, 2, 3, 1]) == 4, "Expected 4 (1 + 3)."


def test_skipping_two_in_a_row():
    assert rob([2, 1, 1, 2]) == 4, (
        "Expected 4 (the two ends). Taking every other house (2 + 1 or 1 + 2) is not enough: the best set may "
        "skip two houses in a row. f(i) = max(f(i-1), f(i-2) + nums[i-1]).")


def test_small_edges():
    assert rob([]) == 0, "No houses: 0."
    assert rob([5]) == 5, "One house: rob it. f(1) = nums[0]."
    assert rob([5, 9]) == 9, "Two houses: the richer one."
    assert rob([0, 0, 0]) == 0, "All empty: 0."


def test_random_against_brute_force():
    rng = random.Random(1111)
    for _ in range(400):
        nums = [rng.randint(0, 20) for _ in range(rng.randint(0, 15))]
        want = brute(nums)
        got = rob(list(nums))
        assert got == want, (
            f"nums={nums}: expected {want} (all valid sets tried), got {got}. Check the base cases and that "
            "the rob branch adds to f(i-2), not f(i-1).")


def test_not_exponential():
    code = "from solution import rob\nprint(rob([3, 1] * 100))\n"
    r = run_big(code, 5)
    assert r is not None, (
        "Time limit (5 s) for 200 houses: exponential: add a memo. Rob-or-skip without a notebook makes "
        "about 1.6**n calls.")
    assert r.returncode == 0, "Your code crashed on 200 houses:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["300"], f"[3, 1] * 100: expected 300, got {r.stdout.split()}."


def test_large_input():
    code = (
        "import random\n"
        "from solution import rob\n"
        "rng = random.Random(1111)\n"
        "a = [rng.randint(0, 400) for _ in range(10**5)]\n"
        "b = [i % 7 for i in range(10**5)]\n"
        "print(rob(a), rob(b), rob(list(range(200))))\n"
    )
    r = run_big(code, 10)
    assert r is not None, "Time limit (10 s) for 100,000 houses: use a table or two rolling variables."
    if "RecursionError" in r.stderr:
        assert False, "RecursionError for 100,000 houses: replace the recursion by a loop over the houses."
    assert r.returncode == 0, "Your code crashed on 100,000 houses:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["11759729", "171426", "10000"], (
        f"Large inputs: expected 11759729 171426 10000, got {r.stdout.split()}.")
