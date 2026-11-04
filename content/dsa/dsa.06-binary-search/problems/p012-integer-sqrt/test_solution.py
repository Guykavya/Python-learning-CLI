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
import math


def test_no_shortcuts():
    tree = ast.parse(SOLUTION.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in ("isqrt", "sqrt", "pow", "math"):
            raise AssertionError(f"Do not use {node.id}: write the binary search on r yourself.")
        if isinstance(node, ast.Attribute) and node.attr in ("isqrt", "sqrt", "pow"):
            raise AssertionError(f"Do not use .{node.attr}: write the binary search on r yourself.")
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            raise AssertionError("No imports are needed. Write the binary search on r yourself.")
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
            e = node.right
            assert isinstance(e, ast.Constant) and e.value == 2, "Only ** 2 is allowed; ** 0.5 is a float and loses precision near 10^18."


def ask(ns, timeout=10):
    return run(f"{len(ns)}\n" + "".join(f"{n}\n" for n in ns), timeout=timeout)


def test_small():
    ns = list(range(0, 70))
    got = ask(ns)
    for n, g in zip(ns, got):
        assert g == str(math.isqrt(n)), f"sqrt of {n}: expected {math.isqrt(n)}, got {g}. Check perfect squares and the numbers just below them (off by one between 'first False' and 'last True')."
    assert len(got) == len(ns), "Print exactly one line per query."


def test_perfect_squares_and_neighbours():
    ns = []
    for k in (10**9, 10**9 - 1, 999999937, 123456789, 3037000500, 2):
        ns += [k * k - 1, k * k, k * k + 1]
    ns += [10**18, 10**18 - 1]
    got = ask(ns)
    for n, g in zip(ns, got):
        assert g == str(math.isqrt(n)), f"sqrt of {n}: expected {math.isqrt(n)}, got {g}. Near 10^18 a float (** 0.5) is not exact; use integer comparison mid * mid <= n."


def test_many_big_queries():
    rng = random.Random(11)
    ns = [rng.randint(0, 10**18) for _ in range(10000)]
    got = ask(ns)
    assert got == [str(math.isqrt(n)) for n in ns], "Wrong answer on a big random query. Also check that every query takes about 60 steps, not a loop up to the answer."
