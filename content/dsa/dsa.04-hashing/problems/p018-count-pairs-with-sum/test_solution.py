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


def ask(a, k, timeout=10):
    return run(f"{len(a)} {k}\n" + " ".join(map(str, a)) + "\n", timeout=timeout)


def brute(a, k):
    return sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] + a[j] == k)


@pytest.mark.parametrize("a, k, expected, why", [
    ([1, 5, 3, 3, 3], 6, 4, "the example: 1+5 and three pairs of 3s"),
    ([3, 3, 3], 6, 3, "three equal values: choose 2 of 3 positions"),
    ([3], 6, 0, "one 3 cannot pair with itself"),
    ([1, 2, 3], 10, 0, "no pairs"),
    ([0, 0, 0, 0], 0, 6, "four zeros: 6 pairs"),
    ([-1, 1, -1, 1], 0, 4, "two -1 times two 1"),
])
def test_examples(a, k, expected, why):
    assert ask(a, k) == [str(expected)], f"a={a}, k={k}: expected {expected} ({why})."


def test_random_small():
    rng = random.Random(20)
    for _ in range(40):
        a = [rng.randint(-4, 4) for _ in range(rng.randint(1, 10))]
        k = rng.randint(-5, 5)
        assert ask(a, k) == [str(brute(a, k))], f"a={a}, k={k}: expected {brute(a, k)}."


def test_large():
    rng = random.Random(21)
    a = [rng.randint(0, 20) for _ in range(200000)]
    c = {}
    for x in a:
        c[x] = c.get(x, 0) + 1
    expected = 0
    for v in c:
        w = 20 - v
        if v < w and w in c:
            expected += c[v] * c[w]
        elif v == w:
            expected += c[v] * (c[v] - 1) // 2
    assert ask(a, 20) == [str(expected)], "Wrong or too slow with 200000 values (about 10^9 pairs). Count with a dictionary."
