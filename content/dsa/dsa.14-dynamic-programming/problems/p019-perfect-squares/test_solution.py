import math
import pathlib
import subprocess
import sys

from solution import num_squares

HERE = pathlib.Path(__file__).parent


def by_number_theory(n):
    """An independent oracle (no DP): Lagrange and Legendre's theorems on sums of squares."""
    r = math.isqrt(n)
    if r * r == n:
        return 1
    for a in range(1, r + 1):
        b = n - a * a
        q = math.isqrt(b)
        if q * q == b:
            return 2
    m = n
    while m % 4 == 0:
        m //= 4
    return 4 if m % 8 == 7 else 3


def brute(n):
    """Try every last square (plain recursion, small n only)."""
    if n == 0:
        return 0
    best = n
    k = 1
    while k * k <= n:
        best = min(best, 1 + brute(n - k * k))
        k += 1
    return best


def run_big(code, limit):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=limit, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_examples():
    got = num_squares(12)
    assert got != 4, (
        "num_squares(12) gave 4: that is greedy (9 + 1 + 1 + 1). 4 + 4 + 4 uses 3. "
        "Try every square as the last one and keep the minimum.")
    assert got == 3, f"Expected 3 (4 + 4 + 4), got {got}."
    assert num_squares(13) == 2, "Expected 2 (4 + 9)."
    assert num_squares(7) == 4, "Expected 4 (4 + 1 + 1 + 1): 7 needs four squares."


def test_squares_themselves():
    for k in range(1, 30):
        assert num_squares(k * k) == 1, f"{k * k} is a square: 1. Include k*k = n in the list of squares."


def test_small_against_recursion():
    for n in range(1, 31):
        want = brute(n)
        got = num_squares(n)
        assert got == want, (
            f"num_squares({n}) = {got}, trying every square gives {want}. "
            "f(a) = 1 + min(f(a - s)) over squares s <= a, f(0) = 0.")


def test_against_number_theory():
    for n in list(range(31, 400)) + [1000, 4095, 5000]:
        want = by_number_theory(n)
        got = num_squares(n)
        assert got == want, f"num_squares({n}) = {got}, expected {want}. Is the table of size n + 1?"


def test_not_exponential():
    code = "from solution import num_squares\nprint(num_squares(300))\n"
    r = run_big(code, 5)
    assert r is not None, (
        "Time limit (5 s) for n = 300: exponential: add a memo. A table of f(0..n) computes each amount once.")
    assert r.returncode == 0, "Your code crashed on n = 300:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["3"], f"num_squares(300) should be 3 (100 + 100 + 100), got {r.stdout.split()}."


def test_large_n():
    code = (
        "from solution import num_squares\n"
        "print(*[num_squares(n) for n in (10000, 9999, 9998, 7999, 9997)])\n"
    )
    r = run_big(code, 15)
    assert r is not None, "Time limit (15 s) for n = 10**4: fill one table, about n * sqrt(n) steps."
    if "RecursionError" in r.stderr:
        assert False, (
            "RecursionError for n = 10**4: a memoised recursion that goes down by 1 is 10,000 calls deep. "
            "Fill a table from 1 up to n.")
    assert r.returncode == 0, "Your code crashed on n = 10**4:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["1", "4", "3", "4", "2"], (
        f"Large n: expected 1 4 3 4 2 for 10000, 9999, 9998, 7999, 9997; got {r.stdout.split()}.")
