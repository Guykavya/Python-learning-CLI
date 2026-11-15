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


def inversions(a):
    return sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] > a[j])


def model(values):
    return [" ".join(map(str, sorted(values))), str(inversions(values))]


@pytest.mark.parametrize("values, why", [
    ([4, 3, 2, 10, 12, 1], "the example: 8 shifts"),
    ([1], "one element"),
    ([1, 2, 3], "already sorted: 0 shifts"),
    ([3, 2, 1], "reversed: 3 shifts"),
    ([2, 2, 2], "all equal: equal values must NOT be shifted"),
    ([2, 1, 2, 1], "duplicates"),
])
def test_examples(values, why):
    got = ask(values)
    assert got == model(values), (
        f"Input {values}: expected {model(values)}, got {got} ({why}). "
        "Shift only while a[j] > key (strictly), and check j >= 0 first.")


def test_random_small():
    rng = random.Random(6)
    for _ in range(40):
        values = [rng.randint(-4, 4) for _ in range(rng.randint(1, 10))]
        assert ask(values) == model(values), f"Input {values}: expected {model(values)}."


def test_large_reversed():
    n = 3000
    values = list(range(n, 0, -1))
    assert ask(values) == [" ".join(map(str, range(1, n + 1))), str(n * (n - 1) // 2)], (
        "Reversed input needs n(n-1)/2 shifts. 3000 elements is about 4.5 million shifts: fine for a plain while loop, too slow if you slice or insert in a list inside the loop.")
