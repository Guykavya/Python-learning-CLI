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


def brute(values):
    """Check every start position; used only by the tests."""
    best_len, best_start = 0, 0
    for s in range(len(values)):
        e = s
        while e + 1 < len(values) and values[e + 1] > values[e]:
            e += 1
        if e - s + 1 > best_len:
            best_len, best_start = e - s + 1, s + 1
    return [f"length {best_len}", f"from {best_start} to {best_start + best_len - 1}"]


def ask(values, timeout=10):
    return run(f"{len(values)}\n" + "".join(f"{v}\n" for v in values), timeout=timeout)


@pytest.mark.parametrize("values, expected, why", [
    ([5, 1, 2, 3, 2, 4, 6, 7], ["length 4", "from 5 to 8"],
     "the longest streak ends at the last number; check the best AFTER every number, not only when a streak breaks"),
    ([42], ["length 1", "from 1 to 1"], "n = 1: a single value is a streak of length 1"),
    ([3, 3, 3, 3], ["length 1", "from 1 to 1"], "equal values do not continue a streak (strictly greater)"),
    ([9, 7, 5, 3, 1], ["length 1", "from 1 to 1"], "strictly decreasing: every streak has length 1, report the earliest"),
    ([1, 2, 3, 4, 5], ["length 5", "from 1 to 5"], "the whole input is one streak"),
    ([1, 2, 0, 5, 6, 1], ["length 3", "from 3 to 5"], "example from the statement"),
    ([1, 3, 2, 4, 0, 9], ["length 2", "from 1 to 2"], "three streaks of length 2: report the earliest (use >, not >=)"),
    ([-5, -3, -4, -1, 0, -10], ["length 3", "from 3 to 5"], "negative values work the same way"),
    ([1, 2, 2, 3], ["length 2", "from 1 to 2"], "2 then 2 breaks the streak"),
])
def test_examples(values, expected, why):
    got = ask(values)
    assert got == expected, f"Values {values}: expected {expected}, got {got}. Note: {why}."


def test_random_against_brute_force():
    rng = random.Random(58)
    for _ in range(10):
        values = [rng.randint(-5, 5) for _ in range(rng.randint(1, 25))]
        expected = brute(values)
        got = ask(values)
        assert got == expected, f"Values {values}: expected {expected}, got {got}."


def test_large_input():
    rng = random.Random(580)
    values = [rng.randint(1, 1000) for _ in range(100000)]
    # Plant a long streak in the middle so the answer is unique and known.
    for i in range(50):
        values[60000 + i] = 2000 + i
    values[59999] = 5000
    values[60050] = 0
    expected = brute(values)
    got = ask(values, timeout=10)
    assert got == expected, (
        f"n = 100000: expected {expected}, got {got}. Use a single pass and keep only a few variables.")


def test_no_lists():
    tree = ast.parse(SOLUTION.read_text())
    for node in ast.walk(tree):
        assert not isinstance(node, (ast.List, ast.ListComp)), (
            "Do not store the numbers in a list. Keep only the previous value and a few counters.")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in {"list", "sorted"}, (
                f"Do not use {node.func.id}(). Read each number once and keep only what you need.")
