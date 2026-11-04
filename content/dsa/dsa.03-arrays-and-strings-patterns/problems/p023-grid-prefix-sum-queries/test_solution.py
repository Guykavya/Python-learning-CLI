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


def ask(grid, queries, timeout=10):
    lines = [f"{len(grid)} {len(grid[0])}"]
    lines += [" ".join(map(str, row)) for row in grid]
    lines.append(str(len(queries)))
    lines += [" ".join(map(str, qu)) for qu in queries]
    return run("\n".join(lines) + "\n", timeout=timeout)


def brute(grid, qu):
    r1, c1, r2, c2 = qu
    return sum(grid[i][j] for i in range(r1 - 1, r2) for j in range(c1 - 1, c2))


EXAMPLE = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]


def test_example():
    got = ask(EXAMPLE, [(1, 1, 3, 4), (2, 2, 3, 3), (1, 4, 2, 4)])
    assert got == ["78", "34", "12"], (
        f"The example: expected 78, 34, 12; got {got}. For 2 2 3 3 the formula is "
        "P[3][3] - P[1][3] - P[3][1] + P[1][1] = 54 - 6 - 15 + 1.")


@pytest.mark.parametrize("query, expected, why", [
    ((1, 1, 1, 1), 1, "one cell in the top-left corner: r1 - 1 = 0 must hit a row of zeros, not P[-1]"),
    ((3, 4, 3, 4), 12, "one cell in the bottom-right corner"),
    ((2, 1, 2, 4), 26, "one whole row: 5 + 6 + 7 + 8"),
    ((1, 2, 3, 2), 18, "one whole column: 2 + 6 + 10"),
    ((2, 2, 3, 4), 54, "a block that does not touch row 1 or column 1: the corner must be added back"),
    ((1, 3, 3, 4), 45, "a block touching row 1: 3+4+7+8+11+12"),
])
def test_single_queries(query, expected, why):
    got = ask(EXAMPLE, [query])
    assert got == [str(expected)], f"Query {query} on the example grid: expected {expected}, got {got} ({why})."


def test_negative_values_and_one_cell_grid():
    got = ask([[-5]], [(1, 1, 1, 1)])
    assert got == ["-5"], f"A 1 x 1 grid holding -5: expected -5, got {got}."
    grid = [[-1, 2], [3, -4]]
    got = ask(grid, [(1, 1, 2, 2), (2, 1, 2, 2), (1, 2, 2, 2)])
    assert got == ["0", "-1", "-2"], f"Grid -1 2 / 3 -4: expected 0, -1, -2; got {got}. Negative values need no special case."


def test_random_small_against_brute_force():
    rng = random.Random(23)
    for _ in range(25):
        r, c = rng.randint(1, 6), rng.randint(1, 6)
        grid = [[rng.randint(-9, 9) for _ in range(c)] for _ in range(r)]
        queries = []
        for _ in range(15):
            r1, r2 = sorted((rng.randint(1, r), rng.randint(1, r)))
            c1, c2 = sorted((rng.randint(1, c), rng.randint(1, c)))
            queries.append((r1, c1, r2, c2))
        got = ask(grid, queries)
        expected = [str(brute(grid, qu)) for qu in queries]
        assert got == expected, (
            f"Grid {grid}, queries {queries}: expected {expected}, got {got}. Check the four terms: "
            "P[r2][c2] - P[r1-1][c2] - P[r2][c1-1] + P[r1-1][c1-1].")


def test_large():
    rng = random.Random(2323)
    r = c = 500
    # Cell (i, j) (1-based) holds i * 1000 + j, so every rectangle sum has a closed formula.
    grid = [[i * 1000 + j for j in range(1, c + 1)] for i in range(1, r + 1)]
    queries = []
    expected = []
    for _ in range(200000):
        r1, r2 = sorted((rng.randint(1, r), rng.randint(1, r)))
        c1, c2 = sorted((rng.randint(1, c), rng.randint(1, c)))
        queries.append((r1, c1, r2, c2))
        h, w = r2 - r1 + 1, c2 - c1 + 1
        expected.append(str(1000 * w * (r1 + r2) * h // 2 + h * (c1 + c2) * w // 2))
    got = ask(grid, queries, timeout=15)
    assert len(got) == len(expected), f"Expected {len(expected)} answer lines, got {len(got)}."
    bad = next((k for k in range(len(expected)) if got[k] != expected[k]), None)
    assert bad is None, (
        f"Large test, query {queries[bad]}: expected {expected[bad]}, got {got[bad]}. "
        "If it is correct on small grids, look at the edges (r1 = 1 or c1 = 1).")
