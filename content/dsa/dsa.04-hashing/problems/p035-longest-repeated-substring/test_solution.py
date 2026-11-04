import subprocess
import sys
from pathlib import Path

import pytest

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or a loop that does far more work than needed.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import random


def ask(s, timeout=10):
    return run(s + "\n", timeout=timeout)


def has_repeat(s, k):
    seen = set()
    for i in range(len(s) - k + 1):
        w = s[i:i + k]
        if w in seen:
            return True
        seen.add(w)
    return False


def brute(s):
    best = 0
    for k in range(1, len(s)):
        if has_repeat(s, k):
            best = k
    return best


@pytest.mark.parametrize("s, expected, why", [
    ("banana", 3, "the example: ana, overlapping"),
    ("abcd", 0, "no repeated letter"),
    ("a", 0, "a single letter"),
    ("aa", 1, "the letter a twice"),
    ("aaaaa", 4, "overlap: aaaa occurs at 0 and 1"),
    ("abcabcabc", 6, "abcabc at 0 and 3"),
    ("abab", 2, "ab twice"),
])
def test_examples(s, expected, why):
    assert ask(s) == [str(expected)], f"s={s!r}: expected {expected} ({why})."


def test_random_small():
    rng = random.Random(40)
    for _ in range(60):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(1, 14)))
        assert ask(s) == [str(brute(s))], f"s={s!r}: expected {brute(s)}."


def test_large_random():
    rng = random.Random(41)
    s = "".join(rng.choice("ab") for _ in range(50000))
    lo, hi = 0, len(s) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if has_repeat(s, mid):
            lo = mid
        else:
            hi = mid - 1
    assert ask(s) == [str(lo)], "n = 50000. Binary search the length and check each length in O(n) with a rolling hash."


def test_large_all_equal():
    s = "a" * 100000
    assert ask(s) == ["99999"], "All letters equal: the answer is n - 1. A hash with letter value 0 would go wrong; use a = 1."
