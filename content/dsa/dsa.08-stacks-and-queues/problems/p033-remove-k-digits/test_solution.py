import itertools
import random

import pytest

from solution import remove_k_digits


def slow(num, k):
    keep = len(num) - k
    best = None
    for idx in itertools.combinations(range(len(num)), keep):
        value = int("".join(num[i] for i in idx)) if idx else 0
        if best is None or value < best:
            best = value
    return str(best)


@pytest.mark.parametrize("num, k, want, why", [
    ("1432219", 3, "1219", "the chapter example"),
    ("10200", 1, "200", "leading zeros must be stripped"),
    ("10", 2, "0", "everything removed: return '0', not ''"),
    ("9", 1, "0", "one digit removed"),
    ("112", 1, "11", "the digits never decrease: removals are left after the scan, take them from the end"),
    ("12345", 0, "12345", "k = 0: nothing to remove (careful: stack[:-0] is empty)"),
    ("12345", 2, "123", "increasing: remove the last two"),
    ("54321", 2, "321", "decreasing: remove the first two"),
    ("100", 1, "0", "removing the 1 leaves '00', which is 0"),
    ("1111", 2, "11", "equal digits: do not pop on equality"),
    ("1234567890", 9, "0", "nine removals keep the 0"),
    ("0", 0, "0", "zero stays zero"),
])
def test_cases(num, k, want, why):
    got = remove_k_digits(num, k)
    assert got == want, f"remove_k_digits({num!r}, {k}) should be {want!r}, got {got!r}: {why}."


def test_random_against_brute_force():
    rng = random.Random(33)
    for _ in range(1000):
        n = rng.randint(1, 9)
        num = str(rng.randint(1, 9)) + "".join(rng.choice("0123456789" if rng.random() < 0.5 else "0019")
                                               for _ in range(n - 1))
        k = rng.randint(0, n)
        assert remove_k_digits(num, k) == slow(num, k), f"remove_k_digits({num!r}, {k}) should be {slow(num, k)!r}."


def test_long():
    num = "9" * 50000 + "1" * 50000
    assert remove_k_digits(num, 50000) == "1" * 50000, "Removing the 50,000 nines leaves 50,000 ones."
