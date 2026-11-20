import pathlib
import random
import subprocess
import sys

from solution import rob_circle

HERE = pathlib.Path(__file__).parent


def brute(nums):
    """Try every subset of houses; keep those with no two neighbours on the circle."""
    n = len(nums)
    best = 0
    for mask in range(1 << n):
        ok = True
        for i in range(n):
            j = (i + 1) % n
            if j != i and mask >> i & 1 and mask >> j & 1:
                ok = False
                break
        if ok:
            best = max(best, sum(nums[i] for i in range(n) if mask >> i & 1))
    return best


def row_answer(nums):
    """The p011 answer, ignoring the circle: used only to explain a wrong answer."""
    prev2, prev1 = 0, 0
    for money in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + money)
    return prev1


def run_big(code, limit):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=limit, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_examples():
    got = rob_circle([2, 3, 2])
    assert got != 4, (
        "rob_circle([2, 3, 2]) gave 4: you robbed the first and the last house, which are neighbours on a "
        "circle. Solve the row without the last house and the row without the first house.")
    assert got == 3, f"rob_circle([2, 3, 2]) should be 3, got {got}."
    assert rob_circle([1, 2, 3, 1]) == 4, "Expected 4 (1 + 3)."
    assert rob_circle([2, 7, 9, 3, 1]) == 11, (
        "Expected 11 (2 + 9). 2 + 9 + 1 = 12 is not allowed: the houses with 1 and 2 touch on the circle.")


def test_tiny_circles():
    assert rob_circle([5]) == 5, (
        "One house has no neighbour: rob it. Both rows nums[:-1] and nums[1:] are empty when n = 1, so treat "
        "n = 1 on its own.")
    assert rob_circle([5, 9]) == 9, "Two houses are neighbours: take the richer."
    assert rob_circle([4, 1, 4]) == 4, "Three houses on a circle are all neighbours: take one."
    assert rob_circle([0, 0, 0, 0]) == 0, "All empty: 0."


def test_random_against_brute_force():
    rng = random.Random(1212)
    for _ in range(300):
        nums = [rng.randint(0, 15) for _ in range(rng.randint(1, 11))]
        want = brute(nums)
        got = rob_circle(list(nums))
        if got != want and got == row_answer(nums):
            assert False, (
                f"nums={nums}: you returned {got}, the answer for a ROW. On a circle the first and last house "
                f"are neighbours: the answer is {want}.")
        assert got == want, (
            f"nums={nums}: expected {want} (all valid sets on the circle), got {got}. "
            "Take the max of the row without the last house and the row without the first house.")


def test_large_input():
    code = (
        "import random\n"
        "from solution import rob_circle\n"
        "rng = random.Random(1212)\n"
        "d = [rng.randint(0, 400) for _ in range(10**5)]\n"
        "b = [i % 7 for i in range(10**5)]\n"
        "print(rob_circle(d), rob_circle(b), rob_circle([5] * 99999), rob_circle([5] * 100000))\n"
    )
    r = run_big(code, 10)
    assert r is not None, (
        "Time limit (10 s) for 100,000 houses: exponential: add a memo. Two linear passes are enough.")
    if "RecursionError" in r.stderr:
        assert False, "RecursionError for 100,000 houses: use a loop over the houses, not recursion."
    assert r.returncode == 0, "Your code crashed on 100,000 houses:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["11709945", "171426", "249995", "250000"], (
        f"Large inputs: expected 11709945 171426 249995 250000, got {r.stdout.split()}. "
        "[5] * 99999 is an odd circle: at most 49999 houses can be robbed.")
