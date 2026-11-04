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

import bisect


def brute(values):
    return sum(1 for i in range(len(values)) for j in range(i + 1, len(values)) if values[i] > 2 * values[j])


def fast(values):
    pts = sorted(set(values))
    size = len(pts)
    tree = [0] * (size + 2)

    def add(i):
        i += 1
        while i <= size:
            tree[i] += 1
            i += i & -i

    def prefix(i):  # count of stored values with rank < i
        s = 0
        while i > 0:
            s += tree[i]
            i -= i & -i
        return s

    total = 0
    for k, v in enumerate(values):
        le = prefix(bisect.bisect_right(pts, 2 * v))
        total += k - le
        add(bisect.bisect_left(pts, v))
    return total


@pytest.mark.parametrize("values, why", [
    ([1, 3, 2, 3, 1], "the example: 2 pairs"),
    ([2, 4, 3, 5, 1], "second example: 3 pairs"),
    ([1], "one element"),
    ([5, 2], "5 > 4"),
    ([4, 2], "4 > 4 is false: strictly greater"),
    ([-5, -5], "negatives: -5 > -10 is true"),
    ([-1, 0, -3], "mixed signs"),
    ([2147483647, -2147483648], "extreme values: no overflow in Python, but check the sign logic"),
])
def test_examples(values, why):
    got = ask(values)
    assert got == [str(brute(values))], f"Input {values}: expected {brute(values)}, got {got} ({why}). Condition: a[i] > 2 * a[j], strictly, with i < j."


def test_random_small():
    rng = random.Random(47)
    for _ in range(100):
        values = [rng.randint(-6, 6) for _ in range(rng.randint(1, 12))]
        assert ask(values) == [str(brute(values))], f"Input {values}: expected {brute(values)}. Count BEFORE merging, with the threshold 2 * right[j]."


def test_large_random():
    rng = random.Random(48)
    values = [rng.randint(-2**31, 2**31 - 1) for _ in range(100000)]
    assert ask(values) == [str(fast(values))], "Wrong or too slow on 100000 numbers (5 * 10^9 pairs would never finish)."


def test_large_decreasing():
    values = [100000 - i for i in range(100000)]
    assert ask(values) == [str(fast(values))], "Decreasing input of 100000: many reverse pairs; the pointer must not restart for each j."
