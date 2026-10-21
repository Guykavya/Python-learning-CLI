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


def ask(values, queries, timeout=10):
    text = f"{len(values)}\n" + " ".join(map(str, values)) + f"\n{len(queries)}\n"
    text += "".join(f"{l} {r}\n" for l, r in queries)
    return run(text, timeout=timeout)


def brute(values, queries):
    return [str(sum(values[l - 1:r])) for l, r in queries]


def test_example():
    got = ask([3, -1, 4, 1, 5], [(1, 3), (2, 5), (4, 4)])
    assert got == ["6", "9", "1"], f"The example: expected 6, 9, 1, got {got}."


def test_edges():
    values = [10, 20, 30]
    queries = [(1, 1), (3, 3), (1, 3), (2, 3), (1, 2)]
    got = ask(values, queries)
    assert got == brute(values, queries), (
        f"Values {values}, queries {queries}: expected {brute(values, queries)}, got {got}. "
        "Check the first day (l = 1) and the last day (r = n): an off-by-one in the indexes shows here.")


def test_random_small():
    rng = random.Random(14)
    values = [rng.randint(-50, 50) for _ in range(30)]
    queries = []
    for _ in range(60):
        l = rng.randint(1, 30)
        queries.append((l, rng.randint(l, 30)))
    got = ask(values, queries)
    assert got == brute(values, queries), "Random small test with negative sales: some totals are wrong."


def test_large():
    rng = random.Random(140)
    n = 100000
    values = [rng.randint(-10**9, 10**9) for _ in range(n)]
    before = [0]
    for v in values:
        before.append(before[-1] + v)
    queries = [(rng.randint(1, 1000), rng.randint(n - 1000, n)) for _ in range(100000)]
    expected = [str(before[r] - before[l - 1]) for l, r in queries]
    got = ask(values, queries, timeout=6)
    assert got == expected, (
        "100000 days and 100000 long ranges: wrong totals or too slow. Adding up each range again is O(n) per "
        "question. Precompute running totals once, then answer each question with one subtraction.")
