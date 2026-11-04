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


def brute(h):
    return max(min(h[i], h[j]) * (j - i) for i in range(len(h)) for j in range(i + 1, len(h)))


def by_sorting(h):
    """Tallest walls first; each wall pairs with the farthest wall at least as tall."""
    order = sorted(range(len(h)), key=lambda i: -h[i])
    lo = hi = order[0]
    best = 0
    for i in order[1:]:
        lo, hi = min(lo, i), max(hi, i)
        best = max(best, h[i] * max(i - lo, hi - i))
    return best


@pytest.mark.parametrize("values, expected, why", [
    ([1, 8, 6, 2, 5, 4, 8, 3, 7], 49, "the example: walls 2 and 9. Moving the taller wall misses it"),
    ([1, 1], 1, "two walls of height 1, one apart"),
    ([0, 5], 0, "a wall of height 0 holds nothing"),
    ([4, 3, 2, 1, 4], 16, "the two outer walls: width 4 times height 4"),
    ([1, 2, 1], 2, "the outer pair: width is j - i = 2, not 3"),
    ([1, 2, 4, 3], 4, "walls 2 and 4 (2 * 2) or 3 and 4 (3 * 1) or 1 and 4 (1 * 3): 4 is best"),
    ([2, 3, 10, 5, 7, 8, 9], 36, "an inner pair wins: walls 3 and 7, min(10, 9) * 4"),
    ([10, 1, 1, 1, 1, 1, 1, 10], 70, "equal outer walls"),
    ([1, 10, 10, 1], 10, "two tall walls side by side beat the wide short container"),
])
def test_examples(values, expected, why):
    got = ask(values)
    assert got == [str(expected)], f"Heights {values}: expected {expected}, got {got} ({why})."


def test_random_small_against_brute_force():
    rng = random.Random(26)
    for _ in range(40):
        n = rng.randint(2, 15)
        values = [rng.randint(0, 9) for _ in range(n)]
        got = ask(values)
        expected = brute(values)
        assert got == [str(expected)], (
            f"Heights {values}: expected {expected}, got {got}. Measure min(h[l], h[r]) * (r - l), then move the "
            "pointer at the SHORTER wall.")


def test_large_increasing():
    n = 200000
    values = [i % 10001 for i in range(1, n + 1)]
    expected = by_sorting(values)
    got = ask(values, timeout=10)
    assert got == [str(expected)], (
        f"Large saw-tooth heights: expected {expected}, got {got}. A timeout means you try every pair: use two "
        "pointers that start at both ends.")


def test_large_random():
    rng = random.Random(2626)
    values = [rng.randint(0, 10000) for _ in range(200000)]
    expected = by_sorting(values)
    got = ask(values, timeout=10)
    assert got == [str(expected)], f"Large random heights: expected {expected}, got {got}."
