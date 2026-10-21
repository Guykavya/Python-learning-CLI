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


def expected_rows(n: int) -> list[str]:
    rows = []
    for i in range(1, n + 1):
        rows.append(" ".join(str(j) for j in range(1, i + 1)))
    return rows


def test_four():
    got = run("4\n")
    assert got == ["1", "1 2", "1 2 3", "1 2 3 4"], (
        f"For n=4 expected 4 rows ending in 1, 2, 3, 4. Got {got}. "
        "Row i should hold the numbers 1 to i.")


def test_one():
    got = run("1\n")
    assert got == ["1"], f"For n=1 expected a single line '1', got {got}."


def test_zero_prints_nothing():
    got = run("0\n")
    assert got == [], f"For n=0 nothing should be printed, got {got}. Do not print an empty triangle header or blank text."


@pytest.mark.parametrize("n", [2, 5, 10, 12, 30])
def test_sizes(n):
    expected = expected_rows(n)
    got = run(f"{n}\n")
    assert len(got) == n, f"For n={n} expected exactly {n} lines, got {len(got)}."
    assert got == expected, (
        f"For n={n} the rows do not match. Expected first rows {expected[:3]} ... last {expected[-1]!r}, "
        f"got first {got[:3]} ... last {got[-1:]}. Use single spaces between numbers.")


def test_no_leading_space():
    r = subprocess.run([sys.executable, str(SOLUTION)], input="3\n", capture_output=True, text=True, timeout=10)
    for line in r.stdout.splitlines():
        assert not line.startswith(" "), (
            f"The line {line!r} starts with a space. Add the space before each number except the first.")
