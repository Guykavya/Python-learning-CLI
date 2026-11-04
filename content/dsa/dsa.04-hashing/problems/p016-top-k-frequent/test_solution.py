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
from collections import Counter


def ask(a, k, timeout=10):
    return run(f"{len(a)} {k}\n" + " ".join(map(str, a)) + "\n", timeout=timeout)


def expected_for(a, k):
    c = Counter(a)
    return [" ".join(map(str, sorted(c, key=lambda v: (-c[v], v))[:k]))]


@pytest.mark.parametrize("a, k, why", [
    ([1, 1, 1, 2, 2, 3, 3, 4], 2, "the example: 2 and 3 tie, smaller value first"),
    ([5], 1, "single value"),
    ([3, 3, 2, 2, 1, 1], 3, "all tie: ascending by value"),
    ([9, 9, 9, 8, 8, 7], 1, "k = 1"),
    ([-1, -1, 0, 0, 0, 5], 2, "negative values"),
    ([4, 1, 2, 2, 1, 4, 4], 3, "ties after the leader"),
])
def test_examples(a, k, why):
    got = ask(a, k)
    assert got == expected_for(a, k), (
        f"a={a}, k={k}: expected {expected_for(a, k)}, got {got} ({why}). Order by count (largest first), then by value (smallest first).")


def test_large():
    rng = random.Random(17)
    a = [int(rng.paretovariate(1.2)) for _ in range(200000)]
    k = len(set(a)) // 2 + 1
    assert ask(a, k) == expected_for(a, k), "Wrong or slow on 200000 values: count once with a dictionary, then sort the distinct values."
