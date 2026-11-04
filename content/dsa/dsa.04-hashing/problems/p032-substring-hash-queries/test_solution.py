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

B = 131
M = 1_000_000_007


def ask(s, queries, timeout=10):
    text = s + "\n" + str(len(queries)) + "\n" + "\n".join(f"{l} {r}" for l, r in queries) + "\n"
    return run(text, timeout=timeout)


def H(t):
    h = 0
    for ch in t:
        h = (h * B + ord(ch) - 96) % M
    return h


def expected_for(s, queries):
    return [str(H(s[l - 1:r])) for l, r in queries]


def test_hand_checked_values():
    # H("a") = 1, H("ab") = 1*131 + 2 = 133, H("abc") = 133*131 + 3 = 17426
    got = ask("abc", [(1, 1), (1, 2), (1, 3), (2, 3)])
    assert got == ["1", "133", "17426", str(2 * 131 + 3)], (
        f"Got {got}. By hand: H('a') = 1, H('ab') = 1*131 + 2 = 133, H('abc') = 133*131 + 3 = 17426, H('bc') = 2*131 + 3 = 265.")


def test_equal_substrings_equal_hashes():
    got = ask("abcab", [(1, 2), (4, 5)])
    assert got[0] == got[1] == "133", f"Got {got}. 'ab' at 1-2 and at 4-5 must hash to the same value, 133."


def test_all_substrings_small():
    rng = random.Random(33)
    for _ in range(20):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(1, 10)))
        queries = [(l, r) for l in range(1, len(s) + 1) for r in range(l, len(s) + 1)]
        got = ask(s, queries)
        assert got == expected_for(s, queries), (
            f"s={s!r}: some substring hash is wrong. Remove the first l-1 letters by subtracting P[l-1] * B^(r-l+1), "
            "and keep the result non-negative with % M.")


def test_long_values_need_mod():
    s = "z" * 50
    got = ask(s, [(1, 50)])
    assert got == [str(H(s))], f"Got {got}, expected {H(s)}. Take % M after every step: the numbers must stay below M."


def test_large():
    rng = random.Random(34)
    n = 200000
    s = "".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(n))
    queries = []
    for _ in range(200000):
        l = rng.randint(1, n)
        r = rng.randint(l, n)
        queries.append((l, r))
    P, pw = [0], [1]
    for ch in s:
        P.append((P[-1] * B + ord(ch) - 96) % M)
        pw.append(pw[-1] * B % M)
    expected = [str((P[r] - P[l - 1] * pw[r - l + 1]) % M) for l, r in queries]
    assert ask(s, queries) == expected, "Wrong or too slow with 200000 queries on a 200000-letter string: one O(1) formula per query."
