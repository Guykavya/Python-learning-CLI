import subprocess
import sys
from pathlib import Path

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

import pytest


def simulate(h, u, d):
    """Day-by-day simulation, used only by the tests on small numbers."""
    height = 0
    for day in range(1, 10_000):
        height += u
        if height >= h:
            return str(day)
        height -= d
        if height <= 0 and day > 1:
            return "never"
    return "never"


def ask(h, u, d, timeout=10):
    return run(f"{h}\n{u}\n{d}\n", timeout=timeout)


@pytest.mark.parametrize("h, u, d, expected, why", [
    (10, 3, 1, "5", "the example from the statement"),
    (5, 5, 100, "1", "u >= h: it escapes on day 1 before any slide"),
    (6, 5, 5, "never", "u == d and u < h: no progress at all"),
    (6, 4, 5, "never", "u < d: it slides further than it climbs"),
    (1, 1, 0, "1", "the smallest well"),
    (9, 3, 1, "4", "h - u = 6 is an exact multiple of the gain 2: do not add an extra day"),
    (10, 3, 0, "4", "no sliding at all"),
    (100, 99, 98, "2", "a tiny gain, but the second climb is enough"),
    (100, 1, 0, "100", "one metre per day"),
])
def test_examples(h, u, d, expected, why):
    got = ask(h, u, d)
    assert got == [expected], f"h={h}, u={u}, d={d}: expected {expected!r}, got {got}. Note: {why}."


def test_matches_simulation():
    rng = random.Random(56)
    for _ in range(12):
        h = rng.randint(1, 60)
        u = rng.randint(1, 15)
        d = rng.randint(0, u)     # include u == d
        expected = simulate(h, u, d)
        got = ask(h, u, d)
        assert got == [expected], (
            f"h={h}, u={u}, d={d}: expected {expected!r}, got {got}. Check the ceiling division "
            "(a + b - 1) // b and the two special cases.")


def test_huge_slow_snail():
    h, u, d = 10 ** 18, 2, 1
    got = ask(h, u, d, timeout=3)
    assert got == [str(10 ** 18 - 1)], (
        f"h=10^18, u=2, d=1: expected {10 ** 18 - 1}, got {got}. Simulating day by day is far too slow "
        "here; use the formula. Floats would also give a slightly wrong answer at this size.")


def test_huge_exact():
    h, u, d = 10 ** 18, 10 ** 9 + 7, 3
    gain = u - d
    expected = 1 + (h - u + gain - 1) // gain
    got = ask(h, u, d, timeout=3)
    assert got == [str(expected)], (
        f"h={h}, u={u}, d={d}: expected {expected}, got {got}. Use integer ceiling division, not / and round.")


def test_huge_never():
    got = ask(10 ** 18, 10 ** 17, 10 ** 17, timeout=3)
    assert got == ["never"], f"u == d (and u < h): expected ['never'], got {got}."


def test_huge_first_day():
    got = ask(10 ** 18, 10 ** 18, 10 ** 18, timeout=3)
    assert got == ["1"], f"u == h: expected ['1'], got {got}. Reaching exactly h counts as escaping."
