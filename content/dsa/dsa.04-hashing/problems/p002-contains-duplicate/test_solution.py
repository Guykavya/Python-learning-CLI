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


@pytest.mark.parametrize("values, expected, why", [
    ([4, 8, 15, 8, 23], "YES", "the example: 8 twice"),
    ([4, 8, 15, 16, 23], "NO", "all different"),
    ([1], "NO", "a single value cannot repeat"),
    ([2, 2], "YES", "two equal values next to each other"),
    ([7, 1, 2, 3, 7], "YES", "the repeat is at the two ends"),
    ([0, -0, 5], "YES", "0 and -0 are the same integer"),
    ([-3, 3], "NO", "-3 and 3 are different values"),
])
def test_examples(values, expected, why):
    assert ask(values) == [expected], f"Input {values}: expected {expected} ({why})."


def test_empty():
    assert run("0\n\n") == ["NO"], "No numbers means no repeat: print NO."


def test_large_all_different():
    values = list(range(1, 200001))
    random.Random(5).shuffle(values)
    assert ask(values) == ["NO"], (
        "200000 different numbers. Comparing every pair is 2 * 10^10 steps. Use a set of values seen so far.")


def test_large_repeat_at_the_end():
    values = list(range(1, 200000)) + [1]
    assert ask(values) == ["YES"], "The repeat is 1 ... 1, far apart. Did a slow pairwise scan time out?"
