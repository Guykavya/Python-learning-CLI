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


def ask(values, k, t, timeout=10):
    return run(f"{len(values)} {k} {t}\n" + " ".join(map(str, values)) + "\n", timeout=timeout)


def brute(values, k, t):
    return str(sum(1 for i in range(len(values) - k + 1) if sum(values[i:i + k]) >= t * k))


@pytest.mark.parametrize("values, k, t, why", [
    ([1, 3, 5, 2, 6, 4, 0], 3, 4, "the example: a window with average exactly 4 counts (use >=)"),
    ([5, 5, 5], 3, 5, "one window, average exactly t: count it"),
    ([5, 5, 5], 3, 6, "one window, average below t"),
    ([9, 1, 1, 1], 2, 5, "only the first window qualifies: check it before the slide loop"),
    ([1, 1, 1, 9], 2, 5, "only the last window qualifies: make sure the loop reaches it"),
    ([-1, 0, -1, -2], 1, -1, "negative threshold, k = 1: count elements >= -1"),
    ([-1, 0, 0, -2], 3, 0, "sum -1, average -1/3: below 0, so not counted"),
    ([4, 4, 4, 4], 2, 4, "every window has average exactly 4"),
])
def test_examples(values, k, t, why):
    got = ask(values, k, t)
    want = brute(values, k, t)
    assert got == [want], f"Array {values}, k = {k}, t = {t}: expected {want}, got {got} ({why})."


def test_random_small():
    rng = random.Random(18)
    for _ in range(30):
        values = [rng.randint(-5, 5) for _ in range(rng.randint(1, 12))]
        k = rng.randint(1, len(values))
        t = rng.randint(-3, 3)
        got = ask(values, k, t)
        want = brute(values, k, t)
        assert got == [want], f"Array {values}, k = {k}, t = {t}: expected {want}, got {got}."


def test_large():
    rng = random.Random(19)
    values = [rng.randint(-10**4, 10**4) for _ in range(200000)]
    k, t = 50000, 0
    p = list(accumulate(values, initial=0))
    want = str(sum(1 for i in range(len(values) - k + 1) if p[i + k] - p[i] >= t * k))
    got = ask(values, k, t, timeout=10)
    assert got == [want], (
        f"n = 200000, k = 50000: expected {want}, got {got}. If this timed out you re-sum each window (O(n * k)); "
        "slide it instead.")
