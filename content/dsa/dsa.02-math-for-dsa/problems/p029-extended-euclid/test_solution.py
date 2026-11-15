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


def ask(pairs, timeout=10):
    return run(f"{len(pairs)}\n" + "\n".join(f"{a} {b}" for a, b in pairs) + "\n", timeout=timeout)


def ext(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = ext(b, a % b)
    return g, y1, x1 - (a // b) * y1


def line(a, b):
    return " ".join(map(str, ext(a, b)))


@pytest.mark.parametrize("a, b, expected, why", [
    (240, 46, "2 -9 47", "the example: 240*(-9) + 46*47 = 2"),
    (17, 5, "1 -2 7", "17*(-2) + 5*7 = 1"),
    (0, 5, "5 0 1", "gcd(0, 5) = 5 with x = 0, y = 1: the first call swaps the pair"),
    (5, 0, "5 1 0", "base case b == 0 returns (a, 1, 0)"),
    (0, 0, "0 1 0", "base case again: (a, 1, 0) with a = 0"),
    (7, 7, "7 0 1", "equal numbers: one step, 7 % 7 = 0"),
    (1, 1000, "1 1 0", "ext(1, 1000) -> ext(1000, 1) -> ext(1, 0): x, y after two swaps"),
    (12, 18, "6 -1 1", "12*(-1) + 18*1 = 6"),
])
def test_examples(a, b, expected, why):
    got = ask([(a, b)])
    assert got == [expected], (
        f"ext({a}, {b}): expected `{expected}`, got {got} ({why}). Use exactly the algorithm in the statement: "
        "return (g, y1, x1 - (a // b) * y1).")


def test_small_all_pairs():
    pairs = [(a, b) for a in range(0, 25) for b in range(0, 25)]
    got = ask(pairs)
    assert len(got) == len(pairs), "Print exactly one line per query."
    for (a, b), g in zip(pairs, got):
        assert g == line(a, b), (
            f"a = {a}, b = {b}: expected `{line(a, b)}`, got `{g}`. Check the base case and the update "
            "(g, y1, x1 - (a // b) * y1).")


def test_equation_holds_big():
    rng = random.Random(29)
    pairs = [(rng.randint(0, 10 ** 18), rng.randint(0, 10 ** 18)) for _ in range(2000)]
    pairs.append((10 ** 18, 10 ** 18 - 1))
    # Fibonacci pair: the deepest recursion
    f = [1, 1]
    while f[-1] < 10 ** 18:
        f.append(f[-1] + f[-2])
    pairs.append((f[-1], f[-2]))
    got = ask(pairs, timeout=6)
    assert len(got) == len(pairs), "Print exactly one line per query."
    for (a, b), g in zip(pairs, got):
        assert g == line(a, b), (
            f"a = {a}, b = {b}: expected `{line(a, b)}`, got `{g}`. Use // (integer division), not / : floats lose "
            "digits above 2^53.")


def test_many_queries():
    rng = random.Random(290)
    pairs = [(rng.randint(0, 10 ** 18), rng.randint(0, 10 ** 18)) for _ in range(20000)]
    got = ask(pairs, timeout=5)
    assert got == [line(a, b) for a, b in pairs], (
        "20000 queries: wrong output or too slow. Each query should take about 90 steps, not a loop over many numbers.")
