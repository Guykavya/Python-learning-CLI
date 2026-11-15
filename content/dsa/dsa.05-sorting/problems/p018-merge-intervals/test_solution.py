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

def ask(pairs, timeout=10):
    return run(f"{len(pairs)}\n" + "\n".join(f"{l} {r}" for l, r in pairs) + "\n", timeout=timeout)


def brute_merge(pairs):
    """Independent model: union-find over pairs that share a point (closed intervals)."""
    n = len(pairs)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(n):
        for j in range(i + 1, n):
            if max(pairs[i][0], pairs[j][0]) <= min(pairs[i][1], pairs[j][1]):
                parent[find(i)] = find(j)
    groups = {}
    for i, (l, r) in enumerate(pairs):
        g = groups.setdefault(find(i), [l, r])
        g[0] = min(g[0], l)
        g[1] = max(g[1], r)
    return sorted(tuple(g) for g in groups.values())


def fmt(pairs):
    return [f"{l} {r}" for l, r in pairs]


@pytest.mark.parametrize("pairs, why", [
    ([(1, 3), (8, 10), (2, 6), (15, 18)], "the example: unsorted input"),
    ([(1, 2), (2, 3)], "touching intervals merge"),
    ([(1, 10), (2, 3), (4, 5)], "nested intervals: the end must stay 10 (use max)"),
    ([(5, 5)], "one interval, a single point"),
    ([(1, 2), (3, 4)], "gap of 1: no merge"),
    ([(4, 6), (1, 5), (7, 9), (6, 7)], "chain of touching and overlapping"),
    ([(2, 2), (2, 2), (2, 2)], "identical intervals"),
])
def test_examples(pairs, why):
    got = ask(pairs)
    assert got == fmt(brute_merge(pairs)), f"Input {pairs}: expected {fmt(brute_merge(pairs))}, got {got} ({why}). Sort by start; extend with max(cr, r); l <= cr means merge."


def test_random_small():
    rng = random.Random(22)
    for _ in range(80):
        pairs = []
        for _ in range(rng.randint(1, 9)):
            l = rng.randint(0, 20)
            pairs.append((l, l + rng.randint(0, 5)))
        assert ask(pairs) == fmt(brute_merge(pairs)), f"Input {pairs}: expected {fmt(brute_merge(pairs))}."


def test_large():
    rng = random.Random(23)
    pairs = []
    for _ in range(200000):
        l = rng.randint(0, 10**9 - 1000)
        pairs.append((l, l + rng.randint(0, 1000)))
    want = []
    cl, cr = None, None
    for l, r in sorted(pairs):
        if cl is None:
            cl, cr = l, r
        elif l <= cr:
            cr = max(cr, r)
        else:
            want.append((cl, cr))
            cl, cr = l, r
    want.append((cl, cr))
    assert ask(pairs) == fmt(want), "Wrong or too slow on 200000 intervals: sort once, then one sweep."
