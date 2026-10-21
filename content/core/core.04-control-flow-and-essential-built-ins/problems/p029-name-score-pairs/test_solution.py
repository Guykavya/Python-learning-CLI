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

def test_example():
    assert run("Asha Ravi Meena\n82 91 77\n") == ["Asha: 82", "Ravi: 91", "Meena: 77", "Average: 83.3"], (
        "Pair the names and scores in order and show the average with 1 decimal.")


def test_more_names():
    assert run("A B C\n1 2\n") == ["Mismatch: 3 names, 2 scores"], (
        "zip stops at the shorter line without complaint. Compare the lengths before looping.")


def test_more_scores():
    assert run("A\n1 2 3\n") == ["Mismatch: 1 names, 3 scores"], "Check both directions of mismatch."


def test_empty():
    assert run("\n\n") == ["No data"], "Both lines empty: nothing to average, and no division by zero."


def test_single():
    assert run("Zed\n0\n") == ["Zed: 0", "Average: 0.0"], "One pair with a score of 0."


def test_uses_zip():
    assert calls("zip") >= 1, "Use zip(names, scores) to walk the two lines together."
