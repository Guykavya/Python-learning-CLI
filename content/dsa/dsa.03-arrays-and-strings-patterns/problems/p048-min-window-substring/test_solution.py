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


def ask(s, t, timeout=10):
    return run(f"{s}\n{t}\n", timeout=timeout)


def covers(window, need):
    have = {}
    for ch in window:
        have[ch] = have.get(ch, 0) + 1
    return all(have.get(ch, 0) >= k for ch, k in need.items())


def brute(s, t):
    need = {}
    for ch in t:
        need[ch] = need.get(ch, 0) + 1
    for length in range(1, len(s) + 1):
        for i in range(len(s) - length + 1):
            if covers(s[i:i + length], need):
                return s[i:i + length]
    return "-1"


def by_binary_search(s, t):
    """Independent check: binary search the length; test each length with a FIXED window."""
    need = {}
    for ch in t:
        need[ch] = need.get(ch, 0) + 1

    def first_start(L):
        have = {}
        short = len(need)          # number of distinct letters still below their need
        for i, ch in enumerate(s):
            have[ch] = have.get(ch, 0) + 1
            if have[ch] == need.get(ch, -1):
                short -= 1
            if i >= L:
                out = s[i - L]
                if have[out] == need.get(out, -1):
                    short += 1
                have[out] -= 1
            if i >= L - 1 and short == 0:
                return i - L + 1
        return -1

    lo, hi = len(t), len(s)
    if hi < lo or first_start(hi) == -1:
        return "-1"
    while lo < hi:
        mid = (lo + hi) // 2
        if first_start(mid) != -1:
            hi = mid
        else:
            lo = mid + 1
    st = first_start(lo)
    return s[st:st + lo]


@pytest.mark.parametrize("s, t, want, why", [
    ("ADOBECODEBANC", "ABC", "BANC", "the example"),
    ("a", "a", "a", "the whole string"),
    ("abc", "d", "-1", "t has a letter that s does not have"),
    ("a", "aa", "-1", "s has the letter, but not enough copies"),
    ("abca", "aa", "abca", "multiplicity: two a's needed, so the window must reach the second a"),
    ("aAbB", "AB", "AbB", "case-sensitive: 'A' and 'a' differ"),
    ("xyzabc", "cba", "abc", "the order of t does not matter"),
    ("abcdebdde", "bde", "deb", "'deb' and 'ebd' both have length 3; 'deb' starts first"),
])
def test_examples(s, t, want, why):
    got = ask(s, t)
    assert got == [want], f"s = {s!r}, t = {t!r}: expected {want!r}, got {got} ({why})."


@pytest.mark.parametrize("s, t, want", [
    ("baXab", "ab", "ba"),
    ("cabxxxbac", "abc", "cab"),
    ("aXbYa", "a", "a"),
])
def test_tie_earliest(s, t, want):
    got = ask(s, t)
    assert got == [want], (
        f"s = {s!r}, t = {t!r}: expected {want!r}, got {got}. Several shortest windows exist; keep the earliest. "
        "Replace the best only when the new window is strictly shorter (`<`, not `<=`).")


def test_shrink_fully():
    got = ask("aaaaab", "ab")
    assert got == ["ab"], (
        f"Expected 'ab', got {got}. Once the window is good, keep shrinking from the left WHILE it stays good, "
        "and record each good window; stopping after one step leaves extra a's in it.")


def test_extra_copies_are_not_missing():
    got = ask("aaflslflsldkalskaaa", "aaa")
    assert got == ["aaa"], (
        f"Expected 'aaa', got {got}. Count a character as 'found' only while the window has no more of it than "
        "t needs; extra copies must not reduce the missing count.")


def test_random_small_against_brute_force():
    rng = random.Random(48)
    for _ in range(30):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(1, 15)))
        t = "".join(rng.choice("abc") for _ in range(rng.randint(1, 4)))
        got = ask(s, t)
        assert got == [brute(s, t)], f"s = {s!r}, t = {t!r}: expected {brute(s, t)!r}, got {got}."


def test_large_needle_at_the_end():
    s = "a" * 199999 + "b"
    got = ask(s, "ab", timeout=8)
    assert got == ["ab"], (
        f"Expected 'ab', got {got[:1]}. If it timed out, you extend a new window from every start (O(n^2)); "
        "the left end must only move forward.")


def test_large_random():
    rng = random.Random(4800)
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    s = "".join(rng.choice(letters) for _ in range(200000))
    t = "".join(rng.choice(letters) for _ in range(60))
    want = by_binary_search(s, t)
    got = ask(s, t, timeout=8)
    assert got == [want], f"Random s of length 200000, t of length 60: expected a window of length {len(want)}, got {got[:1]}."


def test_large_impossible():
    s = "ab" * 100000
    got = ask(s, "abc", timeout=8)
    assert got == ["-1"], f"s has no 'c' at all: expected -1, got {got[:1]}."
