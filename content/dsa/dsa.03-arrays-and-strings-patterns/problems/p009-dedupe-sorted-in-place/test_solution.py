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


def expected(values):
    out = []
    for x in values:
        if not out or out[-1] != x:
            out.append(x)
    return [str(len(out))] + ([" ".join(map(str, out))] if out else [])


@pytest.mark.parametrize("values, why", [
    ([1, 1, 2, 3, 3, 3, 7, 7], "the example"),
    ([5], "one element: k = 1"),
    ([4, 4, 4, 4], "all equal: k = 1"),
    ([1, 2, 3], "no duplicates: everything stays, k = n"),
    ([-3, -3, 0, 0, 0, 9], "negative values and a run at the start"),
    ([1, 2, 2], "a run at the very end"),
    ([0, 0, 1, 1, 2, 2, 3, 3, 4, 4], "every value twice"),
])
def test_examples(values, why):
    got = ask(values)
    assert got == expected(values), f"Input {values}: expected {expected(values)}, got {got} ({why})."


def test_empty():
    got = run("0\n\n")
    assert got == ["0"], f"n = 0: print k = 0 and an empty second line. Got {got}. Do not start w at 1 when there is nothing to keep."


def test_random_small():
    rng = random.Random(14)
    for _ in range(25):
        values = sorted(rng.randint(-4, 4) for _ in range(rng.randint(1, 12)))
        got = ask(values)
        assert got == expected(values), (
            f"Input {values}: expected {expected(values)}, got {got}. Compare each value with the last value you kept.")


def test_large():
    rng = random.Random(15)
    values = sorted(rng.randint(0, 150000) for _ in range(200000))
    got = ask(values, timeout=10)
    assert got == expected(values), (
        "200000 sorted values with about 110000 distinct ones: wrong or too slow. `x not in result` scans the "
        "whole result list for each element, and pop/del shift the list each time: both are O(n^2).")
