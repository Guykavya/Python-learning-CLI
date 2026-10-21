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


@pytest.mark.parametrize("nums", [[4, 9, -3, 2, 0], [10, 9, 100], [-5, -2, -9], [0], [7, 7, 7], [0, 0, -1]])
def test_stats(nums):
    want = [f"Count: {len(nums)}", f"Sum: {sum(nums)}", f"Min: {min(nums)}", f"Max: {max(nums)}",
            f"Spread: {max(nums) - min(nums)}"]
    got = run(" ".join(map(str, nums)) + "\n")
    assert got == want, (
        f"For {nums} expected {want}, got {got}. Compare as numbers (convert with int), not as text; "
        "and a minimum of 0 is still a real minimum.")


def test_empty():
    assert run("\n") == ["Count: 0", "Sum: 0", "Min: none", "Max: none"], (
        "No numbers: min and max need default=None, and there is no Spread line.")


def test_uses_builtins():
    for name in ("sum", "min", "max"):
        assert calls(name) >= 1, f"Use the built-in {name}() in this problem."
