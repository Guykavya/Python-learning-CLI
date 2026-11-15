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


def ask(values, ops, timeout=10):
    text = f"{len(values)}\n" + " ".join(map(str, values)) + f"\n{len(ops)}\n"
    text += "".join(f"{l} {r}\n" for l, r in ops)
    return run(text, timeout=timeout)


def brute(values, ops):
    a = list(values)
    for l, r in ops:
        a[l - 1:r] = list(reversed(a[l - 1:r]))
    return [" ".join(map(str, a))]


def test_example():
    got = ask([1, 2, 3, 4, 5, 6, 7], [(1, 7), (1, 3), (4, 7)])
    assert got == ["5 6 7 1 2 3 4"], f"Expected '5 6 7 1 2 3 4' for the example, got {got}."


@pytest.mark.parametrize("values, ops, why", [
    ([1, 2, 3, 4], [(1, 4)], "even length: i and j cross without meeting. Stop when i < j fails, not when i == j"),
    ([1, 2, 3, 4, 5], [(1, 5)], "odd length: the middle stays"),
    ([9], [(1, 1)], "a part of one element does not change"),
    ([1, 2, 3, 4, 5, 6], [(2, 5)], "only the middle part moves; positions 1 and 6 stay"),
    ([1, 2, 3, 4, 5, 6], [(2, 3)], "a part of two elements: one swap"),
    ([1, 2, 3], [(1, 3), (1, 3)], "reversing twice gives the original back"),
    ([5, 5, 1, 1], [(1, 4), (2, 3)], "repeated values"),
])
def test_small(values, ops, why):
    got = ask(values, ops)
    assert got == brute(values, ops), f"Array {values}, operations {ops}: expected {brute(values, ops)}, got {got} ({why})."


def test_random_small():
    rng = random.Random(7)
    for _ in range(15):
        n = rng.randint(1, 10)
        values = [rng.randint(0, 9) for _ in range(n)]
        ops = []
        for _ in range(rng.randint(1, 5)):
            l = rng.randint(1, n)
            ops.append((l, rng.randint(l, n)))
        got = ask(values, ops)
        assert got == brute(values, ops), (
            f"Array {values}, operations {ops}: expected {brute(values, ops)}, got {got}. "
            "If the part comes out unchanged, your loop swaps each pair twice (it runs past the middle).")


def test_large_rotation():
    n, k = 200000, 12345
    values = list(range(1, n + 1))
    ops = [(1, n), (1, k), (k + 1, n)]
    expected = values[-k:] + values[:-k]
    got = ask(values, ops, timeout=10)
    assert got == [" ".join(map(str, expected))], (
        "Three reversals on 200000 elements should rotate the array right by 12345. Check the 1-based to 0-based "
        "conversion (i = l - 1, j = r - 1) and that each reversal is O(length), not O(length^2).")
