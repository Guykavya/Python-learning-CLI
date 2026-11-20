import pathlib
import random
import subprocess
import sys

from solution import min_path_sum

HERE = pathlib.Path(__file__).parent
INF = float("inf")


def brute(grid):
    """Try every right/down path (exponential; small grids only)."""
    rows, cols = len(grid), len(grid[0])

    def walk(r, c):
        if r >= rows or c >= cols:
            return INF
        if (r, c) == (rows - 1, cols - 1):
            return grid[r][c]
        return grid[r][c] + min(walk(r + 1, c), walk(r, c + 1))

    return walk(0, 0)


def oracle(grid):
    """The infinity-border version of section 8, for big grids."""
    rows, cols = len(grid), len(grid[0])
    f = [[INF] * (cols + 1) for _ in range(rows + 1)]
    f[0][1] = 0
    for r in range(rows):
        for c in range(cols):
            f[r + 1][c + 1] = grid[r][c] + min(f[r][c + 1], f[r + 1][c])
    return f[rows][cols]


def run_big(code, timeout=10):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=timeout, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_example():
    assert min_path_sum([[1, 3, 1], [1, 5, 1], [4, 2, 1]]) == 7, (
        "Expected 7 (1 -> 3 -> 1 -> 1 -> 1). f[r][c] = grid[r][c] + min(above, left).")


def test_one_row_one_column_one_cell():
    assert min_path_sum([[1, 2, 3]]) == 6, (
        "One row: the only path takes every cell, 6. The first row has no cell above: f = left + grid.")
    assert min_path_sum([[1], [2], [3]]) == 6, "One column: 6. The first column has no cell on the left."
    assert min_path_sum([[5]]) == 5, "One cell: the path is the cell itself, cost 5 (not 0)."


def test_both_ends_are_counted():
    assert min_path_sum([[9, 0], [0, 9]]) == 18, (
        "Expected 18: the start (9) and the end (9) are always on the path. Did you leave out one of them?")


def test_zeros():
    assert min_path_sum([[0, 0], [0, 0]]) == 0, "All zeros cost 0. Is 0 used as 'no value yet' somewhere?"


def test_random_against_brute_force():
    rng = random.Random(27)
    for _ in range(300):
        rows, cols = rng.randint(1, 6), rng.randint(1, 6)
        grid = [[rng.randint(0, 9) for _ in range(cols)] for _ in range(rows)]
        want = brute(grid)
        got = min_path_sum([row[:] for row in grid])
        assert got == want, (
            f"grid={grid}: expected {want}, got {got}. Check the first row (left only), the first column "
            "(above only) and the inner cells (min of above and left).")


def test_big_grid_needs_memo_or_table():
    make = ("import random\n"
            "rng = random.Random(2027)\n"
            "grid = [[rng.randint(0, 100) for _ in range(200)] for _ in range(200)]\n")
    code = make + "from solution import min_path_sum\nprint(min_path_sum(grid))\n"
    names = {}
    exec(make, names)                 # the same grid, built here for the checker
    grid = names["grid"]
    r = run_big(code)
    assert r is not None, (
        "Time limit (10 s) on a 200 by 200 grid. exponential: add a memo. Each cell is one state; "
        "fill a 200 by 200 table once.")
    assert r.returncode == 0, "Your code crashed on a 200 by 200 grid:\n" + r.stderr[-800:]
    assert r.stdout.split() == [str(oracle(grid))], "Wrong minimum on the 200 by 200 grid."
