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


def brute(s):
    for i, ch in enumerate(s):
        if s.count(ch) == 1:
            return i
    return -1


@pytest.mark.parametrize("s, expected, why", [
    ("loveleetcode", 2, "the example: v is the first letter that appears once"),
    ("leetcode", 0, "l appears once and is first"),
    ("aabb", -1, "every letter repeats"),
    ("z", 0, "a single letter"),
    ("aabbc", 4, "the unique letter is last"),
    ("abcabcd", 6, "only d is unique; a, b, c repeat"),
    ("aab", 2, "unique letter after a repeated one"),
])
def test_examples(s, expected, why):
    assert ask(s) == [str(expected)], f"Input {s!r}: expected {expected} ({why}). Print the INDEX, 0-based."


def test_random_small():
    rng = random.Random(6)
    for _ in range(40):
        s = "".join(rng.choice("abcde") for _ in range(rng.randint(1, 12)))
        assert ask(s) == [str(brute(s))], f"Input {s!r}: expected {brute(s)}."


def test_large():
    s = "a" * 100000 + "b" * 99999 + "c"
    assert ask(s) == ["199999"], (
        "Large input. Count once, scan once. A s.count(ch) inside the scan re-reads the string for every index.")
