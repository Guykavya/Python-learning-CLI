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



def build(n, rng, spread):
    m = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            up = m[i - 1][j] if i else 0
            left = m[i][j - 1] if j else 0
            m[i][j] = max(up, left) + rng.randint(0, spread)
    return m


def check(m, k, why):
    n = len(m)
    flat = sorted(v for row in m for v in row)
    want = flat[k - 1]
    got = run(f"{n} {k}\n" + "".join(" ".join(map(str, row)) + "\n" for row in m))
    assert got == [str(want)], (
        f"{n}x{n} matrix, k = {k}: expected {want}, got {got} ({why}). "
        "Binary search the VALUE; count entries <= v with a staircase walk; the answer is the first v with count >= k.")


def test_no_shortcuts():
    check_banned(names=("sorted", "heapq", "nsmallest"), attrs=("sort",), no_in=False, what="the search")


def test_example():
    m = [[1, 5, 9], [10, 11, 13], [12, 13, 15]]
    for k in range(1, 10):
        check(m, k, "the example, every k")


def test_one_cell():
    check([[-7]], 1, "a 1x1 matrix")


def test_duplicates():
    check([[2, 2], [2, 2]], 3, "all equal: any k gives 2")
    check([[1, 1, 3], [1, 3, 3], [3, 3, 3]], 4, "k lands inside a block of equal values")
    check([[1, 2], [1, 3]], 2, "the second smallest is a duplicate of the smallest")


def test_random_small():
    rng = random.Random(71)
    for _ in range(25):
        n = rng.randint(2, 6)
        m = build(n, rng, 3)
        check(m, rng.randint(1, n * n), "random small matrix")


def test_large():
    rng = random.Random(72)
    m = build(700, rng, 1500)
    check(m, 245000, "700x700 matrix: flattening and sorting is banned, count with a walk")
    check(m, 1, "k = 1")
    check(m, 700 * 700, "k = n * n")
