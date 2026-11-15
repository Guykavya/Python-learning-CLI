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

import math


def ask(queries, timeout=10):
    return run(f"{len(queries)}\n" + "\n".join(f"{n} {r}" for n, r in queries) + "\n", timeout=timeout)


@pytest.mark.parametrize("queries, expected, why", [
    ([(5, 2), (4, 0), (6, 6), (3, 5)], ["10", "1", "1", "0"], "the example"),
    ([(0, 0)], ["1"], "C(0, 0) = 1: one way to choose nothing"),
    ([(1, 1), (1, 0)], ["1", "1"], "row 1 is 1 1"),
    ([(4, 2)], ["6"], "row 4 is 1 4 6 4 1; if you got 4 or 10, your rows are shifted by one"),
    ([(10, 3), (10, 7)], ["120", "120"], "C(n, r) = C(n, n - r)"),
    ([(7, 8), (0, 1)], ["0", "0"], "r > n: no way to pick more items than exist, answer 0"),
    ([(52, 5)], ["2598960"], "poker hands: C(52, 5)"),
])
def test_examples(queries, expected, why):
    got = ask(queries)
    assert got == expected, f"Input {queries}: expected {expected}, got {got} ({why})."


def test_full_table():
    queries = [(n, r) for n in range(61) for r in range(0, 62, 3)]
    got = ask(queries)
    assert got == [str(math.comb(n, r)) for n, r in queries], (
        "Some entry of the table is wrong. Row n has n + 1 entries; interior entries are the sum of two above.")


def test_big_middle_values_speed():
    queries = [(60, 30), (59, 29), (58, 29), (60, 29)] * 200
    got = ask(queries, timeout=5)
    assert got == [str(math.comb(n, r)) for n, r in queries], (
        "C(60, 30) = 118264581564861424. If this timed out, you recompute sub-problems: build Pascal's rows once "
        "(or memoise) instead of recursing without memory.")
