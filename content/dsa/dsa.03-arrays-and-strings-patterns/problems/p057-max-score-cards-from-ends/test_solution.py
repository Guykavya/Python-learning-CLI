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


def ask(a, k, timeout=10):
    return run(f"{len(a)} {k}\n" + " ".join(map(str, a)) + "\n", timeout=timeout)


def by_split(a, k):
    """Independent check: try every split x from the left + (k - x) from the right with running sums."""
    left = 0
    right = sum(a[len(a) - k:])          # x = 0: all k from the right
    best = right
    for x in range(1, k + 1):
        left += a[x - 1]
        right -= a[len(a) - k + x - 1]
        best = max(best, left + right)
    return best


@pytest.mark.parametrize("a, k, want, why", [
    ([1, 2, 3, 4, 5, 6, 1], 3, 12, "the example: 6 + 5 + 1"),
    ([6, 1, 1, 100, 1, 5], 3, 106, "greedy takes 6, 5, 1 = 12; the best is the right three, 100 + 1 + 5"),
    ([2, 2, 2], 2, 4, "all equal"),
    ([9, 7, 7, 9, 7, 7, 9], 7, 55, "k = n: take everything (the block left behind is empty)"),
    ([5], 1, 5, "one card"),
    ([1, 1000, 1], 1, 1, "k = 1: only an end card can be taken, never the middle one"),
    ([10, 1, 1, 1, 10], 2, 20, "one from each end"),
    ([3, 8, 1, 1, 1], 2, 11, "both from the left"),
])
def test_examples(a, k, want, why):
    got = ask(a, k)
    assert got == [str(want)], f"a = {a}, k = {k}: expected {want}, got {got} ({why})."


def test_window_size_is_n_minus_k():
    got = ask([1, 79, 80, 1, 1, 1, 200, 1], 3)
    assert got == ["202"], (
        f"Expected 202 (take 1 from the left and 200 + 1 from the right), got {got}. The block you LEAVE has "
        "n - k cards; a window of size k finds the cards in the middle, which you are not allowed to take.")


def test_k_equals_n_no_crash():
    got = ask([4, 5, 6], 3)
    assert got == ["15"], (
        f"k = n = 3: take all cards, 15; got {got}. The block left behind has size 0 and sum 0: make sure the "
        "window code does not index a[-1] or divide by zero for that case.")


def test_random_small():
    rng = random.Random(57)
    for _ in range(25):
        n = rng.randint(1, 15)
        a = [rng.randint(1, 20) for _ in range(n)]
        k = rng.randint(1, n)
        got = ask(a, k)
        assert got == [str(by_split(a, k))], f"a = {a}, k = {k}: expected {by_split(a, k)}, got {got}."


def test_large():
    rng = random.Random(5700)
    n = 200000
    a = [rng.randint(1, 10**4) for _ in range(n)]
    k = 100000
    want = by_split(a, k)
    got = ask(a, k, timeout=8)
    assert got == [str(want)], (
        f"n = 200000, k = 100000: expected {want}, got {got}. If it timed out, you re-sum every window or every "
        "split with sum() (O(n k)); slide the window, adding one card and removing one.")
