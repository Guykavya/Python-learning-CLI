import functools
import itertools
import pathlib
import random
import subprocess
import sys

from solution import count_strings

HERE = pathlib.Path(__file__).parent


def count_strings_memo(n, k):
    """The colleague's top-down version from problem.md."""
    @functools.cache
    def go(i, run):
        if i == 0:
            return 1
        total = go(i - 1, 0)
        if run + 1 < k:
            total += go(i - 1, run + 1)
        return total

    return go(n, 0)


def brute(n, k):
    """List every binary string of length n and check it."""
    bad = "1" * k
    return sum(1 for bits in itertools.product("01", repeat=n) if bad not in "".join(bits))


def run_big(code, limit):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=limit, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_examples():
    assert count_strings(4, 3) == 13, "Length 4, no '111': 16 - 3 = 13 strings."
    got = [count_strings(n, 2) for n in range(8)]
    assert got == [1, 2, 3, 5, 8, 13, 21, 34], (
        f"k = 2 should give 1, 2, 3, 5, 8, 13, 21, 34 for n = 0..7, got {got}. "
        "If everything is shifted, check the base row t[0][run] = 1 and that you return t[n][0].")


def test_edges():
    assert count_strings(0, 3) == 1, "n = 0: the empty string is one string. t[0][0] = 1."
    assert count_strings(5, 1) == 1, (
        "k = 1 forbids any 1, so only '00000' is left. Your table may have k columns (run = 0..k-1); "
        "a 1 may be placed only if run + 1 < k.")
    assert count_strings(3, 4) == 8, "k = 4 > n = 3: nothing is forbidden, all 8 strings count."


def test_against_brute_force():
    for n in range(0, 11):
        for k in range(1, 5):
            want = brute(n, k)
            got = count_strings(n, k)
            assert got == want, (
                f"count_strings({n}, {k}) = {got}, but listing all strings gives {want}. "
                "Compare each table cell with go(i, run) of the memo version.")


def test_against_memo_random():
    rng = random.Random(808)
    for _ in range(100):
        n, k = rng.randint(0, 60), rng.randint(1, 8)
        want = count_strings_memo(n, k)
        got = count_strings(n, k)
        assert got == want, (
            f"count_strings({n}, {k}) = {got}, the memo version gives {want}. Is the table "
            "(n + 1) x k, filled with i increasing, and is every row a separate list?")


def test_no_recursion_for_large_n():
    code = (
        "from solution import count_strings\n"
        "a = count_strings(5000, 10)\n"
        "b = count_strings(4000, 2)\n"
        "c = count_strings(3000, 50)\n"
        "print(a % 1000000007, a.bit_length(), b % 1000000007, c % 1000000007, count_strings(5000, 1))\n"
    )
    r = run_big(code, 15)
    assert r is not None, (
        "Time limit (15 s) for n = 5000: exponential: add a memo. A table of (n + 1) x k cells is filled "
        "once each; check that you are not recomputing rows.")
    if "RecursionError" in r.stderr:
        assert False, (
            "RecursionError for n = 5000: the solution is still recursive. The point of this problem is a "
            "table filled by loops, with no recursion at all.")
    assert r.returncode == 0, "Your code crashed for n = 5000:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["946877808", "4997", "524485014", "937178608", "1"], (
        f"Large inputs gave wrong counts: {r.stdout.split()} (shown modulo 10**9+7). Small cases may still "
        "pass if the table shape is wrong only for large k: make it (n + 1) rows of k columns.")
