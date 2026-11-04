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


def ask(values, updates, timeout=10):
    text = f"{len(values)}\n" + " ".join(map(str, values)) + f"\n{len(updates)}\n"
    text += "".join(f"{l} {r} {v}\n" for l, r, v in updates)
    return run(text, timeout=timeout)


def brute(values, updates):
    a = list(values)
    for l, r, v in updates:
        for i in range(l - 1, r):
            a[i] += v
    return [" ".join(map(str, a))]


def test_example():
    got = ask([1, 1, 1, 1, 1], [(1, 3, 2), (2, 5, 10), (5, 5, -4)])
    assert got == ["3 13 13 11 7"], f"Expected '3 13 13 11 7' for the example, got {got}."


@pytest.mark.parametrize("values, updates, why", [
    ([4, 5, 6], [], "no updates: print the array unchanged"),
    ([0, 0, 0, 0], [(2, 4, 5)], "a range that ends at n: d[r + 1] must still exist (make d of size n + 2)"),
    ([0, 0, 0, 0], [(1, 4, 3)], "the whole array"),
    ([0, 0, 0, 0], [(3, 3, 7)], "a range of one cell: only position 3 changes. If 4 changes too, the minus is at r, not r + 1"),
    ([0, 0, 0, 0, 0], [(2, 3, 1)], "positions 2 and 3 only. If position 4 also gets 1, you forgot the -v at r + 1"),
    ([10, 10], [(1, 2, -15), (1, 1, 5)], "negative additions"),
    ([1], [(1, 1, 1)] * 5, "the same update five times on one cell"),
])
def test_small(values, updates, why):
    got = ask(values, updates)
    assert got == brute(values, updates), f"Array {values}, updates {updates}: expected {brute(values, updates)}, got {got} ({why})."


def test_random_small():
    rng = random.Random(5)
    for _ in range(15):
        n = rng.randint(1, 12)
        values = [rng.randint(-9, 9) for _ in range(n)]
        updates = []
        for _ in range(rng.randint(0, 8)):
            l = rng.randint(1, n)
            updates.append((l, rng.randint(l, n), rng.randint(-5, 5)))
        got = ask(values, updates)
        assert got == brute(values, updates), (
            f"Array {values}, updates {updates}: expected {brute(values, updates)}, got {got}.")


def test_large():
    rng = random.Random(6)
    n = q = 200000
    values = [rng.randint(-10**9, 10**9) for _ in range(n)]
    updates = []
    for _ in range(q):
        l = rng.randint(1, 500)
        updates.append((l, rng.randint(n - 500, n), rng.randint(-10**9, 10**9)))
    # expected: sweep over the sorted start/stop events (a second way to get the same totals)
    events = sorted([(l, v) for l, r, v in updates] + [(r + 1, -v) for l, r, v in updates])
    a = list(values)
    k = 0
    total = 0
    for i in range(1, n + 1):
        while k < len(events) and events[k][0] == i:
            total += events[k][1]
            k += 1
        a[i - 1] += total
    got = ask(values, updates, timeout=10)
    assert got == [" ".join(map(str, a))], (
        "Wrong or too slow with 200000 long range updates. Adding v to every cell of every range is O(n * q). "
        "Mark +v at l and -v at r + 1, then take one running total at the end.")
