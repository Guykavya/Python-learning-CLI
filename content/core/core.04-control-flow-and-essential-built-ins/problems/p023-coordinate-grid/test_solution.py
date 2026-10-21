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

import pytest


def grid(r, c):
    return [" ".join(f"({i},{j})" for j in range(1, c + 1)) for i in range(1, r + 1)]


def test_example():
    assert run("2\n3\n") == ["(1,1) (1,2) (1,3)", "(2,1) (2,2) (2,3)"], (
        "Two rows of three cells, counting from 1. Does each row start with an empty line string?")


@pytest.mark.parametrize("r, c", [(1, 1), (1, 4), (4, 1), (3, 3), (10, 2)])
def test_shapes(r, c):
    got = run(f"{r}\n{c}\n")
    assert got == grid(r, c), f"{r} rows by {c} columns: expected {grid(r, c)}, got {got}"


@pytest.mark.parametrize("r, c", [(0, 3), (3, 0), (0, 0)])
def test_empty(r, c):
    assert run(f"{r}\n{c}\n") == ["(empty grid)"], "A grid with 0 rows or 0 columns prints (empty grid)."
