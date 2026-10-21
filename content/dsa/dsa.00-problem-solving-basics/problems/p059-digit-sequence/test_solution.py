import subprocess
import sys
from pathlib import Path

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

import ast
import random

import pytest

# Test-side brute force: the real sequence, built with str (only the TEST may do this).
SEQUENCE = "".join(str(i) for i in range(1, 3000))


def kth_digit(k):
    """Independent block-skipping check for huge k (uses str inside the test only)."""
    length, count, start = 1, 9, 1
    while k > length * count:
        k -= length * count
        length, count, start = length + 1, count * 10, start * 10
    number = start + (k - 1) // length
    return str(number)[(k - 1) % length]


@pytest.mark.parametrize("k, why", [
    (1, "the first digit"),
    (9, "the last one-digit number"),
    (10, "the first digit of 10 (first 2-digit block position)"),
    (11, "the second digit of 10"),
    (12, "the first digit of 11"),
    (189, "the last digit of 99, the end of the 2-digit block"),
    (190, "the first digit of 100"),
    (191, "the middle digit of 100"),
    (192, "the last digit of 100"),
    (2889, "the last digit of 999, the end of the 3-digit block"),
    (2890, "the first digit of 1000"),
])
def test_boundaries(k, why):
    expected = SEQUENCE[k - 1]
    got = run(f"{k}\n")
    assert got == [expected], (
        f"k = {k}: expected {expected}, got {got}. Note: {why}. Off-by-one errors live at block "
        "edges: use k > length * count (not >=) and (k - 1) // length, (k - 1) % length.")


def test_random_small_against_real_sequence():
    rng = random.Random(59)
    for k in rng.sample(range(1, 8000), 12):
        expected = SEQUENCE[k - 1]
        got = run(f"{k}\n")
        assert got == [expected], f"k = {k}: expected {expected}, got {got}."


@pytest.mark.parametrize("k", [10 ** 18, 10 ** 18 - 1, 123456789012345678, 10 ** 12])
def test_huge_k_fast(k):
    expected = kth_digit(k)
    got = run(f"{k}\n", timeout=3)
    assert got == [expected], (
        f"k = {k}: expected {expected}, got {got}. Skip whole blocks at once; walking through numbers "
        "one at a time is far too slow.")


def test_no_strings():
    tree = ast.parse(SOLUTION.read_text())
    for node in ast.walk(tree):
        assert not isinstance(node, ast.JoinedStr), "Do not use f-strings here. Use // and % only."
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in {"str", "repr", "format", "list"}, (
                f"Do not use {node.func.id}(). Extract the digit with // and %.")
