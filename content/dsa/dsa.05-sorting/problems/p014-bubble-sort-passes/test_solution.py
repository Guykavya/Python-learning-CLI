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
    passes = swaps = 0
    while True:
        passes += 1
        swapped = False
        for i in range(len(a) - 1):
            if a[i] > a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]
                swaps += 1
                swapped = True
        if not swapped:
            return [str(passes), str(swaps), " ".join(map(str, a))]


@pytest.mark.parametrize("values, why", [
    ([5, 1, 4, 2, 8], "the example: 3 passes, 4 swaps"),
    ([1, 2, 3], "sorted: 1 pass (the clean one), 0 swaps"),
    ([7], "one element"),
    ([3, 2, 1], "reversed: 3 passes, 3 swaps"),
    ([2, 2, 2], "all equal: no swaps (use >, not >=)"),
    ([2, 1, 2, 1], "duplicates"),
    ([2, 3, 4, 5, 1], "one small value at the end moves one place per pass: 5 passes"),
])
def test_examples(values, why):
    got = ask(values)
    assert got == model(values), (
        f"Input {values}: expected {model(values)}, got {got} ({why}). "
        "Count a pass before checking whether it swapped anything, and swap only when a[i] > a[i+1].")


def test_random_small():
    rng = random.Random(14)
    for _ in range(40):
        values = [rng.randint(-4, 4) for _ in range(rng.randint(1, 10))]
        assert ask(values) == model(values), f"Input {values}: expected {model(values)}."


def test_large():
    n = 2000
    values = list(range(n, 0, -1))
    assert ask(values) == [str(n), str(n * (n - 1) // 2), " ".join(map(str, range(1, n + 1)))], "Reversed 2000 numbers: n passes and n(n-1)/2 swaps."
