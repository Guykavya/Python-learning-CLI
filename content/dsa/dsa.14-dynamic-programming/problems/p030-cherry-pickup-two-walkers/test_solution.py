import pathlib
import random
import subprocess
import sys
from functools import lru_cache

from solution import cherry_pickup

HERE = pathlib.Path(__file__).parent


def all_paths(grid):
    """Every right/down path from the top-left to the bottom-right that avoids -1 (small grids only)."""
    n = len(grid)
    out = []

    def walk(r, c, cells):
        if r >= n or c >= n or grid[r][c] == -1:
            return
        cells = cells + [(r, c)]
        if (r, c) == (n - 1, n - 1):
            out.append(cells)
            return
        walk(r + 1, c, cells)
        walk(r, c + 1, cells)

    walk(0, 0, [])
    return out


def brute(grid):
    """Try every pair of trips; a cell picked twice counts once."""
    paths = all_paths(grid)
    best = 0
    for a in paths:
        for b in paths:
            best = max(best, sum(grid[r][c] for r, c in set(a) | set(b)))
    return best


def oracle(grid):
    """Top-down memo over (r1, c1, r2): a different formulation, for the big grid."""
    n = len(grid)
    NEG = float("-inf")

    @lru_cache(maxsize=None)
    def best(r1, c1, r2):
        c2 = r1 + c1 - r2
        if r1 >= n or c1 >= n or r2 >= n or c2 >= n or grid[r1][c1] == -1 or grid[r2][c2] == -1:
            return NEG
        here = grid[r1][c1] + (grid[r2][c2] if (r1, c1) != (r2, c2) else 0)
        if (r1, c1) == (n - 1, n - 1):
            return here
        nxt = max(best(r1 + 1, c1, r2 + 1), best(r1 + 1, c1, r2), best(r1, c1 + 1, r2 + 1), best(r1, c1 + 1, r2))
        return here + nxt

    return max(0, best(0, 0, 0))


def run_big(code, timeout=10):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=timeout, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_examples():
    assert cherry_pickup([[0, 1, -1], [1, 0, -1], [1, 1, 1]]) == 5, "Expected 5: all five cherries."
    assert cherry_pickup([[1, -1, 1], [1, 1, 1], [1, -1, 1]]) == 5, (
        "Expected 5. A walker can never step on -1; both trips go through the middle row.")


def test_two_trips_must_be_planned_together():
    assert cherry_pickup([[1, 1, 0], [1, 1, 1], [1, 0, 1]]) == 7, (
        "Expected 7: one trip along the top and right, the other along the left and bottom, both through the "
        "middle. Taking the best single trip first and then the best second trip can stop at 6.")


def test_no_route():
    assert cherry_pickup([[1, 1, -1], [1, -1, 1], [-1, 1, 1]]) == 0, (
        "Thorns block every route to the bottom-right: return 0, not a negative number or the cherries "
        "near the start. Unreachable states must stay at -infinity.")
    assert cherry_pickup([[-1]]) == 0, "The only cell is a thorn: 0."
    assert cherry_pickup([[1, 1], [1, -1]]) == 0, "The end cell is a thorn: there is no trip at all, so 0."


def test_single_cell_counted_once():
    assert cherry_pickup([[1]]) == 1, (
        "One cell with a cherry: 1. Both walkers stand on it; count its cherry once (r1 == r2 means same cell).")
    assert cherry_pickup([[1, 1], [1, 1]]) == 4, (
        "Expected 4: the two walkers split at the start and meet at the end; the start and end cherries "
        "are counted once each.")


def test_random_against_brute_force():
    rng = random.Random(30)
    for _ in range(250):
        n = rng.randint(1, 5)
        grid = [[rng.choice([-1, 0, 1, 1]) for _ in range(n)] for _ in range(n)]
        if rng.random() < 0.8:
            grid[0][0] = rng.choice([0, 1])
            grid[n - 1][n - 1] = rng.choice([0, 1])
        want = brute(grid)
        got = cherry_pickup([row[:] for row in grid])
        assert got == want, (
            f"grid={grid}: expected {want}, got {got}. State (t, r1, r2): after t steps the walkers are at "
            "(r1, t-r1) and (r2, t-r2); each came from above or the left (4 combinations); add both cells, "
            "but only once if r1 == r2; skip thorns; return max(0, final).")


def test_big_grid():
    make = ("import random\n"
            "rng = random.Random(2030)\n"
            "grid = [[rng.choice([-1, 0, 1, 1, 1, 0, 1]) for _ in range(50)] for _ in range(50)]\n"
            "grid[0][0] = grid[49][49] = 1\n")
    code = make + "from solution import cherry_pickup\nprint(cherry_pickup(grid))\n"
    names = {}
    exec(make, names)                 # the same grid, built here for the checker
    r = run_big(code)
    assert r is not None, (
        "Time limit (10 s) on a 50 by 50 grid. exponential: add a memo. Trying every pair of trips is hopeless; "
        "the state (t, r1, r2) has only about 99 * 50 * 50 values.")
    assert r.returncode == 0, "Your code crashed on a 50 by 50 grid:\n" + r.stderr[-800:]
    assert r.stdout.split() == [str(oracle(names["grid"]))], "Wrong number of cherries on the 50 by 50 grid."
