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


def ask(h, timeout=10):
    return run(f"{len(h)}\n" + " ".join(map(str, h)) + "\n", timeout=timeout)


def by_prefix_max(h):
    n = len(h)
    if n == 0:
        return 0
    left = [0] * n
    right = [0] * n
    left[0] = h[0]
    for i in range(1, n):
        left[i] = max(left[i - 1], h[i])
    right[n - 1] = h[n - 1]
    for i in range(n - 2, -1, -1):
        right[i] = max(right[i + 1], h[i])
    return sum(min(left[i], right[i]) - h[i] for i in range(n))


@pytest.mark.parametrize("h, want, why", [
    ([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1], 6, "the example"),
    ([4, 2, 0, 3, 2, 5], 9, "a deep basin: 2 + 4 + 1 + 2"),
    ([5, 0, 5], 5, "one dip between two equal walls"),
    ([5, 0, 3], 3, "the lower wall decides the level: min(5, 3) - 0 = 3, not 5"),
    ([3, 0, 5], 3, "the lower wall is on the left this time"),
    ([1, 2, 3, 4, 5], 0, "increasing: water runs off the left side"),
    ([5, 4, 3, 2, 1], 0, "decreasing: water runs off the right side"),
    ([2, 2, 2], 0, "flat: nothing is trapped"),
    ([7], 0, "a single bar holds nothing"),
    ([0, 0, 4, 0, 0], 0, "a single peak with nothing on the far sides holds nothing"),
    ([3, 0, 0, 2, 0, 4], 10, "3 + 3 + 1 + 3: the inner bar 2 is under water level 3"),
])
def test_examples(h, want, why):
    got = ask(h)
    assert got == [str(want)], f"Heights {h}: expected {want}, got {got} ({why})."


def test_empty():
    assert ask([]) == ["0"], "With n = 0 the second line is empty and the answer is 0. Do not index h[0] or h[-1] blindly."


def test_never_negative():
    got = ask([1, 5, 2])
    assert got == ["0"], (
        f"Heights [1, 5, 2]: expected 0, got {got}. If you take the maxima strictly left and right of bar i, "
        "the level can be below h[i] (here min(1, 2) - 5 = -4). Include bar i itself, or add max(0, ...).")


def test_big_heights():
    h = [10**9, 0, 0, 10**9]
    assert ask(h) == [str(2 * 10**9)], "Heights up to 10^9: the total is 2 * 10^9, which needs exact integers."


def test_random_small():
    rng = random.Random(45)
    for _ in range(20):
        h = [rng.randint(0, 9) for _ in range(rng.randint(1, 30))]
        got = ask(h)
        assert got == [str(by_prefix_max(h))], f"Heights {h}: expected {by_prefix_max(h)}, got {got}."


def test_large_random():
    rng = random.Random(4500)
    h = [rng.randint(0, 10**9) for _ in range(200000)]
    want = by_prefix_max(h)
    got = ask(h, timeout=8)
    assert got == [str(want)], (
        f"n = 200000: expected {want}, got {got}. If it timed out, you scan left and right for every bar (O(n^2)); "
        "keep running maxima instead.")


def test_large_valley():
    n = 200000
    h = [n] + [0] * (n - 2) + [n]
    got = ask(h, timeout=8)
    assert got == [str(n * (n - 2))], (
        f"A wide valley between two walls of height {n}: expected {n * (n - 2)}, got {got}. "
        "Rescanning for the highest wall from every bar takes O(n^2) here.")
