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
import string


def brute(s):
    best = ""
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            if len(set(s[i:j])) == j - i and j - i > len(best):
                best = s[i:j]
    return [str(len(best)), best]


def by_last_index(s):
    last = {}
    l = 0
    best_len, best_start = 0, 0
    for r, ch in enumerate(s):
        if ch in last and last[ch] >= l:
            l = last[ch] + 1
        last[ch] = r
        if r - l + 1 > best_len:
            best_len, best_start = r - l + 1, l
    return [str(best_len), s[best_start:best_start + best_len]]


@pytest.mark.parametrize("s, expected, why", [
    ("pwwkew", ["3", "wke"], "the example: wke and kew tie, the earlier one wins"),
    ("abcabcbb", ["3", "abc"], "abc, bca, cab all have length 3: print the first"),
    ("bbbbb", ["1", "b"], "all the same character"),
    ("a", ["1", "a"], "one character"),
    ("dvdf", ["3", "vdf"], "do not restart at the repeat: drop only up to the OLD d, keep v"),
    ("abba", ["2", "ab"], "with the last-index trick, l must never move backwards (use max)"),
    ("abcdef", ["6", "abcdef"], "no repeats: the whole string"),
    ("tmmzuxt", ["5", "mzuxt"], "the second t is fine: the first t already left the window"),
    ("aab", ["2", "ab"], "the window must shrink past the first a"),
    ("a!b?a#", ["5", "!b?a#"], "signs are characters too"),
    ("AaBbAa", ["4", "AaBb"], "upper and lower case are different characters"),
])
def test_examples(s, expected, why):
    got = run(s + "\n")
    assert got == expected, f"Input {s!r}: expected {expected}, got {got} ({why})."


def test_random_small_against_brute_force():
    rng = random.Random(27)
    for _ in range(60):
        s = "".join(rng.choice("abcd") for _ in range(rng.randint(1, 14)))
        got = run(s + "\n")
        expected = brute(s)
        assert got == expected, (
            f"Input {s!r}: expected {expected}, got {got}. Print the length, then the EARLIEST longest substring "
            "with no repeated character (update the best only when strictly longer).")


def test_large_random():
    rng = random.Random(2727)
    alphabet = string.ascii_letters + string.digits
    s = "".join(rng.choice(alphabet) for _ in range(200000))
    expected = by_last_index(s)
    got = run(s + "\n", timeout=10)
    assert got == expected, (
        f"Large random string: expected length {expected[0]} ({expected[1]!r}), got {got[:1]}. A timeout "
        "means you look at many substrings: keep one window and move l only forward.")


def test_large_repeating_pattern():
    s = string.ascii_lowercase * 7000 + "!"
    expected = ["27", string.ascii_lowercase + "!"]
    got = run(s + "\n", timeout=10)
    assert got == expected, (
        f"The alphabet repeated 7000 times, then '!': every earlier window stops at 26 letters, and only the last "
        f"copy of the alphabet plus '!' reaches 27. Expected {expected}, got {got}.")
