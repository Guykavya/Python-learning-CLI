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


def ask(a, target, timeout=10):
    return run(f"{len(a)} {target}\n" + " ".join(map(str, a)) + "\n", timeout=timeout)


def check(a, target, got, why=""):
    assert len(got) == 1 and len(got[0].split()) == 2, f"Print exactly two numbers 'i j'. Got {got}. {why}"
    i, j = map(int, got[0].split())
    assert 0 <= i < j < len(a), f"Got {i} {j}: print two different positions with i < j (0-based). {why}"
    assert a[i] + a[j] == target, f"a[{i}] + a[{j}] = {a[i]} + {a[j]} = {a[i] + a[j]}, not {target}. {why}"


@pytest.mark.parametrize("a, target, why", [
    ([2, 7, 11, 15], 9, "the example"),
    ([3, 2, 4], 6, "3 + 3 would be wrong: an element must not pair with itself; the answer is 2 + 4"),
    ([3, 3], 6, "equal values at two positions"),
    ([-3, 4, 3, 90], 0, "negative values"),
    ([0, 4, 3, 0], 0, "two zeros"),
    ([1, 5, 9, 14], 23, "the pair is at the end"),
])
def test_examples(a, target, why):
    check(a, target, ask(a, target), why)


def test_large():
    rng = random.Random(15)
    a = rng.sample(range(-10**9, 10**9), 200000)
    i, j = 5, 199990
    target = a[i] + a[j]
    # make sure the pair is the only one: all values distinct, so check with a dictionary
    pos = {v: k for k, v in enumerate(a)}
    pairs = [(k, pos[target - v]) for k, v in enumerate(a) if (target - v) in pos and pos[target - v] > k]
    if len(pairs) != 1:
        a[j] = 10**9 + 7
        target = a[i] + a[j]
    check(a, target, ask(a, target), "")
