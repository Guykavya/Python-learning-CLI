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


def ask(values, timeout=10):
    return run(f"{len(values)}\n" + " ".join(map(str, values)) + "\n", timeout=timeout)


def expected_for(values):
    return [f"{v} {c}" for v, c in Counter(values).items()]


@pytest.mark.parametrize("values, why", [
    ([3, 1, 3, 2, 1, 3, 5], "the example"),
    ([7], "one element"),
    ([4, 4, 4, 4], "all equal: one line only"),
    ([-1, 1, -1, 0, 0], "negative numbers and zero are ordinary keys"),
    ([5, 4, 3, 2, 1], "all different: every count is 1"),
])
def test_examples(values, why):
    got = ask(values)
    assert got == expected_for(values), (
        f"Input {values}: expected {expected_for(values)}, got {got} ({why}). "
        "Print values in the order they FIRST appear, with their total count.")


def test_empty():
    assert run("0\n\n") == [], "With n = 0 print nothing at all."


def test_first_appearance_order_not_sorted():
    got = ask([9, 2, 9, 1])
    assert got == ["9 2", "2 1", "1 1"], f"Got {got}. Do not sort: 9 appeared first, so it is printed first."


def test_large():
    rng = random.Random(4)
    values = [rng.randint(1, 1000) for _ in range(200000)]
    got = ask(values)
    assert got == expected_for(values), (
        "Wrong or too slow on 200000 numbers. Calling a.count(x) for every value is O(n^2); "
        "count in one pass with a dictionary.")
