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


def feed(numbers):
    return f"{len(numbers)}\n" + "".join(f"{x}\n" for x in numbers)


def test_example():
    got = run(feed([1, 2, 3, 4, 0]))
    assert got == ["even 3", "odd 2"], (
        f"Numbers 1 2 3 4 0: expected ['even 3', 'odd 2'], got {got}. Zero is even. "
        "Print both lines once, after the loop.")


def test_negative_odds():
    got = run(feed([-3, -4, -7]))
    assert got == ["even 1", "odd 2"], (
        f"Numbers -3 -4 -7: expected ['even 1', 'odd 2'], got {got}. Negative odd numbers are odd. "
        "Use x % 2 == 0 for even and else for odd.")


def test_no_numbers():
    got = run("0\n")
    assert got == ["even 0", "odd 0"], (
        f"Count 0: expected ['even 0', 'odd 0'], got {got}. Print both counters even when the loop never runs.")


def test_zero_only():
    got = run(feed([0]))
    assert got == ["even 1", "odd 0"], f"The single number 0: expected ['even 1', 'odd 0'], got {got}. Zero is even."


@pytest.mark.parametrize("numbers", [
    [5] * 7,
    [-1, -2, -3, -1000000000, 1000000000, 999999999],
    list(range(-500, 500)),
])
def test_mixed(numbers):
    e = sum(1 for x in numbers if x % 2 == 0)
    expected = [f"even {e}", f"odd {len(numbers) - e}"]
    got = run(feed(numbers))
    assert got == expected, f"{len(numbers)} numbers (starting {numbers[:4]}): expected {expected}, got {got}."
