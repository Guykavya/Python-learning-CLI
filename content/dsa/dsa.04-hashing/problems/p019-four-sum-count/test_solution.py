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


def ask(A, B, C, D, timeout=10):
    return run(f"{len(A)}\n" + "\n".join(" ".join(map(str, L)) for L in (A, B, C, D)) + "\n", timeout=timeout)


def brute(A, B, C, D):
    return sum(1 for a in A for b in B for c in C for d in D if a + b + c + d == 0)


@pytest.mark.parametrize("A, B, C, D, expected, why", [
    ([1, 2], [-2, -1], [-1, 2], [0, 2], 2, "the example"),
    ([0], [0], [0], [0], 1, "all zeros: one quadruple"),
    ([1], [1], [1], [1], 0, "no way to reach 0"),
    ([0, 0], [0, 0], [0, 0], [0, 0], 16, "all zeros, n = 2: 2^4 quadruples"),
    ([1, 1], [-1, -1], [0, 0], [0, 0], 16, "many equal sums must all be counted"),
])
def test_examples(A, B, C, D, expected, why):
    assert ask(A, B, C, D) == [str(expected)], (
        f"Lists {A} {B} {C} {D}: expected {expected} ({why}). Count HOW MANY pairs give each sum, not just whether one exists.")


def test_random_small():
    rng = random.Random(22)
    for _ in range(30):
        n = rng.randint(1, 5)
        L = [[rng.randint(-3, 3) for _ in range(n)] for _ in range(4)]
        assert ask(*L) == [str(brute(*L))], f"Lists {L}: expected {brute(*L)}."


def test_large():
    rng = random.Random(23)
    n = 500
    L = [[rng.randint(-50, 50) for _ in range(n)] for _ in range(4)]
    pair = {}
    for a in L[0]:
        for b in L[1]:
            pair[a + b] = pair.get(a + b, 0) + 1
    expected = sum(pair.get(-(c + d), 0) for c in L[2] for d in L[3])
    assert ask(*L) == [str(expected)], "n = 500: four nested loops are 6 * 10^10 steps. Use a dictionary of pair sums."
