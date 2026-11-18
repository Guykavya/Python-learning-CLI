import pathlib
import random
import subprocess
import sys

from solution import paths_with_obstacles

HERE = pathlib.Path(__file__).parent


def brute(grid):
    """Walk every right/down path one by one (exponential; small grids only)."""
    rows, cols = len(grid), len(grid[0])

    def walk(r, c):
        if r >= rows or c >= cols or grid[r][c] == 1:
            return 0
        if (r, c) == (rows - 1, cols - 1):
            return 1
        return walk(r + 1, c) + walk(r, c + 1)

    return walk(0, 0)


def oracle(grid):
    """Pull-style DP with a dictionary, written differently from the chapter (for big grids)."""
    rows, cols = len(grid), len(grid[0])
    ways = {}
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                ways[(r, c)] = 0
            elif r == c == 0:
                ways[(r, c)] = 1
            else:
                ways[(r, c)] = ways.get((r - 1, c), 0) + ways.get((r, c - 1), 0)
    return ways[(rows - 1, cols - 1)]


def run_big(code, timeout=10):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=timeout, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_examples():
    assert paths_with_obstacles([[0, 0, 0], [0, 1, 0], [0, 0, 0]]) == 2, "Expected 2: around the centre, top or left."
    assert paths_with_obstacles([[0, 1], [0, 0]]) == 1, "Expected 1: down, then right."


def test_start_or_end_blocked():
    assert paths_with_obstacles([[1, 0]]) == 0, (
        "The start is blocked: 0 paths. Check the obstacle BEFORE you set the start to 1.")
    assert paths_with_obstacles([[0, 0], [0, 1]]) == 0, "The end is blocked: 0 paths."
    assert paths_with_obstacles([[1]]) == 0, "A single blocked cell: 0 paths."
    assert paths_with_obstacles([[0]]) == 1, "A single open cell: 1 path (stand still)."


def test_obstacle_in_first_row_blocks_the_rest_of_it():
    assert paths_with_obstacles([[0, 1, 0, 0]]) == 0, (
        "In one row, an obstacle cuts off every cell to its right. If you filled the first row with 1s "
        "regardless, you count paths that jump over the obstacle.")
    assert paths_with_obstacles([[0], [1], [0]]) == 0, "One column with an obstacle in the middle: 0 paths."
    assert paths_with_obstacles([[0, 1, 0], [0, 0, 0]]) == 1, (
        "Expected 1 (down, right, right). The top-right cell can only be reached through the obstacle, so it is 0.")


def test_random_against_brute_force():
    rng = random.Random(26)
    for _ in range(400):
        rows, cols = rng.randint(1, 6), rng.randint(1, 6)
        grid = [[1 if rng.random() < 0.25 else 0 for _ in range(cols)] for _ in range(rows)]
        want = brute(grid)
        got = paths_with_obstacles([row[:] for row in grid])
        assert got == want, (
            f"grid={grid}: expected {want} paths, got {got}. A blocked cell is 0; any other cell is "
            "(cell above) + (cell on the left); the start is 1 only if it is open.")


def test_big_grid_needs_memo_or_table():
    make = ("import random\n"
            "rng = random.Random(2026)\n"
            "grid = [[1 if rng.random() < 0.05 else 0 for _ in range(200)] for _ in range(200)]\n"
            "grid[0][0] = grid[199][199] = 0\n")
    code = make + "from solution import paths_with_obstacles\nprint(paths_with_obstacles(grid))\n"
    names = {}
    exec(make, names)                 # the same grid, built here for the checker
    grid = names["grid"]
    r = run_big(code)
    assert r is not None, (
        "Time limit (10 s) on a 200 by 200 grid. exponential: add a memo. Walking every path one by one is "
        "hopeless; each cell is one state, so a table of 40,000 cells is enough.")
    assert r.returncode == 0, "Your code crashed on a 200 by 200 grid:\n" + r.stderr[-800:]
    assert r.stdout.split() == [str(oracle(grid))], "Wrong count on the 200 by 200 grid."
