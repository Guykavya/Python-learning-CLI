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
    got = run(f"{len(a)} {k}\n" + " ".join(map(str, a)) + "\n", timeout=timeout)
    return got[0].split() if got else []


def brute(a, k):
    return [str(max(a[i:i + k])) for i in range(len(a) - k + 1)]


def by_blocks(a, k):
    """Independent O(n) check: cut the array into blocks of k; a window = suffix max of one block + prefix max of the next."""
    n = len(a)
    pre = a[:]
    suf = a[:]
    for i in range(1, n):
        if i % k:
            pre[i] = max(pre[i - 1], a[i])
    for i in range(n - 2, -1, -1):
        if (i + 1) % k:
            suf[i] = max(suf[i + 1], a[i])
    return [str(max(suf[i], pre[i + k - 1])) for i in range(n - k + 1)]


@pytest.mark.parametrize("a, k, why", [
    ([1, 3, -1, -3, 5, 3, 6, 7], 3, "the example"),
    ([4], 1, "one element"),
    ([5, 1, 2, 3], 1, "k = 1: every element is its own maximum"),
    ([5, 1, 2, 3], 4, "k = n: one window, the maximum of everything"),
    ([9, 8, 7, 6, 5], 2, "decreasing: the maximum leaves through the FRONT every step"),
    ([1, 2, 3, 4, 5], 2, "increasing: every new element clears the deque from the back"),
    ([-5, -1, -7, -3], 2, "all negative values"),
    ([2, 2, 2, 1, 1], 3, "equal values: duplicates must not break the window"),
])
def test_examples(a, k, why):
    got = ask(a, k)
    assert got == brute(a, k), f"a = {a}, k = {k}: expected {' '.join(brute(a, k))}, got {' '.join(got)} ({why})."


def test_front_leaves_the_window():
    a, k = [10, 1, 1, 1, 1], 2
    got = ask(a, k)
    assert got == ["10", "1", "1", "1"], (
        f"a = {a}, k = 2: expected 10 1 1 1, got {' '.join(got)}. The 10 is only in the first window. Remove the "
        "front index once it is <= i - k.")


def test_count_of_outputs():
    a, k = [3, 1, 4, 1, 5, 9, 2, 6], 3
    got = ask(a, k)
    assert len(got) == len(a) - k + 1, (
        f"Expected {len(a) - k + 1} maxima (n - k + 1), got {len(got)}. Start printing when i = k - 1, the end of "
        "the first full window.")


def test_random_small_against_brute_force():
    rng = random.Random(53)
    for _ in range(25):
        n = rng.randint(1, 30)
        a = [rng.randint(-5, 5) for _ in range(n)]
        k = rng.randint(1, n)
        got = ask(a, k)
        assert got == brute(a, k), f"a = {a}, k = {k}: expected {' '.join(brute(a, k))}, got {' '.join(got)}."


def test_large_wide_window():
    rng = random.Random(5300)
    a = [rng.randint(-10**9, 10**9) for _ in range(200000)]
    k = 100000
    got = ask(a, k, timeout=8)
    assert got == by_blocks(a, k), (
        "n = 200000, k = 100000: the maxima differ. If it timed out, you call max() on every window (O(n k)); "
        "a monotonic deque does each step in O(1) on average.")


def test_large_decreasing():
    n, k = 200000, 50000
    a = list(range(n, 0, -1))
    got = ask(a, k, timeout=8)
    assert got == [str(n - i) for i in range(n - k + 1)], (
        "A decreasing array: each window's maximum is its first element. The front of the deque must leave "
        "as the window moves.")
