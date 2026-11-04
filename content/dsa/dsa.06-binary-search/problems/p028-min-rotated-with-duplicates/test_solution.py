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



def model(a):
    return min(a)


def ask(arrays, timeout=10):
    text = f"{len(arrays)}\n" + "".join(f"{len(a)}\n{' '.join(map(str, a))}\n" for a in arrays)
    return run(text, timeout=timeout)


def rot(base, r):
    return base[r:] + base[:r]


def test_no_shortcuts():
    check_banned(names=("min", "max", "sorted"), attrs=("sort",), no_in=False, what="the search")


def test_example():
    assert ask([[3, 3, 1, 3], [1, 1, 0, 1, 1], [2, 2, 2]]) == ["1", "0", "2"], "The example: [3,3,1,3] -> 1, [1,1,0,1,1] -> 0, [2,2,2] -> 2."


def test_tricky_cases():
    cases = [[3, 1, 3, 3, 3], [3, 3, 1, 3], [1, 3, 3], [10, 1, 10, 10, 10], [2, 2, 2, 0, 2], [1, 1, 1, 0, 1, 1, 1], [5], [4, 4], [9, 4], [4, 9],
             [1, 0, 1, 1, 1], [1, 1, 1, 1, 0], [0, 1, 1, 1, 1]]
    got = ask(cases)
    for c, g in zip(cases, got):
        assert g == str(model(c)), f"{c}: expected {model(c)}, got {g}. When a[mid] == a[hi] do NOT move lo or hi to mid: just drop a[hi] (hi -= 1)."


def test_random_small():
    rng = random.Random(61)
    arrays = []
    for _ in range(1500):
        n = rng.randint(1, 10)
        base = sorted(rng.randint(0, 4) for _ in range(n))
        arrays.append(rot(base, rng.randrange(n)))
    got = ask(arrays)
    assert len(got) == len(arrays), "Print one line per test case."
    for c, g in zip(arrays, got):
        assert g == str(model(c)), f"{c}: expected {model(c)}, got {g}. With duplicates the case a[mid] == a[hi] needs hi -= 1."


def test_large():
    n = 100000
    a = [1] * n
    a[n // 2 + 3] = 0
    big = [rot(sorted([1] * (n - 1) + [0]), 54321), a, [7] * n]
    got = ask(big)
    assert got == ["0", "0", "7"], "Big arrays with almost all values equal: answers 0, 0, 7. A loop that moves by one is still fine here, but check the equal case."
