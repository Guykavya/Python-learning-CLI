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
    ([3, 6, 1, 8, 2, 9, 2, 3, 3], "the example"),
    ([1], "one element"),
    ([2, 1], "two elements"),
    ([1, 2, 3, 4, 5], "already sorted"),
    ([5, 4, 3, 2, 1], "reverse sorted"),
    ([4, 4, 4, 4], "all equal"),
    ([-3, 5, -3, 0, 5, 0], "duplicates and negatives"),
])
def test_examples(values, why):
    got = ask(values)
    assert got == model(values), f"Input {values}: expected {model(values)}, got {got} ({why}). Elements equal to the pivot must stay in the answer exactly once each."


def test_random_small():
    rng = random.Random(44)
    for _ in range(80):
        values = [rng.randint(-4, 4) for _ in range(rng.randint(1, 14))]
        assert ask(values) == model(values), f"Input {values}: expected {model(values)}."


def test_large_random():
    rng = random.Random(45)
    values = [rng.randint(-10**9, 10**9) for _ in range(200000)]
    assert ask(values) == model(values), "Wrong or too slow on 200000 random numbers."


def test_large_sorted():
    values = list(range(200000))
    assert ask(values) == model(values), (
        "200000 already sorted numbers: a first/last-element pivot recurses 200000 deep (RecursionError) and takes O(n^2). Use a random pivot.")


def test_large_reversed():
    values = list(range(200000, 0, -1))
    assert ask(values) == model(values), "200000 reversed numbers: use a random or median-of-three pivot."


def test_large_all_equal():
    values = [7] * 200000
    assert ask(values) == model(values), (
        "200000 equal numbers: with a two-way partition (< and >=) every split puts all elements on one side. Use a three-way split.")


def test_large_few_distinct():
    rng = random.Random(46)
    values = [rng.randint(0, 2) for _ in range(200000)]
    assert ask(values) == model(values), "Only 3 different values: the equal part must not be recursed into."
