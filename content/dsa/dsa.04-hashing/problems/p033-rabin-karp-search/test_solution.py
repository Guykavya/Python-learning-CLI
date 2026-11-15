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


def ask(t, p, timeout=10):
    return run(f"{t}\n{p}\n", timeout=timeout)


def expected_for(t, p):
    pos = [i for i in range(len(t) - len(p) + 1) if t[i:i + len(p)] == p]
    return [str(len(pos))] + ([" ".join(map(str, pos))] if pos else [])


@pytest.mark.parametrize("t, p, why", [
    ("abababa", "aba", "the example: overlapping matches at 0, 2, 4"),
    ("hello", "ll", "a match in the middle"),
    ("hello", "xyz", "no match: print 0 and an empty line"),
    ("aaaa", "aa", "overlaps: positions 0, 1, 2"),
    ("abc", "abc", "pattern equals the text"),
    ("abc", "c", "one-letter pattern at the end (the last window)"),
    ("abcabcabc", "abca", "partly overlapping"),
])
def test_examples(t, p, why):
    assert ask(t, p) == expected_for(t, p), (
        f"Text {t!r}, pattern {p!r}: expected {expected_for(t, p)} ({why}). Positions are 0-based; overlaps count.")


def test_random_small():
    rng = random.Random(35)
    for _ in range(60):
        t = "".join(rng.choice("ab") for _ in range(rng.randint(1, 14)))
        p = "".join(rng.choice("ab") for _ in range(rng.randint(1, min(4, len(t)))))
        assert ask(t, p) == expected_for(t, p), f"Text {t!r}, pattern {p!r}: expected {expected_for(t, p)}."


def test_large_random():
    rng = random.Random(36)
    t = "".join(rng.choice("ab") for _ in range(200000))
    p = t[777:777 + 18]
    assert ask(t, p) == expected_for(t, p), "Wrong or slow on 200000 letters."


def test_large_many_matches():
    t = "a" * 200000
    p = "a" * 100000
    assert ask(t, p) == expected_for(t, p), (
        "100001 overlapping matches. Slicing t[i:i+m] for every position copies 100000 letters each time; "
        "compare hashes first and verify only when they match.")
