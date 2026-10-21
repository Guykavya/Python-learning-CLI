import ast
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


def called_names() -> set[str]:
    """Names of every plain function call in your solution, e.g. {'print', 'int', 'input'}."""
    tree = ast.parse(SOLUTION.read_text())
    return {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}



import pytest


def test_example():
    got = run("7\n3\n")
    expected = ["7 x 1 = 7", "7 x 2 = 14", "7 x 3 = 21"]
    assert got == expected, (
        f"Input 7 and 3: expected {expected}, got {got}. Use range(1, k + 1) and the exact format 'n x i = p'.")


def test_negative():
    got = run("-4\n2\n")
    expected = ["-4 x 1 = -4", "-4 x 2 = -8"]
    assert got == expected, f"Input -4 and 2: expected {expected}, got {got}."


def test_zero_n():
    got = run("0\n2\n")
    expected = ["0 x 1 = 0", "0 x 2 = 0"]
    assert got == expected, f"Input 0 and 2: expected {expected}, got {got}. n = 0 still prints k lines."


def test_single_line():
    got = run("9\n1\n")
    assert got == ["9 x 1 = 9"], f"Input 9 and 1: expected exactly one line '9 x 1 = 9', got {got}."


@pytest.mark.parametrize("n, k", [(12, 10), (-1000, 100), (1, 100)])
def test_many_lines(n, k):
    expected = [f"{n} x {i} = {n * i}" for i in range(1, k + 1)]
    got = run(f"{n}\n{k}\n")
    assert len(got) == k, f"Input {n} and {k}: expected {k} lines, got {len(got)}. Is n * k the last line?"
    assert got == expected, (
        f"Input {n} and {k}: first expected line {expected[0]!r}, last {expected[-1]!r}; "
        f"you printed {got[0]!r} ... {got[-1]!r}.")
