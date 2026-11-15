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
from bisect import bisect_right


def ask(values, s, timeout=10):
    return run(f"{len(values)} {s}\n" + " ".join(map(str, values)) + "\n", timeout=timeout)


def brute(values, s):
    best = 0
    for i in range(len(values)):
        total = 0
        for j in range(i, len(values)):
            total += values[j]
            if total >= s:
                if best == 0 or j - i + 1 < best:
                    best = j - i + 1
                break
    return best


def by_binary_search(values, s):
    P = [0]
    for x in values:
        P.append(P[-1] + x)
    best = 0
    for r in range(1, len(P)):
        l = bisect_right(P, P[r] - s) - 1      # largest l with P[r] - P[l] >= s
        if l >= 0 and (best == 0 or r - l < best):
            best = r - l
    return best


@pytest.mark.parametrize("values, s, expected, why", [
    ([2, 3, 1, 2, 4, 3], 7, 2, "the example: 4 3"),
    ([1, 4, 4], 4, 1, "one element equal to s: sum exactly s counts (use >=, not >)"),
    ([1, 1, 1, 1, 1], 11, 0, "even the whole array is too small: print 0, not n + 1"),
    ([1, 1, 1, 1, 1], 5, 5, "only the whole array works: length n is a real answer"),
    ([1, 1, 1, 10], 10, 1, "the new 10 allows three cuts in a row: shrink with while, not if"),
    ([5], 5, 1, "one element"),
    ([5], 6, 0, "one element, too small"),
    ([1, 2, 3, 4, 5], 11, 3, "3 4 5"),
    ([10000] * 3, 10**9, 0, "s much larger than the total"),
])
def test_examples(values, s, expected, why):
    got = ask(values, s)
    assert got == [str(expected)], f"Input {values}, s = {s}: expected {expected}, got {got} ({why})."


def test_random_small_against_brute_force():
    rng = random.Random(28)
    for _ in range(50):
        n = rng.randint(1, 15)
        values = [rng.randint(1, 6) for _ in range(n)]
        s = rng.randint(1, 30)
        got = ask(values, s)
        expected = brute(values, s)
        assert got == [str(expected)], (
            f"Input {values}, s = {s}: expected {expected}, got {got}. Record r - l + 1 while the sum is still "
            ">= s, then shrink; print 0 when nothing reaches s.")


def test_large_long_answer():
    n = 200000
    got = ask([1] * n, 100000, timeout=10)
    assert got == ["100000"], (
        f"200000 ones with s = 100000: the answer is 100000; got {got}. A timeout means you restart the sum at "
        "every start position: keep ONE window and move l only forward.")


def test_large_random():
    rng = random.Random(2828)
    values = [rng.randint(1, 10**4) for _ in range(200000)]
    for s in (37000, 5 * 10**7):
        expected = by_binary_search(values, s)
        got = ask(values, s, timeout=10)
        assert got == [str(expected)], f"Large random array, s = {s}: expected {expected}, got {got}."
