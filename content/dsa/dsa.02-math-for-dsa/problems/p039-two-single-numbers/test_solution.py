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


def ask(values, timeout=10):
    return run(f"{len(values)}\n" + " ".join(map(str, values)) + "\n", timeout=timeout)


@pytest.mark.parametrize("values, want, why", [
    ([1, 2, 1, 3, 2, 5], "3 5", "the example"),
    ([7, 4], "4 7", "no pairs: print smaller first"),
    ([0, 9, 9, 6], "0 6", "one single is 0"),
    ([5, 1, 5, 2], "1 2", "the singles differ only in bit 0 and bit 1: x = 3, low bit is 1"),
    ([6, 2, 6, 3], "2 3", "a ^ b = 1: only bit 0 differs"),
    ([8, 1, 8, 4], "1 4", "singles 1 and 4 have the same parity, so splitting by `& 1` would fail"),
    ([2, 4, 2, 6, 4, 10], "6 10", "6 and 10 are both even: splitting by `& 1` puts them together"),
    ([2 ** 29, 5, 7, 5], "7 536870912", "large value with a high bit"),
    ([3, 3, 9, 12], "9 12", "9 = 1001, 12 = 1100"),
])
def test_examples(values, want, why):
    got = ask(values)
    assert got == [want], f"values {values}: expected `{want}`, got {got} ({why})."


def make(rng, k, hi):
    nums = rng.sample(range(0, hi), k + 2)
    a, b = nums[0], nums[1]
    values = nums[2:] * 2 + [a, b]
    rng.shuffle(values)
    return values, f"{min(a, b)} {max(a, b)}"


def test_random_small():
    rng = random.Random(39)
    for _ in range(40):
        values, want = make(rng, rng.randint(0, 8), 64)
        got = ask(values)
        assert got == [want], (
            f"values {values}: expected `{want}`, got {got}. Split by the lowest SET bit of the total XOR (`x & -x`), "
            "not by a fixed bit, and print the smaller value first.")


def test_large():
    rng = random.Random(390)
    values, want = make(rng, 499999, 2 ** 30)
    got = ask(values, timeout=6)
    assert got == [want], (
        f"10^6 numbers: expected `{want}`, got {got}. If this timed out, do not use `count` or `in` on a list: two passes "
        "of XOR are enough.")
