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



def model(lines):
    s, out = [], []
    for ln in lines:
        op, v = ln.split()
        v = int(v)
        if op == "add":
            s.insert(bisect_left(s, v), v)
        elif op == "remove":
            i = bisect_left(s, v)
            if i < len(s) and s[i] == v:
                del s[i]
                out.append("1")
            else:
                out.append("0")
        elif op == "count_le":
            out.append(str(bisect_right(s, v)))
        elif op == "kth":
            out.append(str(s[v - 1]) if 1 <= v <= len(s) else "none")
        else:
            i = bisect_left(s, v)
            out.append(str(s[i]) if i < len(s) else "none")
    return out


def check(lines, why):
    got = run(f"{len(lines)}\n" + "\n".join(lines) + "\n")
    want = model(lines)
    assert len(got) == len(want), f"{why}: expected {len(want)} output lines, got {len(got)}. add prints nothing; every other command prints one line."
    for i, (g, w_) in enumerate(zip(got, want)):
        assert g == w_, f"{why}: output line {i + 1} is {g}, expected {w_}. Check lower/upper bound, removal of ONE copy, and the 1-based kth."


def test_no_shortcuts():
    check_banned(names=("bisect", "bisect_left", "bisect_right", "insort", "insort_left", "insort_right", "sorted", "heapq"),
                 attrs=("sort", "index", "count", "remove"), no_in=False, what="the sorted multiset")


def test_example():
    check(["add 5", "add 3", "add 5", "count_le 5", "remove 5", "count_le 5", "kth 2", "ceil 4", "remove 9"], "the example")


def test_one_copy_only():
    check(["add 2", "add 2", "add 2", "remove 2", "count_le 2", "remove 2", "remove 2", "remove 2", "count_le 2", "kth 1"], "remove deletes exactly one copy")


def test_empty_and_bounds():
    check(["kth 1", "ceil 0", "count_le 0", "remove 0", "add 7", "kth 2", "kth 1", "ceil 8", "ceil 7", "ceil -100", "count_le 6", "count_le 7"], "empty set and the ends")


def test_random_small():
    rng = random.Random(81)
    for _ in range(20):
        lines = []
        for _ in range(60):
            op = rng.choice(["add", "add", "remove", "count_le", "kth", "ceil"])
            lines.append(f"{op} {rng.randint(1, 8) if op == 'kth' else rng.randint(0, 9)}")
        check(lines, "random small commands")


def test_large():
    rng = random.Random(82)
    lines = []
    for _ in range(100000):
        op = rng.choice(["add", "add", "remove", "count_le", "kth", "ceil"])
        if op == "kth":
            lines.append(f"kth {rng.randint(1, 20000)}")
        else:
            lines.append(f"{op} {rng.randint(-10**9, 10**9) if rng.random() < 0.5 else rng.randint(0, 1000)}")
    check(lines, "100000 commands: a linear scan per command is too slow")
