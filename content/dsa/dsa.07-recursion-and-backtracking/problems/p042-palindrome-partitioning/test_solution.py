import random

import pytest

from solution import palindrome_partitions


def brute(s):
    """Try every set of cut positions with a bit mask."""
    out = []
    n = len(s)
    if n == 0:
        return [[]]
    for mask in range(1 << (n - 1)):
        pieces, start = [], 0
        for i in range(1, n):
            if mask >> (i - 1) & 1:
                pieces.append(s[start:i])
                start = i
        pieces.append(s[start:])
        if all(p == p[::-1] for p in pieces):
            out.append(pieces)
    return sorted(out)


@pytest.mark.parametrize("s, want, why", [
    ("aab", [["a", "a", "b"], ["aa", "b"]], "the example"),
    ("a", [["a"]], "a single letter"),
    ("", [[]], "the empty string has one partition with no pieces"),
    ("ab", [["a", "b"]], "'ab' is not a palindrome, so it must be cut"),
    ("aba", [["a", "b", "a"], ["aba"]], "the whole string is a palindrome too"),
    ("aaa", [["a", "a", "a"], ["a", "aa"], ["aa", "a"], ["aaa"]], "all letters equal: 2^(3-1) = 4 ways"),
])
def test_cases(s, want, why):
    got = sorted(palindrome_partitions(s))
    assert got == sorted(want), (
        f"palindrome_partitions({s!r}) should be {sorted(want)} ({why}), got {got}. "
        "If nothing is found, check that the loop's end goes up to len(s) inclusive.")


def test_racecar():
    got = sorted(palindrome_partitions("racecar"))
    assert got == brute("racecar"), f"'racecar' has {len(brute('racecar'))} palindrome partitions."


def test_all_equal_count():
    assert len(palindrome_partitions("a" * 10)) == 512, "Ten equal letters: every one of the 9 gaps may be cut or not, 2^9 = 512."


def test_random_against_brute_force():
    rng = random.Random(42)
    for _ in range(60):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(1, 9)))
        assert sorted(palindrome_partitions(s)) == brute(s), f"palindrome_partitions({s!r}) should be {brute(s)}."
