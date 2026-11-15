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

def ask(values, timeout=10):
    return run(f"{len(values)}\n" + " ".join(map(str, values)) + "\n", timeout=timeout)


def expect(values):
    return [" ".join(map(str, sorted(values))), " ".join(map(str, sorted(values, reverse=True)))]


@pytest.mark.parametrize("values, why", [
    ([3, -1, 4, 1, -5, 9], "the example"),
    ([7], "one element"),
    ([2, 2, 2], "all equal"),
    ([1, 2, 3, 4], "already sorted"),
    ([4, 3, 2, 1], "reverse sorted"),
    ([10, 9, 100, 1], "numbers, not strings: 10 > 9"),
])
def test_examples(values, why):
    got = ask(values)
    assert got == expect(values), (
        f"Input {values}: expected {expect(values)}, got {got} ({why}). "
        "Line 1 ascending, line 2 descending. Did you convert to int before sorting?")


def test_empty():
    assert ask([]) in ([], ["", ""]), "With n = 0 print nothing (or two empty lines)."


def test_large():
    rng = random.Random(1)
    values = [rng.randint(-10**9, 10**9) for _ in range(200000)]
    assert ask(values) == expect(values), "Wrong on 200000 numbers. Use the built-in sort; do not write a quadratic loop."
