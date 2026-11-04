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


def ask(text, pattern, timeout=10):
    return run(f"{text}\n{pattern}\n", timeout=timeout)


def brute(text, pattern):
    m = len(pattern)
    key = sorted(pattern)
    return sum(1 for i in range(len(text) - m + 1) if sorted(text[i:i + m]) == key)


def by_weights(text, pattern, seed):
    """Give every letter a random big weight: equal weight sums mean equal letter counts (with near certainty)."""
    rng = random.Random(seed)
    w = {ch: rng.getrandbits(61) for ch in "abcdefghijklmnopqrstuvwxyz"}
    m = len(pattern)
    if m > len(text):
        return 0
    target = sum(w[ch] for ch in pattern)
    cur = sum(w[ch] for ch in text[:m])
    count = 1 if cur == target else 0
    for r in range(m, len(text)):
        cur += w[text[r]] - w[text[r - m]]
        if cur == target:
            count += 1
    return count


@pytest.mark.parametrize("text, pattern, expected, why", [
    ("cbaebabacd", "abc", 2, "the example: cba and bac"),
    ("abab", "ab", 3, "ab, ba, ab overlap: each window counts"),
    ("aaaa", "aa", 3, "three overlapping windows of aa"),
    ("ab", "abc", 0, "the pattern is longer than the text: 0, and no crash"),
    ("abc", "cba", 1, "text and pattern have the same length: one window"),
    ("a", "a", 1, "one letter each"),
    ("aab", "ab", 1, "only the window ab: the first window aa has the wrong counts"),
    ("baa", "aa", 1, "the window ba must lose its b when it slides: remove text[r - m]"),
    ("xyz", "aa", 0, "no window matches"),
    ("abcbca", "aabc", 0, "multiplicity matters: the pattern needs two a's and no window has them"),
    ("abcabc", "aabc", 1, "abca has two a's, one b, one c: it matches; the other windows do not"),
])
def test_examples(text, pattern, expected, why):
    got = ask(text, pattern)
    assert got == [str(expected)], f"text {text!r}, pattern {pattern!r}: expected {expected}, got {got} ({why})."


def test_random_small_against_brute_force():
    rng = random.Random(29)
    for _ in range(50):
        text = "".join(rng.choice("abc") for _ in range(rng.randint(1, 15)))
        pattern = "".join(rng.choice("abc") for _ in range(rng.randint(1, 4)))
        got = ask(text, pattern)
        expected = brute(text, pattern)
        assert got == [str(expected)], (
            f"text {text!r}, pattern {pattern!r}: expected {expected}, got {got}. Add text[r], remove text[r - m], "
            "and compare only when the window is full.")


def test_large_every_window():
    text = "ab" * 100000
    pattern = "a" * 500 + "b" * 500
    got = ask(text, pattern, timeout=10)
    expected = len(text) - len(pattern) + 1
    assert got == [str(expected)], (
        f"text 'abab...' (200000 letters), pattern of 500 a's and 500 b's: every window matches, so the answer "
        f"is {expected}; got {got}. A timeout means you count or sort every window from scratch.")


def test_large_random():
    rng = random.Random(2929)
    text = "".join(rng.choice("abc") for _ in range(200000))
    pattern = "".join(rng.choice("abc") for _ in range(30))
    expected = by_weights(text, pattern, 29)
    got = ask(text, pattern, timeout=10)
    assert got == [str(expected)], f"Large random text, pattern {pattern!r}: expected {expected}, got {got}."
