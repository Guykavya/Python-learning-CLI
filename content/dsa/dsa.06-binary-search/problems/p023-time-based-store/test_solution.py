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
    times, vals, out = {}, {}, []
    for ln in lines:
        p = ln.split()
        if p[0] == "set":
            times.setdefault(p[1], []).append(int(p[3]))
            vals.setdefault(p[1], []).append(p[2])
        else:
            ts = times.get(p[1], [])
            i = bisect_right(ts, int(p[2]))
            out.append(vals[p[1]][i - 1] if i else "NONE")
    return out


def check(lines, why):
    got = run(f"{len(lines)}\n" + "\n".join(lines) + "\n")
    want = model(lines)
    assert len(got) == len(want), f"One output line per get: expected {len(want)}, got {len(got)}."
    for i, (g, w_) in enumerate(zip(got, want)):
        assert g == w_, f"Get number {i + 1}: expected {w_}, got {g} ({why}). A get at time t returns the set with the largest time <= t (upper bound), NONE if there is none."


def test_no_shortcuts():
    check_banned(names=("bisect", "bisect_left", "bisect_right", "insort"), attrs=(), no_in=False)


def test_example():
    check(["set love high 10", "set love low 20", "get love 5", "get love 10", "get love 15", "get love 25", "get fun 3"], "the example")


def test_two_keys_interleaved():
    check(["set a x 1", "set b y 2", "set a z 5", "get a 4", "get b 1", "get b 2", "get b 99", "get a 5", "get c 5"], "keys must not mix their histories")


def test_exact_times():
    check(["set k v1 3", "set k v2 6", "set k v3 9", "get k 3", "get k 6", "get k 9", "get k 2", "get k 8"], "a get exactly at a set time returns that set (<=, not <)")


def test_large_single_key():
    rng = random.Random(15)
    lines = [f"set key v{i} {10 * i + 10}" for i in range(100000)]
    lines += [f"get key {rng.randint(0, 1000020)}" for _ in range(100000)]
    check(lines, "100000 sets and 100000 gets on one key: a scan per get needs 10^10 steps")


def test_large_mixed():
    rng = random.Random(16)
    lines, clock = [], {}
    for _ in range(150000):
        k = f"k{rng.randint(0, 5)}"
        if rng.random() < 0.5:
            clock[k] = clock.get(k, 0) + rng.randint(1, 5)
            lines.append(f"set {k} w{rng.randint(0, 999)} {clock[k]}")
        else:
            lines.append(f"get {k} {rng.randint(0, clock.get(k, 0) + 3)}")
    check(lines, "mixed commands on a few keys")
