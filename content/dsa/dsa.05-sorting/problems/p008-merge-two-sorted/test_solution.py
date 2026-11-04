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

def ask(a, b, timeout=10):
    return run(f"{len(a)} {len(b)}\n" + " ".join(map(str, a)) + "\n" + " ".join(map(str, b)) + "\n", timeout=timeout)


def model(a, b):
    out = " ".join(map(str, sorted(a + b)))
    return [out] if out else []


@pytest.mark.parametrize("a, b, why", [
    ([1, 4, 7], [2, 4, 9, 10], "the example"),
    ([], [3], "first list empty"),
    ([3], [], "second list empty"),
    ([], [], "both empty: print nothing"),
    ([1, 2, 3], [4, 5, 6], "all of a before b: copy the leftover of b"),
    ([4, 5, 6], [1, 2, 3], "all of b before a: copy the leftover of a"),
    ([2, 2, 2], [2, 2], "all equal"),
    ([-5, 0, 7], [-6, 0, 8], "negatives and a shared 0"),
])
def test_examples(a, b, why):
    got = ask(a, b)
    assert got == model(a, b), f"a={a} b={b}: expected {model(a, b)}, got {got} ({why}). Copy what is left of BOTH lists after the main loop."


def test_random_small():
    rng = random.Random(8)
    for _ in range(40):
        a = sorted(rng.randint(-5, 5) for _ in range(rng.randint(0, 8)))
        b = sorted(rng.randint(-5, 5) for _ in range(rng.randint(0, 8)))
        assert ask(a, b) == model(a, b), f"a={a} b={b}: expected {model(a, b)}."


def test_large():
    rng = random.Random(9)
    a = sorted(rng.randint(0, 10**9) for _ in range(200000))
    b = sorted(rng.randint(0, 10**9) for _ in range(200000))
    assert ask(a, b) == model(a, b), "Wrong or too slow for 200000 + 200000 values. Use two pointers; a.pop(0) is O(n) each time."
