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
from itertools import accumulate


def ask(values, timeout=10):
    return run(f"{len(values)}\n" + " ".join(map(str, values)) + "\n", timeout=timeout)


@pytest.mark.parametrize("values, expected, why", [
    ([3, -1, 4, 1, 5], "0 3 2 6 7 12", "the example"),
    ([7], "0 7", "one element: two cells, 0 and 7"),
    ([-5, -5, -5], "0 -5 -10 -15", "negative values make the totals go down"),
    ([1, -1, 1, -1], "0 1 0 1 0", "totals can return to 0"),
    ([10**9] * 4, "0 1000000000 2000000000 3000000000 4000000000", "big values: Python ints do not overflow"),
])
def test_examples(values, expected, why):
    got = ask(values)
    assert got == [expected], f"Input {values}: expected {expected!r}, got {got} ({why})."


def test_starts_with_zero():
    got = ask([4, 4])
    assert got and got[0].split()[:1] == ["0"], (
        f"Got {got}. The prefix array starts with p[0] = 0, the sum of no elements, so it has n + 1 values.")
    assert len(got[0].split()) == 3, f"Got {got}: for 2 elements print 3 values (0 4 8)."


def test_empty_array():
    got = run("0\n\n")
    assert got == ["0"], f"With n = 0 the prefix array is just [0]. Got {got}. Do not read a[0] when the array is empty."


def test_random_small():
    rng = random.Random(1)
    for _ in range(20):
        values = [rng.randint(-50, 50) for _ in range(rng.randint(1, 12))]
        expected = " ".join(str(sum(values[:i])) for i in range(len(values) + 1))
        got = ask(values)
        assert got == [expected], f"Input {values}: expected {expected!r}, got {got}."


def test_large_array():
    rng = random.Random(2)
    values = [rng.randint(-10**9, 10**9) for _ in range(200000)]
    expected = " ".join(map(str, accumulate(values, initial=0)))
    got = ask(values, timeout=10)
    assert got == [expected], (
        "Wrong or slow on 200000 elements. If you compute each cell with sum(a[:i]) you re-sum the prefix every step "
        "(O(n^2)). Add one element to the previous cell instead.")
