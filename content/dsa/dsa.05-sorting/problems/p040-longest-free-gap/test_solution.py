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

def ask(t, ms, timeout=10):
    return run(f"{t} {len(ms)}\n" + "".join(f"{l} {r}\n" for l, r in ms), timeout=timeout)


def brute(t, ms):
    busy = [False] * t
    for l, r in ms:
        for x in range(l, r):
            busy[x] = True
    best = cur = 0
    for b in busy:
        cur = 0 if b else cur + 1
        best = max(best, cur)
    return best


@pytest.mark.parametrize("t, ms, why", [
    (20, [(2, 5), (4, 9), (12, 14)], "the example: the last gap 14..20 is the longest"),
    (10, [(0, 10)], "always busy: 0"),
    (10, [], "no meetings: the whole day is free"),
    (10, [(5, 6)], "gaps on both sides"),
    (10, [(0, 3), (3, 6), (6, 10)], "touching meetings leave no gap"),
    (30, [(1, 20), (2, 3), (4, 5), (25, 26)], "a long meeting covers the short ones: gap 20..25 is 5, last gap 26..30 is 4"),
    (12, [(8, 9), (1, 2), (4, 5)], "unsorted input"),
    (10, [(4, 5), (0, 1)], "gap before the first and after the last"),
])
def test_examples(t, ms, why):
    got = ask(t, ms)
    assert got == [str(brute(t, ms))], f"T={t}, {ms}: expected {brute(t, ms)}, got {got} ({why}). Keep the maximum end so far, and add the start and end gaps."


def test_random_small():
    rng = random.Random(51)
    for _ in range(100):
        t = rng.randint(1, 30)
        ms = []
        for _ in range(rng.randint(0, 6)):
            l = rng.randint(0, t - 1)
            ms.append((l, rng.randint(l + 1, min(t, l + 8))))
        assert ask(t, ms) == [str(brute(t, ms))], f"T={t}, {ms}: expected {brute(t, ms)}."


def test_large():
    rng = random.Random(52)
    T = 10**9
    ms = []
    for _ in range(200000):
        l = rng.randint(0, T - 3000)
        ms.append((l, l + rng.randint(1, 3000)))
    best, busy = 0, 0
    for l, r in sorted(ms):
        best = max(best, l - busy)
        busy = max(busy, r)
    best = max(best, T - busy)
    assert ask(T, ms) == [str(best)], "T = 10^9: do not allocate an array of size T, and sort 200000 meetings once."
