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
    ([40, 90, 45, 90, 10, 46], ["2", "4"], "the example"),
    ([40, 90, 45, 90, 10, 44], ["2", "3"], "44 * 2 = 88 is less than 90"),
    ([5], ["1", "1"], "one score is the highest and at least half of itself"),
    ([0, 0, 0], ["3", "3"], "all zero: 2 * 0 >= 0 is true for every score"),
    ([1, 2, 3, 4], ["1", "3"], "2, 3 and 4 are at least half of 4"),
    ([7, 3], ["1", "1"], "6 < 7, so 3 is not at least half"),
])
def test_examples(values, expected, why):
    got = ask(values)
    assert got == expected, f"Scores {values}: expected {expected}, got {got} ({why})."


def test_large():
    rng = random.Random(9)
    values = [rng.randint(0, 10**9) for _ in range(100000)]
    best = max(values)
    expected = [str(values.count(best)), str(sum(1 for v in values if 2 * v >= best))]
    got = ask(values, timeout=5)
    assert got == expected, (
        f"100000 scores: expected {expected}, got {got}. If this timed out, max(a) is still inside the loop. "
        "The highest score does not change while you loop, so compute it once before the loop.")
