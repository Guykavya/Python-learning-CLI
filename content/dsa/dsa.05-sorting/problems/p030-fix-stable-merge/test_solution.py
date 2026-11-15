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

def ask(rows, timeout=10):
    return run(f"{len(rows)}\n" + "".join(f"{k} {l}\n" for k, l in rows), timeout=timeout)


def model(rows):
    return [f"{k} {l}" for k, l in sorted(rows, key=lambda r: r[0])]


@pytest.mark.parametrize("rows, why", [
    ([(2, "ann"), (1, "bob"), (2, "cy"), (1, "dee"), (3, "eli")], "the example"),
    ([(1, "a"), (1, "b")], "bug 1: equal keys must keep input order"),
    ([(1, "a"), (2, "b")], "bug 2: leftovers of the right half must be appended"),
    ([(2, "a"), (1, "b")], "right half finishes first"),
    ([(3, "a"), (2, "b"), (1, "c")], "bug 3: three records, no record may disappear"),
    ([(5, "x")], "one record"),
    ([(1, "a"), (1, "b"), (1, "c"), (1, "d")], "all keys equal: output equals input"),
])
def test_examples(rows, why):
    got = ask(rows)
    assert got == model(rows), f"Input {rows}: expected {model(rows)}, got {got} ({why})."


def test_random_small():
    rng = random.Random(36)
    for _ in range(80):
        rows = [(rng.randint(0, 3), "abcdefghij"[i]) for i in range(rng.randint(1, 9))]
        assert ask(rows) == model(rows), (
            f"Input {rows}: expected {model(rows)}. Check: ties (<=), both leftovers, and the slices a[:mid] / a[mid:].")


def test_large_few_keys():
    rng = random.Random(37)
    rows = [(rng.randint(0, 4), f"w{i}") for i in range(100000)]
    assert ask(rows) == model(rows), "100000 records with five different keys: equal keys must keep their input order."
