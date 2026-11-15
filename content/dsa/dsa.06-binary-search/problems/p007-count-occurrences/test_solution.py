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



def expect(a, x):
    return bisect_right(a, x) - bisect_left(a, x)


def ask(a, qs, timeout=10):
    return run(f"{len(a)}\n{' '.join(map(str, a))}\n{len(qs)}\n{' '.join(map(str, qs))}\n", timeout=timeout)


def test_no_shortcuts():
    check_banned(names=('bisect', 'bisect_left', 'bisect_right', 'insort', 'insort_left', 'insort_right'), attrs=('index', 'count'), no_in=True)


def compare(a, qs, why):
    got = ask(a, qs)
    want = [expect(a, x) for x in qs]
    assert len(got) == len(want), f"Print exactly one line per query: expected {len(want)} lines, got {len(got)}."
    for x, g, wnt in zip(qs, got, want):
        assert g == str(wnt), (
            f"Array {a if len(a) < 30 else '(long array)'}, query {x}: expected {wnt}, got {g} ({why}). count = upper_bound(x) - lower_bound(x); a missing value gives 0.")


@pytest.mark.parametrize("a, qs, why", [

    ([1, 2, 2, 2, 5, 7, 7, 9], [2, 7, 3, 9, 1, 0, 10], "the example and the ends"),
    ([4], [4, 5], "one element"),
    ([6] * 50, [6, 5, 7], "all equal: a walk from one hit would take 50 steps, and 100000 in the big test"),
    ([1, 1, 2, 3, 3, 3, 4], [1, 2, 3, 4], "blocks of different lengths"),
])
def test_cases(a, qs, why):
    compare(a, qs, why)


def test_exhaustive_small():
    rng = random.Random(5)
    for _ in range(40):
        n = rng.randint(1, 8)
        a = sorted(rng.randint(0, 9) for _ in range(n))
        compare(a, list(range(-1, 11)), "a tiny random array; every value from -1 to 10 is asked, so every position and both ends are covered")


def test_large():
    rng = random.Random(7)
    a = sorted(rng.randint(0, 300) for _ in range(100000))
    qs = [rng.randint(-5, 305) for _ in range(100000)]
    compare(a, qs, "100000 numbers and 100000 queries: a linear scan per query needs about 10^10 steps and times out")
