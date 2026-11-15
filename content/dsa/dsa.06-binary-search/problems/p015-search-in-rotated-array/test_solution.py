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
from bisect import bisect_left, bisect_right


import ast


def check_banned(names=(), attrs=(), no_in=False, what="the search"):
    tree = ast.parse(SOLUTION.read_text())
    bad = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in names:
            bad.add(node.id)
        if isinstance(node, ast.Attribute) and (node.attr in attrs or node.attr in names):
            bad.add("." + node.attr)
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mods = [a.name for a in node.names] + [getattr(node, "module", None) or ""]
            for m in mods:
                if m.split(".")[0] in names:
                    bad.add(m)
        if no_in and isinstance(node, ast.Compare) and any(isinstance(o, (ast.In, ast.NotIn)) for o in node.ops):
            bad.add("the `in` operator")
    assert not bad, (
        f"This problem is about writing {what} yourself: found {sorted(bad)} in your code. "
        "Write the loop with lo, hi and mid by hand; library shortcuts are not allowed here.")



def rot(base, r):
    return base[r:] + base[:r]


def check(a, qs, why):
    got = run(f"{len(a)}\n{' '.join(map(str, a))}\n{len(qs)}\n{' '.join(map(str, qs))}\n")
    pos = {v: i for i, v in enumerate(a)}
    want = [pos.get(x, -1) for x in qs]
    assert len(got) == len(want), f"Print exactly one line per query: expected {len(want)} lines, got {len(got)}."
    for x, g, w_ in zip(qs, got, want):
        assert g == str(w_), (
            f"Array {a if len(a) < 30 else '(long array)'}, query {x}: expected {w_}, got {g} ({why}). "
            "Find the sorted half (a[lo] <= a[mid]) and test the target against its bounds.")


def test_no_shortcuts():
    check_banned(names=("bisect", "bisect_left", "bisect_right", "insort"), attrs=("index", "count"), no_in=True)


def test_example():
    check([6, 7, 9, 15, 19, 2, 3, 4], [3, 19, 8, 6, 4, 2, 9, 100], "the example")


def test_every_rotation_small():
    for n in range(1, 8):
        base = list(range(10, 10 + 2 * n, 2))
        for r in range(n):
            check(rot(base, r), list(range(8, 12 + 2 * n)), f"rotation {r} of {base}")


def test_two_elements():
    check([9, 3], [3, 9, 5], "two elements with the drop in the middle: use a[lo] <= a[mid], not <")


def test_large():
    rng = random.Random(4)
    base = sorted(rng.sample(range(0, 400000), 100000))
    a = rot(base, 31337)
    qs = [rng.randint(-5, 400005) for _ in range(100000)]
    check(a, qs, "100000 numbers and 100000 queries: a linear scan times out")
