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

from itertools import combinations


def ask(bs, timeout=10):
    return run(f"{len(bs)}\n" + "".join(f"{a} {b}\n" for a, b in bs), timeout=timeout)


def brute(bs):
    if not bs:
        return 0
    pts = sorted({p for b in bs for p in b})
    for k in range(1, len(bs) + 1):
        for chosen in combinations(pts, k):
            if all(any(a <= x <= b for x in chosen) for a, b in bs):
                return k


@pytest.mark.parametrize("bs, why", [
    ([(10, 16), (2, 8), (1, 6), (7, 12)], "the example: 2 arrows"),
    ([(1, 2), (2, 3)], "touching balloons: one arrow at 2"),
    ([], "no balloons: 0"),
    ([(5, 5)], "one balloon of width 0"),
    ([(1, 2), (3, 4), (5, 6)], "disjoint: one arrow each"),
    ([(-5, -1), (-3, 2), (1, 4)], "negative coordinates"),
    ([(1, 100), (2, 3), (50, 60)], "a long balloon covering two small ones: 2 arrows"),
])
def test_examples(bs, why):
    got = ask(bs)
    assert got == [str(brute(bs))], f"Input {bs}: expected {brute(bs)}, got {got} ({why}). Sort by right end; a new arrow is needed when xs > last arrow."


def test_random_small():
    rng = random.Random(40)
    for _ in range(100):
        bs = []
        for _ in range(rng.randint(0, 7)):
            a = rng.randint(-5, 10)
            bs.append((a, a + rng.randint(0, 5)))
        assert ask(bs) == [str(brute(bs))], f"Input {bs}: expected {brute(bs)}."


def test_large():
    rng = random.Random(41)
    bs = []
    for _ in range(200000):
        a = rng.randint(-10**9, 10**9 - 5000)
        bs.append((a, a + rng.randint(0, 5000)))
    arrows, last = 0, -10**18
    for a, b in sorted(bs, key=lambda x: x[1]):
        if a > last:
            arrows += 1
            last = b
    assert ask(bs) == [str(arrows)], "Wrong or too slow on 200000 balloons."
