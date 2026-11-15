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


def ask(grid, timeout=10):
    lines = [f"{len(grid)} {len(grid[0])}"] + [" ".join(map(str, row)) for row in grid]
    return run("\n".join(lines) + "\n", timeout=timeout)


def numbered(r, c):
    return [[i * c + j + 1 for j in range(c)] for i in range(r)]


def by_sorting(grid):
    """Sort the cells by diagonal, then by row: increasing on odd diagonals, decreasing on even ones."""
    r, c = len(grid), len(grid[0])
    cells = [(i + j, i if (i + j) % 2 else -i, grid[i][j]) for i in range(r) for j in range(c)]
    cells.sort()
    return [" ".join(str(v) for _, _, v in cells)]


@pytest.mark.parametrize("r, c, expected, why", [
    (3, 4, "1 2 5 9 6 3 4 7 10 11 8 12", "the example: diagonals 1 | 2 5 | 9 6 3 | 4 7 10 | 11 8 | 12"),
    (3, 3, "1 2 4 7 5 3 6 8 9", "a square grid: diagonal 1 goes DOWN (2 then 4), diagonal 2 goes UP (7 5 3)"),
    (4, 2, "1 2 3 5 4 6 7 8", "a tall grid: at d = 3 the down-walk starts at column min(3, 1) = 1, row 2"),
    (2, 4, "1 2 5 6 3 4 7 8", "a wide grid: at d = 2 the up-walk starts at row min(2, 1) = 1, column 1"),
    (1, 1, "1", "one cell"),
    (1, 5, "1 2 3 4 5", "one row: every diagonal has one cell"),
    (5, 1, "1 2 3 4 5", "one column: every diagonal has one cell"),
    (2, 2, "1 2 3 4", "2 x 2: up (1), down (2 3), up (4)"),
])
def test_shapes(r, c, expected, why):
    got = ask(numbered(r, c))
    assert got == [expected], f"{r} x {c} grid numbered 1..{r * c} row by row: expected {expected!r}, got {got} ({why})."


def test_values_not_positions():
    grid = [[-5, 0], [7, 1000000000]]
    got = ask(grid)
    assert got == ["-5 0 7 1000000000"], f"Grid -5 0 / 7 1000000000: expected '-5 0 7 1000000000', got {got}."


def test_random_shapes():
    rng = random.Random(35)
    for _ in range(30):
        r, c = rng.randint(1, 7), rng.randint(1, 7)
        grid = [[rng.randint(-99, 99) for _ in range(c)] for _ in range(r)]
        got = ask(grid)
        expected = by_sorting(grid)
        assert got == expected, (
            f"{r} x {c} grid {grid}: expected {expected}, got {got}. Even d: start at row min(d, r-1) and go up; "
            "odd d: start at column min(d, c-1) and go down.")


def test_large():
    rng = random.Random(3535)
    r, c = 500, 499
    grid = [[rng.randint(-10**9, 10**9) for _ in range(c)] for _ in range(r)]
    expected = by_sorting(grid)
    got = ask(grid, timeout=10)
    assert got == expected, (
        "A 500 x 499 grid: the order is wrong somewhere (or values are missing). Check the start of the diagonals "
        "that are cut by the bottom and right edges.")
