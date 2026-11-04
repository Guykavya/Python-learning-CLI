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
from itertools import combinations


def ask(values, timeout=10):
    return run(f"{len(values)}\n" + " ".join(map(str, values)) + "\n", timeout=timeout)


def brute(values):
    found = sorted(set(tuple(sorted(t)) for t in combinations(values, 3) if sum(t) == 0))
    return [str(len(found))] + [f"{x} {y} {z}" for x, y, z in found]


def by_counts(values):
    """Triplets from the counts of each distinct value: an independent way to get the expected output."""
    cnt = {}
    for v in values:
        cnt[v] = cnt.get(v, 0) + 1
    keys = sorted(cnt)
    out = []
    for i, x in enumerate(keys):
        for y in keys[i:]:
            z = -x - y
            if z < y:
                break
            if z not in cnt:
                continue
            need = {}
            for v in (x, y, z):
                need[v] = need.get(v, 0) + 1
            if all(cnt[v] >= k for v, k in need.items()):
                out.append(f"{x} {y} {z}")
    return [str(len(out))] + out


@pytest.mark.parametrize("values, expected, why", [
    ([-1, 0, 1, 2, -1, -4], ["2", "-1 -1 2", "-1 0 1"], "the example"),
    ([1, 2, 3], ["0"], "no triplet: print only 0"),
    ([0, 0], ["0"], "fewer than three numbers: no triplet"),
    ([0, 0, 0], ["1", "0 0 0"], "three zeros make one triplet"),
    ([0, 0, 0, 0, 0], ["1", "0 0 0"], "five zeros: still one DIFFERENT triplet. Skip duplicate values"),
    ([-2, 1, 1], ["1", "-2 1 1"], "the two 1s are different positions, so -2 1 1 counts"),
    ([-2, 1, 1, 1, 1], ["1", "-2 1 1"], "many copies of 1: print -2 1 1 once"),
    ([-1, -1, -1, 2, 2], ["1", "-1 -1 2"], "skip a[i] only when it equals the PREVIOUS value, after it was used"),
    ([3, -3, 0, 2, -2, 1, -1], ["5", "-3 0 3", "-3 1 2", "-2 -1 3", "-2 0 2", "-1 0 1"],
     "several triplets: sorted by x, then by y"),
])
def test_examples(values, expected, why):
    got = ask(values)
    assert got == expected, f"Input {values}: expected {expected}, got {got} ({why})."


def test_random_small_against_brute_force():
    rng = random.Random(25)
    for _ in range(40):
        n = rng.randint(1, 12)
        values = [rng.randint(-5, 5) for _ in range(n)]
        got = ask(values)
        expected = brute(values)
        assert got == expected, (
            f"Input {values}: expected {expected}, got {got}. Each different triplet once, values in "
            "non-decreasing order, lines sorted by x then y, and the count on the first line.")


def test_large_all_zero():
    got = ask([0] * 2000, timeout=10)
    assert got == ["1", "0 0 0"], (
        f"2000 zeros: expected one triplet '0 0 0', got {len(got)} lines. Without the duplicate skips you "
        "print 0 0 0 many times or run too long.")


def test_large_random():
    rng = random.Random(2525)
    values = [rng.randint(-10**5, 10**5) for _ in range(2000)]
    expected = by_counts(values)
    got = ask(values, timeout=10)
    assert got[:1] == expected[:1], (
        f"2000 random values: expected {expected[0]} triplets, got {got[:1]}. A timeout means O(n^3) loops: fix "
        "the first value and use two pointers for the other two.")
    assert got == expected, "The count is right, but some triplet line or the order is wrong (sort by x, then y)."
