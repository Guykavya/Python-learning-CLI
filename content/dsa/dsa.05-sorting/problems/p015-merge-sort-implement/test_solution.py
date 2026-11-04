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


import ast

BANNED = ('sorted', 'heapq', 'bisect')


def test_no_builtin_sorting():
    tree = ast.parse(SOLUTION.read_text())
    bad = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in BANNED:
            bad.add(node.id)
        if isinstance(node, ast.Attribute) and (node.attr == "sort" or node.attr in BANNED):
            bad.add("." + node.attr)
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mods = [a.name for a in node.names] + [getattr(node, "module", None) or ""]
            for m in mods:
                if m.split(".")[0] in BANNED:
                    bad.add(m)
    assert not bad, (
        f"This problem is about BUILDING the sort yourself: found {sorted(bad)} in your code. "
        "Write the loops and comparisons by hand; sorted(), .sort(), heapq and bisect are not allowed here.")

def ask(values, timeout=10):
    return run(f"{len(values)}\n" + " ".join(map(str, values)) + "\n", timeout=timeout)


def model(values):
    return [" ".join(map(str, sorted(values)))]


@pytest.mark.parametrize("values, why", [
    ([38, 27, 43, 3, 9, 82, 10], "the example"),
    ([1], "one element"),
    ([2, 1], "two elements"),
    ([1, 2, 3, 4, 5], "already sorted"),
    ([5, 4, 3, 2, 1], "reverse sorted"),
    ([7, 7, 7, 7], "all equal"),
    ([3, -1, 3, -1, 0], "duplicates and negatives"),
    ([5, 1, 4], "odd length: halves of size 1 and 2"),
])
def test_examples(values, why):
    got = ask(values)
    assert got == model(values), f"Input {values}: expected {model(values)}, got {got} ({why}). Check the base case and the leftovers after the merge loop."


def test_random_small():
    rng = random.Random(15)
    for _ in range(60):
        values = [rng.randint(-5, 5) for _ in range(rng.randint(1, 15))]
        assert ask(values) == model(values), f"Input {values}: expected {model(values)}."


def test_large():
    rng = random.Random(16)
    values = [rng.randint(-10**9, 10**9) for _ in range(200000)]
    assert ask(values) == model(values), "Wrong or too slow on 200000 numbers. Merge sort is O(n log n): do not use pop(0) or list.insert in the merge."


def test_large_sorted_and_reversed():
    values = list(range(200000))
    assert ask(values) == model(values), "Sorted input of 200000."
    assert ask(values[::-1]) == model(values), "Reversed input of 200000."
