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


def ask(a, b, timeout=10):
    return run(f"{len(a)} {len(b)}\n" + " ".join(map(str, a)) + "\n" + " ".join(map(str, b)) + "\n", timeout=timeout)


def expected_for(a, b):
    common = sorted(set(a) & set(b))
    return [str(len(common))] + ([" ".join(map(str, common))] if common else [])


@pytest.mark.parametrize("a, b, why", [
    ([1, 2, 2, 3, 7], [2, 2, 7, 9], "the example: repeats count once"),
    ([1, 2, 3], [4, 5, 6], "nothing in common: print 0 and an empty line"),
    ([5], [5], "one value in both"),
    ([1, 1, 1], [1], "a value repeated in A, once in B: still one"),
    ([-5, 0, 5], [5, 0, -5, 9], "negative values are fine; output is sorted"),
    ([9, 8, 7], [7, 8, 9], "all in common, printed in increasing order"),
])
def test_examples(a, b, why):
    assert ask(a, b) == expected_for(a, b), (
        f"A={a}, B={b}: expected {expected_for(a, b)} ({why}). Count distinct common values, print them sorted.")


def test_large():
    rng = random.Random(9)
    a = [rng.randint(-10**9, 10**9) for _ in range(200000)]
    b = a[:50000] + [rng.randint(-10**9, 10**9) for _ in range(150000)]
    rng.shuffle(b)
    assert ask(a, b) == expected_for(a, b), (
        "Wrong or too slow with 200000 values per list. Checking `x in list` for each value is O(n * m); use sets.")
