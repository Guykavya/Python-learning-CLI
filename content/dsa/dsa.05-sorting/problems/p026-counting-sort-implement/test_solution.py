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

def ask(values, k, timeout=10):
    return run(f"{len(values)} {k}\n" + " ".join(map(str, values)) + "\n", timeout=timeout)


def model(values):
    return [" ".join(map(str, sorted(values)))]


@pytest.mark.parametrize("values, k, why", [
    ([3, 1, 5, 1, 0, 3, 3, 2], 5, "the example: the value k itself occurs"),
    ([0], 0, "k = 0: a single possible value"),
    ([4, 4, 4], 4, "all equal and equal to k"),
    ([2, 1, 0], 2, "reversed"),
    ([0, 1, 2, 3], 3, "already sorted"),
    ([7, 0, 7], 10, "values that never occur between"),
])
def test_examples(values, k, why):
    got = ask(values, k)
    assert got == model(values), f"Input {values}, k={k}: expected {model(values)}, got {got} ({why}). The count array needs k + 1 slots."


def test_large_small_range():
    rng = random.Random(32)
    values = [rng.randint(0, 1000) for _ in range(500000)]
    assert ask(values, 1000) == model(values), "Wrong or too slow on 500000 values in 0..1000."


def test_few_values_huge_range():
    rng = random.Random(33)
    values = [rng.choice([0, 10**6, 999999, 5]) for _ in range(50)]
    assert ask(values, 10**6) == model(values), "k = 10^6 with few values: a count array of size k + 1 is fine; do not loop n * k times."
