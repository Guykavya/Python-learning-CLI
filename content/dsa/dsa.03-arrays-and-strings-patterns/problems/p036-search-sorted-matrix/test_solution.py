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


def ask(grid, targets, timeout=10):
    lines = [f"{len(grid)} {len(grid[0])}"] + [" ".join(map(str, row)) for row in grid]
    lines += [str(len(targets)), " ".join(map(str, targets))]
    return run("\n".join(lines) + "\n", timeout=timeout)


def sorted_grid(rng, r, c, step):
    """Each cell is at least the cell above and the cell to its left."""
    g = [[0] * c for _ in range(r)]
    for i in range(r):
        for j in range(c):
            base = max(g[i - 1][j] if i else -50, g[i][j - 1] if j else -50)
            g[i][j] = base + rng.randint(0, step)
    return g


EXAMPLE = [[1, 4, 7, 11], [2, 5, 8, 12], [3, 6, 9, 16]]


def test_example():
    got = ask(EXAMPLE, [5, 10, 16])
    assert got == ["yes", "no", "yes"], f"The example (5, 10, 16): expected yes, no, yes; got {got}."


@pytest.mark.parametrize("x, expected, why", [
    (1, "yes", "the top-left corner: the walk must go all the way left, then find it"),
    (16, "yes", "the bottom-right corner: the walk goes all the way down"),
    (11, "yes", "the starting corner itself"),
    (3, "yes", "the bottom-left corner: column 0 must be checked (j >= 0, not j > 0)"),
    (0, "no", "smaller than everything: the walk leaves on the left"),
    (17, "no", "larger than everything: the walk leaves at the bottom"),
    (5, "yes", "row 2: binary searching the first column would pick row 3 and miss it"),
    (13, "no", "between 12 and 16"),
])
def test_single_queries(x, expected, why):
    got = ask(EXAMPLE, [x])
    assert got == [expected], f"Query {x} on the example grid: expected {expected}, got {got} ({why})."


def test_one_cell_and_one_row():
    assert ask([[7]], [7, 6, 8]) == ["yes", "no", "no"], "A 1 x 1 grid holding 7: queries 7, 6, 8 give yes, no, no."
    got = ask([[1, 3, 5, 7]], [5, 4, 1, 7])
    assert got == ["yes", "no", "yes", "yes"], f"One row 1 3 5 7, queries 5 4 1 7: expected yes, no, yes, yes; got {got}."
    got = ask([[1], [3], [5]], [3, 2, 5])
    assert got == ["yes", "no", "yes"], f"One column 1 3 5, queries 3 2 5: expected yes, no, yes; got {got}."


def test_duplicates():
    grid = [[1, 2, 2], [2, 2, 3], [2, 3, 3]]
    got = ask(grid, [2, 3, 1, 4])
    assert got == ["yes", "yes", "yes", "no"], f"A grid with many equal values: expected yes, yes, yes, no; got {got}."


def test_random_small():
    rng = random.Random(36)
    for _ in range(30):
        r, c = rng.randint(1, 6), rng.randint(1, 6)
        grid = sorted_grid(rng, r, c, 3)
        values = {v for row in grid for v in row}
        targets = [rng.randint(-52, -50 + 3 * (r + c)) for _ in range(12)]
        got = ask(grid, targets)
        expected = ["yes" if x in values else "no" for x in targets]
        assert got == expected, (
            f"Grid {grid}, queries {targets}: expected {expected}, got {got}. From the top-right: too big -> "
            "move left, too small -> move down, stop when you leave the grid.")


def test_large():
    rng = random.Random(3636)
    r, c = 600, 600
    grid = sorted_grid(rng, r, c, 5)
    values = {v for row in grid for v in row}
    hi = grid[-1][-1]
    targets = [rng.randint(-60, hi + 10) for _ in range(2000)]
    expected = ["yes" if x in values else "no" for x in targets]
    got = ask(grid, targets, timeout=15)
    assert got == expected, (
        "A 600 x 600 sorted grid with 2000 queries: some answers are wrong (or a line is missing). "
        "Each staircase walk must stop when i reaches r or j goes below 0.")
