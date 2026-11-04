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


def brute(values):
    return sum(1 for i in range(len(values)) for j in range(i + 1, len(values)) if values[i] > values[j])


def fast(values):
    # Fenwick tree over ranks, independent of the learner's method
    rank = {v: r + 1 for r, v in enumerate(sorted(set(values)))}
    size = len(rank)
    tree = [0] * (size + 1)
    total = 0
    for k, v in enumerate(values):
        r = rank[v]
        i = r
        seen_le = 0
        while i > 0:
            seen_le += tree[i]
            i -= i & -i
        total += k - seen_le
        i = r
        while i <= size:
            tree[i] += 1
            i += i & -i
    return total


@pytest.mark.parametrize("values, why", [
    ([2, 4, 1, 3, 5], "the example: (2,1), (4,1), (4,3)"),
    ([1], "one element"),
    ([1, 2, 3, 4], "sorted: 0"),
    ([4, 3, 2, 1], "reversed: 6"),
    ([2, 2, 2], "equal values are not inversions"),
    ([3, 1, 2, 1], "duplicates: (3,1),(3,2),(3,1),(2,1)"),
])
def test_examples(values, why):
    got = ask(values)
    assert got == [str(brute(values))], f"Input {values}: expected {brute(values)}, got {got} ({why}). Equal values are not inversions; add len(left) - i when a right value is taken."


def test_random_small():
    rng = random.Random(17)
    for _ in range(60):
        values = [rng.randint(-5, 5) for _ in range(rng.randint(1, 14))]
        assert ask(values) == [str(brute(values))], f"Input {values}: expected {brute(values)}."


def test_large_random():
    rng = random.Random(18)
    values = [rng.randint(-10**9, 10**9) for _ in range(200000)]
    assert ask(values) == [str(fast(values))], "Wrong or too slow on 200000 numbers. Two loops are O(n^2): use merge sort and count while merging."


def test_large_reversed():
    n = 200000
    assert ask(list(range(n, 0, -1))) == [str(n * (n - 1) // 2)], "Reversed 200000 numbers: every pair is an inversion, n(n-1)/2."


def test_large_many_equal():
    rng = random.Random(19)
    values = [rng.randint(0, 3) for _ in range(200000)]
    assert ask(values) == [str(fast(values))], "Many equal values: take the LEFT value on ties so equal values are not counted."
