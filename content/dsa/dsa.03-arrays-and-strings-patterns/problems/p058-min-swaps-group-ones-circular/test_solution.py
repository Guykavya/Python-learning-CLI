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


def ask(a, timeout=10):
    return run(f"{len(a)}\n" + " ".join(map(str, a)) + "\n", timeout=timeout)


def brute(a):
    n, m = len(a), sum(a)
    if m == 0:
        return 0
    return m - max(sum(a[(s + t) % n] for t in range(m)) for s in range(n))


def by_doubled_prefix(a):
    """Independent check: prefix sums over the array written twice; windows of size m start at 0..n-1."""
    n, m = len(a), sum(a)
    if m == 0:
        return 0
    b = a + a
    P = [0]
    for x in b:
        P.append(P[-1] + x)
    return m - max(P[s + m] - P[s] for s in range(n))


@pytest.mark.parametrize("a, want, why", [
    ([0, 1, 0, 1, 1, 0, 0], 1, "the example"),
    ([0, 1, 1, 1, 0, 0, 1, 1, 0], 2, "5 ones; the best window of 5 already holds 3"),
    ([1, 1, 0, 0, 1], 0, "circular: the last 1 touches the first two, so they are already grouped"),
    ([0, 0, 0], 0, "no ones at all: nothing to group (and no window of size 0 to slide)"),
    ([1, 1, 1], 0, "all ones: already grouped"),
    ([1], 0, "a single 1"),
    ([0], 0, "a single 0"),
    ([1, 0, 1, 0, 1, 0], 1, "alternating: any window of 3 holds 2 ones"),
])
def test_examples(a, want, why):
    got = ask(a)
    assert got == [str(want)], f"a = {a}: expected {want}, got {got} ({why})."


def test_wrap_around_counts():
    got = ask([1, 0, 0, 0, 1, 1])
    assert got == ["0"], (
        f"a = [1, 0, 0, 0, 1, 1]: expected 0, got {got}. Around the circle the block 1 1 | 1 (positions 5, 6, 1) "
        "is already together. A straight (non-circular) window cannot see it: use a[i % n].")


def test_window_size_is_number_of_ones():
    got = ask([1, 0, 0, 1, 0, 0, 0, 1, 0, 0])
    assert got == ["2"], (
        f"Expected 2, got {got}. There are 3 ones, so the window has size 3 (the size of the final block), and no "
        "window of size 3 holds more than 1 one.")


def test_random_small_against_brute_force():
    rng = random.Random(58)
    for _ in range(30):
        a = [rng.randint(0, 1) for _ in range(rng.randint(1, 20))]
        got = ask(a)
        assert got == [str(brute(a))], f"a = {a}: expected {brute(a)}, got {got}."


def test_large():
    rng = random.Random(5800)
    a = [1 if rng.random() < 0.5 else 0 for _ in range(200000)]
    want = by_doubled_prefix(a)
    got = ask(a, timeout=8)
    assert got == [str(want)], (
        f"n = 200000 with about 100000 ones: expected {want}, got {got}. If it timed out, you re-count each window "
        "(O(n m)); slide it: add the entering value and subtract the leaving one.")


def test_large_block_split_by_the_end():
    n = 200000
    a = [1] * 1000 + [0] * (n - 2000) + [1] * 1000
    got = ask(a, timeout=8)
    assert got == ["0"], f"2000 ones split across the end of the array form one block around the circle: 0 swaps; got {got}."
