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
    a = list(values)
    swaps = 0
    for i in range(len(a) - 1):
        m = i
        for j in range(i + 1, len(a)):
            if a[j] < a[m]:
                m = j
        if m != i:
            a[i], a[m] = a[m], a[i]
            swaps += 1
    return [" ".join(map(str, a)), str(swaps)]


@pytest.mark.parametrize("values, why", [
    ([64, 25, 12, 22, 11], "the example: 4 swaps"),
    ([5], "one element, no swaps"),
    ([1, 2, 3, 4], "already sorted: 0 swaps, a swap with itself does not count"),
    ([4, 3, 2, 1], "reversed: 2 swaps"),
    ([2, 2, 1, 3], "duplicates: leftmost minimum"),
    ([3, 3, 3], "all equal: no swaps"),
    ([2, 1, 2, 1], "ties inside the unsorted part"),
])
def test_examples(values, why):
    got = ask(values)
    assert got == model(values), (
        f"Input {values}: expected {model(values)}, got {got} ({why}). "
        "Swap only when the minimum is not already at position i, and use < so the leftmost minimum wins.")


def test_random_small():
    rng = random.Random(4)
    for _ in range(40):
        values = [rng.randint(-3, 3) for _ in range(rng.randint(1, 9))]
        assert ask(values) == model(values), f"Input {values}: expected {model(values)}. Count only real swaps (m != i)."


def test_large_quadratic_but_fast_enough():
    rng = random.Random(5)
    values = [rng.randint(-10**9, 10**9) for _ in range(2000)]
    assert ask(values) == model(values), "n = 2000 should take about a second for an O(n^2) loop; do not call a.index/min inside heavier loops."
