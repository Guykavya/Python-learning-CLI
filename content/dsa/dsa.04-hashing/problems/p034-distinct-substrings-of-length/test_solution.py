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


def ask(s, L, timeout=10):
    return run(f"{s}\n{L}\n", timeout=timeout)


def brute(s, L):
    return len({s[i:i + L] for i in range(len(s) - L + 1)})


@pytest.mark.parametrize("s, L, why", [
    ("abcabcab", 3, "the example"),
    ("aaaa", 2, "one distinct substring"),
    ("abcd", 4, "L = n: one window"),
    ("abcd", 1, "L = 1: distinct letters"),
    ("abab", 2, "ab, ba, ab: two distinct"),
    ("zzzzzzzz", 5, "all equal"),
])
def test_examples(s, L, why):
    assert ask(s, L) == [str(brute(s, L))], f"s={s!r}, L={L}: expected {brute(s, L)} ({why})."


def test_random_small():
    rng = random.Random(37)
    for _ in range(50):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(1, 14)))
        L = rng.randint(1, len(s))
        assert ask(s, L) == [str(brute(s, L))], f"s={s!r}, L={L}: expected {brute(s, L)}."


def test_large_short_windows():
    rng = random.Random(38)
    s = "".join(rng.choice("ab") for _ in range(200000))
    assert ask(s, 12) == [str(brute(s, 12))], "n = 200000, L = 12: hash each window in O(1)."


def test_large_long_windows():
    rng = random.Random(39)
    s = "".join(rng.choice("abcdefghij") for _ in range(100000))
    assert ask(s, 3000) == [str(brute(s, 3000))], (
        "n = 100000, L = 3000. Slicing makes a 3000-letter string for each of 97001 windows; "
        "a rolling hash changes the hash with O(1) work per window.")
