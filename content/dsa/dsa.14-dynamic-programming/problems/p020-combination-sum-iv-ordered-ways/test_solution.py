import pathlib
import random
import subprocess
import sys

from solution import ordered_ways

HERE = pathlib.Path(__file__).parent


def brute(nums, target):
    """Try every possible next number (small inputs only). Order matters, so every sequence is counted."""
    if target == 0:
        return 1
    return sum(brute(nums, target - x) for x in nums if x <= target)


def combinations(nums, target):
    """Order does NOT matter here (numbers outside): used only to explain a wrong answer."""
    f = [0] * (target + 1)
    f[0] = 1
    for x in nums:
        for a in range(x, target + 1):
            f[a] += f[a - x]
    return f[target]


def run_big(code, limit):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=limit, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_loop_order():
    got = ordered_ways([1, 2, 3], 4)
    assert got != 4, (
        "ordered_ways([1, 2, 3], 4) gave 4: that counts COMBINATIONS (p018). Here 1+3 and 3+1 are two "
        "different sequences. Put the loop over amounts OUTSIDE and the loop over numbers inside.")
    assert got == 7, f"Expected 7 (1111, 112, 121, 211, 22, 13, 31), got {got}."
    assert ordered_ways([1, 2], 10) == 89, (
        "With [1, 2] the counts are the Fibonacci numbers: f[10] = 89. Split on the LAST number.")
    assert ordered_ways([4, 6], 30) == 28, (
        "[4, 6] and 30: six 4s + one 6 (7 orders), three 4s + three 6s (20 orders), five 6s (1 order): 28.")


def test_edges():
    assert ordered_ways([9], 3) == 0, "9 is bigger than 3: no sequence, 0."
    assert ordered_ways([5], 0) == 1, "Target 0: one sequence, the empty one. f[0] = 1."
    assert ordered_ways([2], 7) == 0, "Only 2s cannot make an odd number."
    assert ordered_ways([3], 9) == 1, "Only 3 + 3 + 3: one sequence."


def test_order_of_nums_does_not_matter():
    assert ordered_ways([3, 1, 2], 4) == ordered_ways([1, 2, 3], 4) == 7, (
        "The order of the nums list must not change the count.")


def test_random_against_brute_force():
    rng = random.Random(2020)
    for _ in range(300):
        nums = rng.sample(range(1, 9), rng.randint(1, 4))
        target = rng.randint(0, 18)
        want = brute(nums, target)
        got = ordered_ways(list(nums), target)
        if got != want and got == combinations(nums, target):
            assert False, (
                f"nums={nums}, target={target}: you returned {got}, the number of COMBINATIONS; sequences "
                f"are {want}. Swap the loops: amounts outside, numbers inside.")
        assert got == want, (
            f"nums={nums}, target={target}: expected {want} sequences, got {got}. "
            "f[0] = 1; for a from 1 up: f[a] = sum of f[a - x] for every x <= a.")


def test_large_targets():
    code = (
        "from solution import ordered_ways\n"
        "x = ordered_ways([3, 7, 13, 101], 10000)\n"
        "y = ordered_ways([1, 2, 5, 10, 20, 50, 100, 200], 5000)\n"
        "print(len(str(x)), x % 1000003, len(str(y)), y % 1000003)\n"
        "print(ordered_ways([2], 9999), ordered_ways([1], 10000))\n"
    )
    r = run_big(code, 15)
    assert r is not None, (
        "Time limit (15 s) for targets up to 10**4: without a memo or table the count is exponential. "
        "A table needs only target * len(nums) steps.")
    if "RecursionError" in r.stderr:
        assert False, (
            "RecursionError for target 10**4: a memoised recursion goes too deep. Fill f[0..target] bottom-up.")
    assert r.returncode == 0, "Your code crashed on a large target:\n" + r.stderr[-800:]
    want = ["750", "170006", "1165", "348478", "0", "1"]
    assert r.stdout.split() == want, (
        "Large targets: the counts are huge exact integers (750 and 1165 digits). Do not take a modulus "
        f"and do not use floats. Expected (digits, value mod 1000003) {want}, got {r.stdout.split()}.")
