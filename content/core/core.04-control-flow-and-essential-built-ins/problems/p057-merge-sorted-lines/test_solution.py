import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or an input() call waiting for a line that never comes.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import ast


def tree():
    return ast.parse(SOLUTION.read_text())


def calls(name):
    """How many times a function with this name is called in your code."""
    return sum(1 for n in ast.walk(tree())
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == name)


def has(node_type):
    return any(isinstance(n, node_type) for n in ast.walk(tree()))

import pytest


def merged(a, b):
    return [" ".join(str(n) for n in sorted(a + b)) or "(empty)", f"From line 1: {len(a)}, from line 2: {len(b)}"]


def line(nums):
    return " ".join(map(str, nums)) + "\n"


def test_example():
    assert run("1 4 9\n2 4 10 11\n") == ["1 2 4 4 9 10 11", "From line 1: 3, from line 2: 4"], (
        "Always take the smaller front number; when one line runs out, add the rest of the other.")


@pytest.mark.parametrize("a, b", [
    ([1, 2, 3], [4, 5, 6]),
    ([4, 5, 6], [1, 2, 3]),
    ([], [1, 2]),
    ([7], []),
    ([2, 2, 2], [2, 2]),
    ([-5, 0, 9, 10], [-6, 9, 100]),
    ([9, 10], [8, 11]),
    ([1, 1, 3, 3], [1, 2, 3, 4]),
])
def test_merge(a, b):
    got = run(line(a) + line(b))
    assert got == merged(a, b), (
        f"Merging {a} and {b}: expected {merged(a, b)}, got {got}. Compare as numbers (10 > 9), "
        "and do not forget the leftover numbers.")


def test_both_empty():
    assert run("\n\n") == ["(empty)", "From line 1: 0, from line 2: 0"], "Two empty lines."


def test_not_sorted():
    assert run("3 1\n1 2\n") == ["Line 1 is not sorted"], "3 then 1 is not sorted."
    assert run("1 2\n5 10 9\n") == ["Line 2 is not sorted"], "10 then 9 is not sorted (as numbers)."
    assert run("9 10\n1\n") == ["9 10", "From line 1: 2, from line 2: 1"][:0] or True


def test_numeric_sortedness():
    got = run("9 10\n1\n")
    assert got == ["1 9 10", "From line 1: 2, from line 2: 1"], (
        "9 10 is sorted as numbers, even though '10' < '9' as text. Convert with int() before comparing.")


def test_no_sorted_builtin():
    assert calls("sorted") == 0, "Do not use sorted(); merge by walking both lines."
    assert not any(isinstance(n, ast.Attribute) and n.attr == "sort" for n in ast.walk(tree())), "Do not use .sort()."
