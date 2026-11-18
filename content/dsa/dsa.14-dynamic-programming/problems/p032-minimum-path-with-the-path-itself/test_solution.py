import pathlib
import random
import subprocess
import sys

from solution import min_path

HERE = pathlib.Path(__file__).parent
INF = float("inf")


def brute_min(grid):
    """The cheapest cost over every right/down path (small grids only)."""
    rows, cols = len(grid), len(grid[0])

    def walk(r, c):
        if r >= rows or c >= cols:
            return INF
        if (r, c) == (rows - 1, cols - 1):
            return grid[r][c]
        return grid[r][c] + min(walk(r + 1, c), walk(r, c + 1))

    return walk(0, 0)


def check(grid, result, want):
    """Validate (total, route): legal route, right cost, optimal. Returns an error message or None."""
    rows, cols = len(grid), len(grid[0])
    if not (isinstance(result, tuple) and len(result) == 2):
        return f"return a tuple (total, route); got {result!r}"
    total, route = result
    if total != want:
        return f"total should be {want}, got {total}"
    route = [tuple(cell) for cell in route]
    if not route or route[0] != (0, 0):
        return f"the route must start at (0, 0); it starts {route[:1]}. Did you forget to reverse it?"
    if route[-1] != (rows - 1, cols - 1):
        return f"the route must end at {(rows - 1, cols - 1)}; it ends {route[-1:]}. Did you forget to reverse it?"
    if len(route) != rows + cols - 1:
        return f"a right/down route has rows + cols - 1 = {rows + cols - 1} cells; yours has {len(route)}"
    for (r1, c1), (r2, c2) in zip(route, route[1:]):
        if (r2 - r1, c2 - c1) not in ((0, 1), (1, 0)):
            return f"illegal step {(r1, c1)} -> {(r2, c2)}: each step goes one cell right or down"
    cost = sum(grid[r][c] for r, c in route)
    if cost != want:
        return f"the cells of your route add up to {cost}, not the minimum {want}"
    return None


def run_big(code, timeout=10):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=timeout, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_example():
    g = [[1, 3, 1], [1, 5, 1], [4, 2, 1]]
    err = check(g, min_path(g), 7)
    assert err is None, "Chapter example: " + err


def test_single_cell_row_and_column():
    for g, want in [([[5]], 5), ([[1, 2, 3]], 6), ([[1], [2], [3]], 6)]:
        err = check(g, min_path(g), want)
        assert err is None, f"grid={g}: " + err + ". On the first row step back left; on the first column, up."


def test_ties_any_route_is_fine():
    g = [[1, 1], [1, 1]]
    err = check(g, min_path(g), 3)
    assert err is None, "All ones: both routes cost 3, either is accepted. " + err


def test_walk_back_follows_the_table_not_the_grid():
    g = [[0, 0, 9],
         [9, 0, 9],
         [9, 0, 0]]
    err = check(g, min_path(g), 0)
    assert err is None, (
        "Expected cost 0 along the zeros. Walking back, compare f values (best cost so far), not the grid "
        "values of the neighbours. " + err)
    g = [[0, 0, 0],
         [9, 9, 3],
         [9, 1, 0]]
    err = check(g, min_path(g), 3)
    assert err is None, (
        "Expected cost 3 along the top row and down the right column. At the end cell the left neighbour "
        "costs only 1, but every path into it costs at least 10 (f = 10), while f above is 3. "
        "Compare f values on the way back. " + err)


def test_random_validated():
    rng = random.Random(32)
    for _ in range(300):
        rows, cols = rng.randint(1, 6), rng.randint(1, 6)
        g = [[rng.randint(0, 5) for _ in range(cols)] for _ in range(rows)]
        want = brute_min(g)
        err = check(g, min_path([row[:] for row in g]), want)
        assert err is None, f"grid={g}: " + err


def test_big_grid():
    make = ("import random\n"
            "rng = random.Random(2032)\n"
            "g = [[rng.randint(0, 100) for _ in range(200)] for _ in range(200)]\n")
    code = make + ("from solution import min_path\n"
                   "total, route = min_path(g)\n"
                   "print(total)\n"
                   "print(';'.join(f'{r},{c}' for r, c in route))\n")
    names = {}
    exec(make, names)                 # the same grid, built here for the checker
    g = names["g"]
    r = run_big(code)
    assert r is not None, (
        "Time limit (10 s) on a 200 by 200 grid. exponential: add a memo. Fill the table f once (40,000 cells), "
        "then walk back: 399 steps.")
    assert r.returncode == 0, "Your code crashed on a 200 by 200 grid:\n" + r.stderr[-800:]
    lines = r.stdout.split()
    route = [tuple(int(x) for x in cell.split(",")) for cell in lines[1].split(";")]
    best = [[0] * 200 for _ in range(200)]
    for i in range(200):
        for j in range(200):
            prev = [best[i - 1][j]] * (i > 0) + [best[i][j - 1]] * (j > 0)
            best[i][j] = g[i][j] + (min(prev) if prev else 0)
    err = check(g, (int(lines[0]), route), best[199][199])
    assert err is None, "Big grid: " + err
