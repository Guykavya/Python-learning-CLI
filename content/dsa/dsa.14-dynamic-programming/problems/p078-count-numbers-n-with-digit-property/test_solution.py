import pathlib
import random
import subprocess
import sys

from solution import count_stepping

HERE = pathlib.Path(__file__).parent


def is_stepping(x):
    s = str(x)
    return all(abs(int(a) - int(b)) == 1 for a, b in zip(s, s[1:]))


def brute(lo, hi):
    """Check every number in the range (small ranges only)."""
    return sum(1 for x in range(lo, hi + 1) if is_stepping(x))


def test_examples():
    assert count_stepping(0, 21) == 13, (
        "Expected 13 in [0, 21]: 0..9, 10, 12, 21. If you got much less, leading zeros are being treated as "
        "digits (7 written as 007): add the 'started' flag.")
    assert count_stepping(10, 15) == 2, "Expected 2 in [10, 15]: 10 and 12."
    assert count_stepping(90, 101) == 2, "Expected 2 in [90, 101]: 98 and 101."


def test_zero_counts():
    assert count_stepping(0, 0) == 1, (
        "0 is a single digit, so it is a stepping number: count_stepping(0, 0) is 1. A DP that returns "
        "1 only if 'started' misses it.")
    assert count_stepping(0, 9) == 10, "Every single digit 0..9 is a stepping number: 10."


def test_range_ends_are_included():
    assert count_stepping(12, 12) == 1, (
        "12 alone is a stepping number: count_stepping(12, 12) must be 1. Subtract upto(lo - 1), not upto(lo).")
    assert count_stepping(11, 11) == 0, "11 is not a stepping number (the digits differ by 0)."
    assert count_stepping(1, 100) == 26, "Expected 26 in [1, 100]: 1..9, then 17 two-digit numbers."


def test_random_against_brute_force():
    rng = random.Random(7878)
    for _ in range(200):
        lo = rng.randint(0, 10**5)
        hi = rng.randint(lo, min(lo + rng.choice([10, 1000, 10**5]), 10**5))
        want = brute(lo, hi)
        got = count_stepping(lo, hi)
        assert got == want, (
            f"count_stepping({lo}, {hi}): expected {want} (every number checked), got {got}. State: "
            "(pos, prev, tight, started); answer upto(hi) - upto(lo - 1).")


def test_huge_ranges():
    code = (
        "from solution import count_stepping\n"
        "print(count_stepping(0, 10**18), count_stepping(1, 10**18), count_stepping(10**17, 10**18),\n"
        "      count_stepping(123456789012345678, 987654321098765432))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) for ranges up to 10**18: checking every number is impossible. With a memo the "
        "digit DP has under 1,000 states.")
    assert r.returncode == 0, "Your code crashed on a huge range:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["1143889", "1143888", "547810", "480312"], (
        f"Huge ranges: expected 1143889 1143888 547810 480312, got {r.stdout.split()}.")
