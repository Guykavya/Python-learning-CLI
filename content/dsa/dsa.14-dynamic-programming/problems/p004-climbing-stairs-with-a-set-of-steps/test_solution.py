import pathlib
import random
import subprocess
import sys

from solution import count_ways

HERE = pathlib.Path(__file__).parent


def brute(n, steps):
    """Try every possible first move (plain recursion, small n only)."""
    if n == 0:
        return 1
    return sum(brute(n - s, steps) for s in steps if s <= n)


def combinations(n, steps):
    """Order NOT mattering (coins outside): used only to explain a wrong answer."""
    f = [0] * (n + 1)
    f[0] = 1
    for s in steps:
        for a in range(s, n + 1):
            f[a] += f[a - s]
    return f[n]


def run_big(code, limit):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=limit, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_examples():
    assert count_ways(4, [1, 2]) == 5, "Steps [1, 2] are the ordinary staircase: 5 ways for n = 4."
    got = count_ways(5, [1, 3, 4])
    assert got != 3, (
        "count_ways(5, [1, 3, 4]) gave 3: that counts combinations (order ignored). Here 1+4 and 4+1 are "
        "different ways: put the loop over i outside and the loop over steps inside.")
    assert got == 6, f"count_ways(5, [1, 3, 4]) should be 6 (11111, 113, 131, 311, 14, 41), got {got}."


def test_impossible_and_empty():
    assert count_ways(0, [5, 9]) == 1, "n = 0: the empty sequence is one way. Base case f(0) = 1."
    assert count_ways(3, [5, 9]) == 0, "Every move is longer than 3: 0 ways. Skip steps with s > i."
    assert count_ways(7, [2]) == 0, "Only 2-steps cannot make 7: 0 ways."
    assert count_ways(8, [2]) == 1, "Only 2-steps make 8 in exactly one way."


def test_unsorted_steps():
    assert count_ways(6, [4, 1, 3]) == count_ways(6, [1, 3, 4]) == 9, (
        "The order of the steps list must not matter: count_ways(6, [1, 3, 4]) is 9.")


def test_random_against_recursion():
    rng = random.Random(1404)
    for _ in range(300):
        steps = rng.sample(range(1, 8), rng.randint(1, 4))
        n = rng.randint(0, 16)
        want = brute(n, steps)
        got = count_ways(n, list(steps))
        if got != want and got == combinations(n, steps):
            assert False, (
                f"n={n}, steps={steps}: you returned {got}, the number of combinations; sequences (order "
                f"matters) are {want}. Loop over i outside and over steps inside.")
        assert got == want, (
            f"n={n}, steps={steps}: expected {want} sequences (counted by recursion), got {got}. "
            "f(i) = sum of f(i - s) over steps s <= i, with f(0) = 1.")


def test_large_n():
    code = (
        "from solution import count_ways\n"
        "print(count_ways(10000, [1, 3, 4]))\n"
        "print(count_ways(10000, list(range(2, 60, 3))))\n"
        "print(count_ways(5000, [3, 7, 100, 10001]))\n"
        "print(count_ways(9999, [2]), count_ways(10000, [2]))\n"
    )
    r = run_big(code, 10)
    assert r is not None, (
        "Time limit (10 s) for n = 10**4: exponential: add a memo. Better, fill a table f[0..n] in a loop.")
    if "RecursionError" in r.stderr:
        assert False, (
            "RecursionError for n = 10**4: a recursion that deep fails even with a memo. Fill a table instead.")
    assert r.returncode == 0, "Your code crashed on large n:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["468833332", "787406028", "214649511", "0", "1"], (
        f"Large inputs: expected 468833332, 787406028, 214649511, 0, 1; got {r.stdout.split()}. "
        "Take % (10**9 + 7) and skip steps longer than i.")
