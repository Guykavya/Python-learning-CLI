import pathlib
import random
import subprocess
import sys
from math import comb

from solution import unique_paths

HERE = pathlib.Path(__file__).parent


def run_big(code, timeout=10):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=timeout, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_examples():
    assert unique_paths(3, 7) == 28, "Expected 28 for 3 rows and 7 columns."
    assert unique_paths(3, 2) == 3, "Expected 3: the single 'right' can come first, second or third."
    assert unique_paths(7, 3) == 28, "The grid turned on its side has the same count: 28."


def test_one_cell_and_one_line():
    assert unique_paths(1, 1) == 1, (
        "A 1 by 1 grid has exactly one path (do nothing), not 0. If you got 0, your table never sets the start to 1.")
    assert unique_paths(1, 5) == 1, "One row: the only path goes right all the way. The first row is all 1s."
    assert unique_paths(5, 1) == 1, "One column: the only path goes down all the way. The first column is all 1s."


def test_against_binomial():
    rng = random.Random(25)
    for _ in range(200):
        rows, cols = rng.randint(1, 15), rng.randint(1, 15)
        want = comb(rows + cols - 2, rows - 1)
        got = unique_paths(rows, cols)
        assert got == want, (
            f"unique_paths({rows}, {cols}): expected {want}, got {got}. f[r][c] = f[r-1][c] + f[r][c-1], "
            "with 1s on the first row and the first column.")


def test_medium_grid_needs_memo():
    code = "from solution import unique_paths\nprint(unique_paths(150, 150))\n"
    r = run_big(code)
    assert r is not None, (
        "Time limit (10 s) on a 150 by 150 grid. exponential: add a memo. paths(r, c) = paths(r-1, c) + "
        "paths(r, c-1) without a cache visits every path one by one; there are about 10**88 of them.")
    assert r.returncode == 0, "Your code crashed on a 150 by 150 grid:\n" + r.stderr[-800:]
    assert r.stdout.split() == [str(comb(298, 149))], "Wrong count for a 150 by 150 grid."


def test_large_grid_uses_a_table():
    code = ("from solution import unique_paths\n"
            "print(unique_paths(1000, 1000) == __import__('math').comb(1998, 999), unique_paths(1, 1000))\n")
    r = run_big(code)
    assert r is not None, (
        "Time limit (10 s) on a 1000 by 1000 grid. The table has 10**6 cells: fill each one once, "
        "row by row (one rolling row is enough).")
    assert r.returncode == 0, (
        "Your code crashed on a 1000 by 1000 grid. A top-down recursion is about 2,000 calls deep here "
        "(RecursionError): fill a table bottom-up instead.\n" + r.stderr[-600:])
    assert r.stdout.split() == ["True", "1"], f"Wrong count for the 1000 by 1000 or the 1 by 1000 grid: {r.stdout}"
