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



def check(m, qs, why):
    r, c = len(m), len(m[0])
    text = f"{r} {c}\n" + "".join(" ".join(map(str, row)) + "\n" for row in m) + f"{len(qs)}\n" + " ".join(map(str, qs)) + "\n"
    got = run(text)
    pos = {v: (i, j) for i, row in enumerate(m) for j, v in enumerate(row)}
    want = [f"{pos[x][0]} {pos[x][1]}" if x in pos else "-1 -1" for x in qs]
    assert len(got) == len(want), f"Print exactly one line per query: expected {len(want)}, got {len(got)}."
    for x, g, w_ in zip(qs, got, want):
        assert g == w_, (
            f"{r}x{c} matrix, query {x}: expected {w_}, got {g} ({why}). "
            "Virtual index i: row = i // C, col = i % C (C is the number of COLUMNS).")


def test_no_shortcuts():
    check_banned(names=("bisect", "bisect_left", "bisect_right", "insort"), attrs=("index", "count"), no_in=True)


def test_example():
    m = [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]]
    check(m, [3, 13, 60, 1, 0, 61, 20, 23], "the example plus the ends")


def test_shapes():
    check([[5]], [5, 4, 6], "a 1x1 matrix")
    check([[1, 4, 9, 12, 20]], [1, 20, 9, 10], "one row")
    check([[2], [4], [6], [8]], [2, 8, 4, 5], "one column: C = 1, row = i")
    check([[1, 2], [3, 4], [5, 6]], list(range(0, 8)), "tall matrix with every value asked")


def test_large():
    rng = random.Random(6)
    r, c = 700, 700
    vals = sorted(rng.sample(range(-10**9, 10**9), r * c))
    m = [vals[i * c:(i + 1) * c] for i in range(r)]
    qs = [rng.choice(vals) if rng.random() < 0.5 else rng.randint(-10**9, 10**9) for _ in range(100000)]
    check(m, qs, "490000 cells and 100000 queries: a scan per query times out")
