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


def ask(values, k, timeout=10):
    return run(f"{len(values)} {k}\n" + " ".join(map(str, values)) + "\n", timeout=timeout)


def brute(values, k):
    return str(max(sum(values[i:i + k]) for i in range(len(values) - k + 1)))


@pytest.mark.parametrize("values, k, why", [
    ([2, -1, 4, 1, -6, 5, 3], 3, "the example: the first window is the best"),
    ([1, 2, 3, 4, 5], 2, "the last window is the best: make sure the loop reaches it"),
    ([5], 1, "one element, k = 1"),
    ([3, 1, 4], 3, "k = n: only one window"),
    ([-5, -2, -8, -1], 2, "all negative: the answer is negative. Do not start best at 0"),
    ([-5, -2, -8, -1], 1, "k = 1: the largest single element"),
    ([4, -10, 4, 4, -10, 4], 2, "the best window is in the middle"),
    ([10**9] * 6, 4, "big values"),
])
def test_examples(values, k, why):
    got = ask(values, k)
    assert got == [brute(values, k)], f"Array {values}, k = {k}: expected {brute(values, k)}, got {got} ({why})."


def test_random_small():
    rng = random.Random(16)
    for _ in range(30):
        values = [rng.randint(-10, 10) for _ in range(rng.randint(1, 12))]
        k = rng.randint(1, len(values))
        got = ask(values, k)
        assert got == [brute(values, k)], (
            f"Array {values}, k = {k}: expected {brute(values, k)}, got {got}. The element leaving is a[r - k].")


def test_large():
    rng = random.Random(17)
    values = [rng.randint(-10**9, 10**9) for _ in range(200000)]
    k = 100000
    p = list(accumulate(values, initial=0))
    expected = str(max(p[i + k] - p[i] for i in range(len(values) - k + 1)))
    got = ask(values, k, timeout=10)
    assert got == [expected], (
        "Wrong or too slow for n = 200000, k = 100000. If you re-sum the window each step that is O(n * k). "
        "Slide it: add the entering element and subtract the leaving one.")
