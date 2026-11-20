import pathlib
import random
import subprocess
import sys

from solution import min_triangle_path

HERE = pathlib.Path(__file__).parent


def brute(triangle, i=0, j=0):
    """Try every path (2**(n-1) of them; small triangles only)."""
    if i == len(triangle) - 1:
        return triangle[i][j]
    return triangle[i][j] + min(brute(triangle, i + 1, j), brute(triangle, i + 1, j + 1))


def oracle(triangle):
    """Top-down table with explicit edges (a different direction from the reference idea)."""
    f = [triangle[0][:]]
    for i in range(1, len(triangle)):
        row = []
        for j in range(i + 1):
            parents = [f[i - 1][k] for k in (j - 1, j) if 0 <= k < i]
            row.append(triangle[i][j] + min(parents))
        f.append(row)
    return min(f[-1])


def run_big(code, timeout=10):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=timeout, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_example():
    assert min_triangle_path([[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]]) == 11, (
        "Expected 11 (2 + 3 + 5 + 1). Greedy (smallest child each time) happens to work here; the random tests "
        "will show where it does not.")


def test_small():
    assert min_triangle_path([[-10]]) == -10, "One row: the answer is that single value."
    assert min_triangle_path([[1], [2, 3]]) == 3, "Expected 3 (1 + 2)."


def test_greedy_fails():
    assert min_triangle_path([[1], [2, 3], [9, 9, 1], [9, 9, 9, 1]]) == 6, (
        "Expected 6 (1 + 3 + 1 + 1). Stepping to the smaller child first (2) leads to 9s. "
        "The DP must compare whole paths: g[i][j] = value + min(g[i+1][j], g[i+1][j+1]).")


def test_only_adjacent_moves():
    assert min_triangle_path([[0], [5, 9], [9, 9, -50]]) == -41, (
        "Expected -41 (0 + 9 - 50). From position 0 you may only reach positions 0 and 1 of the next row; "
        "the -50 is reachable only through the 9.")
    assert min_triangle_path([[0], [1, 9], [9, 9, -50]]) == -41, (
        "Expected -41 again: the -50 at position 2 is reachable only through position 1 of row 1. "
        "If you took the min over the whole next row, you would get a path that jumps.")


def test_negative_values():
    assert min_triangle_path([[-1], [2, 3], [1, -1, -3]]) == -1, (
        "Expected -1 (-1 + 3 - 3: the bigger first step leads to the -3). Values can be negative: never start a minimum at 0.")


def test_random_against_brute_force():
    rng = random.Random(28)
    for _ in range(300):
        n = rng.randint(1, 9)
        tri = [[rng.randint(-9, 9) for _ in range(i + 1)] for i in range(n)]
        want = brute(tri)
        got = min_triangle_path([row[:] for row in tri])
        assert got == want, (
            f"triangle={tri}: expected {want}, got {got}. From (i, j) you may only go to (i+1, j) or (i+1, j+1).")


def test_big_triangle_needs_memo_or_table():
    make = ("import random\n"
            "rng = random.Random(2028)\n"
            "tri = [[rng.randint(-1000, 1000) for _ in range(i + 1)] for i in range(400)]\n")
    code = make + "from solution import min_triangle_path\nprint(min_triangle_path(tri))\n"
    names = {}
    exec(make, names)                 # the same triangle, built here for the checker
    r = run_big(code)
    assert r is not None, (
        "Time limit (10 s) on 400 rows. exponential: add a memo. There are 2**399 paths but only "
        "about 80,000 cells; solve each cell once, from the bottom row up.")
    assert r.returncode == 0, "Your code crashed on 400 rows:\n" + r.stderr[-800:]
    assert r.stdout.split() == [str(oracle(names["tri"]))], "Wrong minimum on the 400-row triangle."
