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
    ([170, 45, 75, 90, 802, 24, 2, 66], "the example"),
    ([0], "a single zero: no digit pass is needed"),
    ([0, 0, 0], "all zeros"),
    ([5, 3, 9, 1], "single digits"),
    ([10, 9, 100, 1], "numbers with different lengths"),
    ([10**9, 999999999, 0, 1], "the largest allowed value has 10 digits"),
    ([21, 12, 11, 22, 21], "duplicates, tens digit decides after the ones pass"),
])
def test_examples(values, why):
    got = ask(values)
    assert got == model(values), f"Input {values}: expected {model(values)}, got {got} ({why}). Least significant digit first, each pass stable."


def test_random_small():
    rng = random.Random(34)
    for _ in range(60):
        values = [rng.randint(0, 1000) for _ in range(rng.randint(1, 15))]
        assert ask(values) == model(values), f"Input {values}: expected {model(values)}."


def test_large():
    rng = random.Random(35)
    values = [rng.randint(0, 10**9) for _ in range(200000)]
    assert ask(values) == model(values), "Wrong or too slow on 200000 numbers. Up to 10 passes of O(n) each is fast enough."
