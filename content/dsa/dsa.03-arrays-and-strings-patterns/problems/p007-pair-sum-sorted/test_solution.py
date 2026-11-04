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


def ask(values, target, timeout=10):
    return run(f"{len(values)}\n" + " ".join(map(str, values)) + f"\n{target}\n", timeout=timeout)


def pinned(values, target):
    """Smallest i that has a partner, then the largest j for it."""
    last = {}
    for k, x in enumerate(values):
        last[x] = k
    for i, x in enumerate(values):
        j = last.get(target - x, -1)
        if j > i:
            return f"{i + 1} {j + 1}"
    return "-1"


@pytest.mark.parametrize("values, target, expected, why", [
    ([1, 2, 4, 5, 7, 11], 9, "2 5", "the example: the rule finds 2 + 7 before 4 + 5"),
    ([1, 2, 3, 4, 6], 7, "1 5", "the first check (1 + 6) already matches"),
    ([1, 3, 5], 100, "-1", "no pair: every sum is too small"),
    ([5], 10, "-1", "one element cannot pair with itself. If you print 1 1, your loop runs while i <= j"),
    ([5, 5], 10, "1 2", "two equal elements at different positions are a valid pair"),
    ([2, 2, 2, 2], 4, "1 4", "duplicates: the rule finds the outermost pair (smallest i, largest j)"),
    ([-3, -1, 0, 2, 8], -1, "1 4", "negative numbers: -3 + 2"),
    ([1, 2, 3, 9], 7, "-1", "4 is missing: the pointers meet without a match"),
    ([1, 1, 3, 3], 4, "1 4", "1 + 3: smallest i is 1, and its largest partner position is 4, not 3"),
    ([0, 0], 0, "1 2", "target 0"),
])
def test_examples(values, target, expected, why):
    got = ask(values, target)
    assert got == [expected], f"Array {values}, target {target}: expected {expected}, got {got} ({why})."


def test_random_small():
    rng = random.Random(10)
    for _ in range(40):
        values = sorted(rng.randint(-8, 8) for _ in range(rng.randint(1, 9)))
        target = rng.randint(-12, 12)
        got = ask(values, target)
        want = pinned(values, target)
        assert got == [want], (
            f"Array {values}, target {target}: expected {want}, got {got}. Follow the two-pointer rule exactly: "
            "move i when the sum is too small, j when it is too big.")


def test_large_no_pair():
    values = list(range(0, 400000, 2))
    got = ask(values, 400001, timeout=10)
    assert got == ["-1"], (
        f"200000 even numbers and an odd target: no pair, expected -1, got {got}. If this timed out, you check "
        "all pairs (O(n^2)); the two pointers need at most n - 1 steps.")


def test_large_one_pair():
    rng = random.Random(11)
    values = sorted(rng.sample(range(0, 10**9, 2), 200000))
    values[70000] += 1
    values[150000] += 1
    target = values[70000] + values[150000]
    got = ask(values, target, timeout=10)
    assert got == [pinned(values, target)], (
        f"Expected {pinned(values, target)} for a single odd pair among 200000 even numbers, got {got}.")
