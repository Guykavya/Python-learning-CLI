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


def ask(values, queries, timeout=10):
    text = f"{len(values)}\n" + " ".join(map(str, values)) + f"\n{len(queries)}\n"
    text += "".join(f"{l} {r}\n" for l, r in queries)
    return run(text, timeout=timeout)


def brute(values, queries):
    return [str(sum(values[l - 1:r])) for l, r in queries]


def test_example():
    got = ask([2, 7, -3, 5, 1, 4], [(2, 4), (1, 6), (3, 3), (5, 6)])
    assert got == ["9", "16", "-3", "5"], f"Expected 9 16 -3 5 for the example, got {got}."


@pytest.mark.parametrize("values, queries, why", [
    ([5], [(1, 1)], "one element, one question"),
    ([1, 2, 3, 4], [(1, 1), (4, 4), (1, 4)], "single cells at both ends and the whole array"),
    ([10, 20, 30], [(1, 2)], "l = 1: the formula needs p[0] = 0. If you print 30 you dropped position 1"),
    ([10, 20, 30], [(2, 3)], "positions 2..3 are 20 and 30. If you print 30 you used p[r] - p[l] (dropped position l)"),
    ([-4, -4, 9], [(1, 3), (2, 2)], "negative values"),
])
def test_small(values, queries, why):
    got = ask(values, queries)
    assert got == brute(values, queries), f"Array {values}, questions {queries}: expected {brute(values, queries)}, got {got} ({why})."


def test_random_small():
    rng = random.Random(3)
    for _ in range(15):
        n = rng.randint(1, 15)
        values = [rng.randint(-20, 20) for _ in range(n)]
        queries = []
        for _ in range(rng.randint(1, 10)):
            l = rng.randint(1, n)
            queries.append((l, rng.randint(l, n)))
        got = ask(values, queries)
        assert got == brute(values, queries), (
            f"Array {values}, questions {queries}: expected {brute(values, queries)}, got {got}. "
            "Check that both ends are included and positions start at 1.")


def test_large():
    rng = random.Random(4)
    n = q = 200000
    values = [rng.randint(-10**9, 10**9) for _ in range(n)]
    queries = []
    for _ in range(q):
        l = rng.randint(1, 1000)
        queries.append((l, rng.randint(n - 1000, n)))
    p = list(accumulate(values, initial=0))
    expected = [str(p[r] - p[l - 1]) for l, r in queries]
    got = ask(values, queries, timeout=10)
    assert got == expected, (
        "Wrong or too slow with 200000 elements and 200000 wide ranges. If you add up each range with a loop or "
        "sum(), that is O(n * q). Build prefix sums once and subtract.")
