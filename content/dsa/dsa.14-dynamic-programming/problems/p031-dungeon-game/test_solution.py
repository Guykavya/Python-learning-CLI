import pathlib
import random
import subprocess
import sys

from solution import min_initial_health

HERE = pathlib.Path(__file__).parent


def brute(dungeon):
    """Every right/down path: the start health must keep every prefix sum above 0 (small grids only)."""
    rows, cols = len(dungeon), len(dungeon[0])
    best = None

    def walk(r, c, total, lowest):
        nonlocal best
        total += dungeon[r][c]
        lowest = min(lowest, total)
        if (r, c) == (rows - 1, cols - 1):
            need = max(1, 1 - lowest)
            if best is None or need < best:
                best = need
            return
        if r + 1 < rows:
            walk(r + 1, c, total, lowest)
        if c + 1 < cols:
            walk(r, c + 1, total, lowest)

    walk(0, 0, 0, 0)
    return best


def survives(dungeon, health):
    """Forward DP for a FIXED start health: the most health left on entering each room (None = dead)."""
    rows, cols = len(dungeon), len(dungeon[0])
    best = [[None] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if r == 0 and c == 0:
                before = health
            else:
                options = [v for v in (best[r - 1][c] if r else None, best[r][c - 1] if c else None)
                           if v is not None]
                before = max(options) if options else None
            if before is not None and before + dungeon[r][c] > 0:
                best[r][c] = before + dungeon[r][c]
    return best[rows - 1][cols - 1] is not None


def oracle(dungeon):
    """Binary search on the start health with the forward check: a different method, for big grids."""
    lo, hi = 1, 1 + 1000 * (len(dungeon) + len(dungeon[0]))
    while lo < hi:
        mid = (lo + hi) // 2
        if survives(dungeon, mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


def run_big(code, timeout=10):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=timeout, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_classic_example():
    assert min_initial_health([[-2, -3, 3], [-5, -10, 1], [10, 30, -5]]) == 7, (
        "Expected 7 (right, right, down, down). Fill need[][] from the bottom-right corner backwards.")


def test_single_rooms():
    assert min_initial_health([[0]]) == 1, "An empty room: he only needs to be alive, health 1."
    assert min_initial_health([[100]]) == 1, (
        "A potion cannot lower the need below 1: he must be alive when he enters. Use max(1, ...).")
    assert min_initial_health([[-5]]) == 6, (
        "One demon of 5: with 6 he ends at 1. With 5 he ends at 0 and dies. Health must stay ABOVE 0.")


def test_potion_later_cannot_save_an_earlier_dip():
    assert min_initial_health([[-10, 50]]) == 11, (
        "Expected 11: the -10 comes first, so he needs 11 before the potion. A potion later on the path does not "
        "help an earlier room. Going forwards with sums gives 1, which is wrong.")


def test_most_health_at_the_end_is_not_the_answer():
    d = [[0, -10, 20],
         [-2, -2, -2],
         [0, 0, 0]]
    assert min_initial_health(d) == 3, (
        "Expected 3 (down, down, right, right: lowest point -2). The path with the biggest final health "
        "(right, right, down, down, sum 8) dips to -10 first and needs 11. Work backwards from the exit.")


def test_last_room_counts():
    assert min_initial_health([[5, -8]]) == 4, (
        "Expected 4: 4 + 5 - 8 = 1. The last room is entered too; its demon counts.")


def test_random_against_brute_force():
    rng = random.Random(31)
    for _ in range(300):
        rows, cols = rng.randint(1, 5), rng.randint(1, 5)
        d = [[rng.randint(-10, 6) for _ in range(cols)] for _ in range(rows)]
        want = brute(d)
        got = min_initial_health([row[:] for row in d])
        assert got == want, (
            f"dungeon={d}: expected {want}, got {got}. need[r][c] = max(1, min(need below, need right) - "
            "dungeon[r][c]); in the last room need = max(1, 1 - dungeon[r][c]).")


def test_big_grid():
    make = ("import random\n"
            "rng = random.Random(2031)\n"
            "d = [[rng.randint(-1000, 900) for _ in range(200)] for _ in range(200)]\n")
    code = make + "from solution import min_initial_health\nprint(min_initial_health(d))\n"
    names = {}
    exec(make, names)                 # the same dungeon, built here for the checker
    r = run_big(code)
    assert r is not None, (
        "Time limit (10 s) on a 200 by 200 dungeon. exponential: add a memo. Each room has ONE value need[r][c]; "
        "compute it once, from the bottom-right corner backwards.")
    assert r.returncode == 0, "Your code crashed on a 200 by 200 dungeon:\n" + r.stderr[-800:]
    assert r.stdout.split() == [str(oracle(names["d"]))], "Wrong starting health on the 200 by 200 dungeon."
