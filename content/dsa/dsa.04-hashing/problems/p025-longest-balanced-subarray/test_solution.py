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


def ask(a, timeout=10):
    return run(f"{len(a)}\n" + " ".join(map(str, a)) + "\n", timeout=timeout)


def brute(a):
    best = 0
    for l in range(len(a)):
        for r in range(l, len(a)):
            seg = a[l:r + 1]
            if seg.count(0) == seg.count(1):
                best = max(best, r - l + 1)
    return best


@pytest.mark.parametrize("a, expected, why", [
    ([0, 1, 0, 1, 1, 1, 0], 4, "the example"),
    ([0, 1], 2, "the smallest balanced array"),
    ([1, 1, 1], 0, "no zeros: none balanced"),
    ([0, 0, 1, 1], 4, "the whole array"),
    ([1, 1, 0, 0, 1], 4, "balanced block in the middle-left"),
    ([0], 0, "one element is never balanced"),
    ([1, 0, 1, 1, 0, 0, 0], 6, "block starting at index 1 or ending at the end"),
])
def test_examples(a, expected, why):
    assert ask(a) == [str(expected)], f"a={a}: expected {expected} ({why}). Keep the FIRST index of each total, start with {{0: -1}}."


def test_random_small():
    rng = random.Random(29)
    for _ in range(50):
        a = [rng.randint(0, 1) for _ in range(rng.randint(1, 12))]
        assert ask(a) == [str(brute(a))], f"a={a}: expected {brute(a)}."


def test_large():
    rng = random.Random(30)
    a = [rng.randint(0, 1) for _ in range(200000)]
    first, s, best = {0: -1}, 0, 0
    for i, x in enumerate(a):
        s += 1 if x else -1
        if s in first:
            best = max(best, i - first[s])
        else:
            first[s] = i
    assert ask(a) == [str(best)], "Wrong or slow on 200000 values. The O(n^2) brute force over all blocks cannot finish."
