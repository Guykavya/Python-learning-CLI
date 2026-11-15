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


def brute(a, k):
    total = 0
    for i in range(len(a)):
        seen = set()
        for j in range(i, len(a)):
            seen.add(a[j])
            if len(seen) == k:
                total += 1
            elif len(seen) > k:
                break
    return total


def two_left_pointers(a, k):
    """Independent O(n) check: l1 = first start with <= k distinct, l2 = first start with <= k-1 distinct."""
    c1, c2 = {}, {}
    l1 = l2 = 0
    total = 0
    for x in a:
        c1[x] = c1.get(x, 0) + 1
        c2[x] = c2.get(x, 0) + 1
        while len(c1) > k:
            y = a[l1]
            c1[y] -= 1
            if c1[y] == 0:
                del c1[y]
            l1 += 1
        while len(c2) >= k:
            y = a[l2]
            c2[y] -= 1
            if c2[y] == 0:
                del c2[y]
            l2 += 1
        total += l2 - l1
    return total


@pytest.mark.parametrize("a, k, want, why", [
    ([1, 2, 1, 2, 3], 2, 7, "the example"),
    ([1, 2, 1, 3, 4], 3, 3, "[1,2,1,3], [2,1,3], [1,3,4]"),
    ([5], 1, 1, "one element, one subarray"),
    ([7, 7, 7], 1, 6, "all equal and k = 1: every one of the 3*4/2 = 6 subarrays counts"),
    ([1, 2, 3], 3, 1, "k = n with all distinct: only the whole array"),
    ([1, 1, 2], 3, 0, "k is larger than the number of distinct values: 0"),
    ([1, 2, 3, 4], 1, 4, "k = 1 with all distinct: only the single elements"),
])
def test_examples(a, k, want, why):
    got = ask(a, k)
    assert got == [str(want)], f"a = {a}, k = {k}: expected {want}, got {got} ({why})."


def test_not_at_most():
    got = ask([1, 2, 1, 2, 3], 2)
    assert got != ["12"], (
        "You printed 12, the number of subarrays with AT MOST 2 distinct values. Subtract the ones with at most "
        "k - 1 = 1 distinct value (5 of them).")
    assert got == ["7"], f"Expected 7, got {got}."


def test_zero_counts_deleted():
    got = ask([1, 2, 3, 1, 1], 2)
    assert got == ["4"], (
        f"Expected 4 ([1,2], [2,3], [3,1], [3,1,1]), got {got}. When a value's count drops "
        "to 0 it has left the window: delete its key, or len(count) keeps counting it.")


def test_counting_only_full_windows_is_wrong():
    got = ask([1, 2, 1, 2], 2)
    assert got == ["6"], (
        f"Expected 6, got {got}. Adding 1 whenever the window has exactly k values misses the shorter windows "
        "inside it: [2,1], [1,2] also end at the same right. Use atMost(k) - atMost(k - 1).")


def test_random_small_against_brute_force():
    rng = random.Random(44)
    for _ in range(25):
        n = rng.randint(1, 25)
        a = [rng.randint(1, 5) for _ in range(n)]
        k = rng.randint(1, 5)
        got = ask(a, k)
        assert got == [str(brute(a, k))], f"a = {a}, k = {k}: expected {brute(a, k)}, got {got}."


def test_large_all_equal():
    n = 200000
    got = ask([3] * n, 1, timeout=8)
    assert got == [str(n * (n + 1) // 2)], (
        f"All 200000 values equal, k = 1: every subarray counts, n(n+1)/2 = {n * (n + 1) // 2}; got {got}. "
        "If this timed out, you start a new scan at every left end (O(n^2)); move both ends forward only.")


def test_large_all_distinct():
    n, k = 200000, 1000
    got = ask(list(range(1, n + 1)), k, timeout=8)
    assert got == [str(n - k + 1)], (
        f"All values distinct: only the windows of length exactly k = {k} qualify, so n - k + 1 = {n - k + 1}; "
        f"got {got}.")


def test_large_random():
    rng = random.Random(4400)
    a = [rng.randint(1, 40) for _ in range(200000)]
    k = 12
    want = two_left_pointers(a, k)
    got = ask(a, k, timeout=8)
    assert got == [str(want)], f"Random array, n = 200000, k = {k}: expected {want}, got {got}."
