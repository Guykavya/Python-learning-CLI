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


def expected_for(grid):
    rows = {i for i, row in enumerate(grid) if 0 in row}
    cols = {j for row in grid for j, v in enumerate(row) if v == 0}
    return [" ".join("0" if (i in rows or j in cols) else str(v) for j, v in enumerate(row))
            for i, row in enumerate(grid)]


def test_example():
    grid = [[1, 2, 0, 4], [5, 6, 7, 8], [0, 1, 2, 3]]
    got = ask(grid)
    assert got == ["0 0 0 0", "0 6 0 8", "0 0 0 0"], (
        f"The example: expected rows '0 0 0 0', '0 6 0 8', '0 0 0 0'; got {got}. If row 2 became all zeros, "
        "a NEW zero cleared its row: find the original zeros first, then write.")


@pytest.mark.parametrize("grid, expected, why", [
    ([[1, 2], [3, 4]], ["1 2", "3 4"], "no zeros: nothing changes"),
    ([[0]], ["0"], "a 1 x 1 grid holding 0"),
    ([[1, 0, 1]], ["0 0 0"], "one row: the zero clears the whole row"),
    ([[1], [0], [1]], ["0", "0", "0"], "one column: the zero clears the whole column"),
    ([[1, 1, 1], [1, 0, 1], [1, 1, 1]], ["1 0 1", "0 0 0", "1 0 1"], "a zero in the middle: a plus sign, the corners stay"),
    ([[0, 1, 1], [1, 1, 1], [1, 1, 1]], ["0 0 0", "0 1 1", "0 1 1"],
     "a corner zero. Scanning in place, the new zeros in row 1 and column 1 would wipe out everything"),
    ([[1, 2, 3, 4], [5, 0, 7, 8], [9, 10, 11, 0]], ["1 0 3 0", "0 0 0 0", "0 0 0 0"],
     "two zeros in a 3 x 4 grid: columns 2 and 4, rows 2 and 3"),
    ([[-1, 5], [7, -3]], ["-1 5", "7 -3"], "negative numbers are not zeros"),
])
def test_small(grid, expected, why):
    got = ask(grid)
    assert got == expected, f"Grid {grid}: expected {expected}, got {got} ({why})."


def test_random_small():
    rng = random.Random(34)
    for _ in range(30):
        r, c = rng.randint(1, 6), rng.randint(1, 6)
        grid = [[rng.choice((0, 1, 2, 3, 4, 5, 6, 7)) for _ in range(c)] for _ in range(r)]
        got = ask(grid)
        expected = expected_for(grid)
        assert got == expected, (
            f"Grid {grid}: expected {expected}, got {got}. Only ORIGINAL zeros clear their row and column.")


def test_large():
    rng = random.Random(3434)
    r, c = 500, 400
    grid = [[rng.randint(1, 10**9) for _ in range(c)] for _ in range(r)]
    for _ in range(300):
        grid[rng.randrange(r)][rng.randrange(c)] = 0
    expected = expected_for(grid)
    got = ask(grid, timeout=10)
    assert len(got) == r, f"Expected {r} output rows, got {len(got)}."
    bad = next((i for i in range(r) if got[i] != expected[i]), None)
    assert bad is None, (
        f"Large 500 x 400 grid with 300 zeros: row {bad + 1} is wrong. Mark rows and columns in one pass, write "
        "in a second pass.")
