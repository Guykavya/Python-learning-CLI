import pathlib
import random
import subprocess
import sys

from solution import maximal_square

HERE = pathlib.Path(__file__).parent


def brute(matrix):
    """Check every square directly (slow; small grids only)."""
    rows, cols = len(matrix), len(matrix[0])
    best = 0
    for top in range(rows):
        for left in range(cols):
            k = 1
            while top + k <= rows and left + k <= cols:
                if all(matrix[r][c] == 1 for r in range(top, top + k) for c in range(left, left + k)):
                    best = max(best, k)
                k += 1
    return best * best


def oracle(matrix):
    """One rolling row plus the saved diagonal: a different way to write the same DP."""
    cols = len(matrix[0])
    prev = [0] * (cols + 1)
    best = 0
    for row in matrix:
        cur = [0] * (cols + 1)
        for c in range(1, cols + 1):
            if row[c - 1] == 1:
                cur[c] = 1 + min(prev[c], cur[c - 1], prev[c - 1])
                best = max(best, cur[c])
        prev = cur
    return best * best


def run_big(code, timeout=10):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=timeout, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_chapter_example():
    m = [[1, 0, 1, 0, 0], [1, 0, 1, 1, 1], [1, 1, 1, 1, 1], [1, 0, 0, 1, 0]]
    got = maximal_square(m)
    assert got != 2, "You returned the side (2). The function must return the AREA: side * side = 4."
    assert got == 4, f"Expected area 4 (a 2 by 2 square at rows 1-2, columns 3-4), got {got}."


def test_small_cases():
    assert maximal_square([[0, 0], [0, 0]]) == 0, "No 1s at all: area 0."
    assert maximal_square([[1]]) == 1, "A single 1: area 1."
    assert maximal_square([[1, 1], [1, 1]]) == 4, "All ones 2 by 2: area 4."
    assert maximal_square([[1, 1, 1], [1, 1, 1], [1, 1, 1]]) == 9, "All ones 3 by 3: area 9."


def test_rectangles_are_not_squares():
    assert maximal_square([[1, 1, 1, 1]]) == 1, (
        "A 1 by 4 strip of ones holds only 1 by 1 squares. Did you count the length of a run of ones?")
    assert maximal_square([[1, 1, 1], [1, 1, 1]]) == 4, "A 2 by 3 block of ones: the biggest square is 2 by 2."


def test_min_of_three_not_two():
    m = [[0, 1, 1],
         [1, 1, 1],
         [1, 1, 1]]
    assert maximal_square(m) == 4, (
        "Expected 4. The top-left 0 stops the 3 by 3 square. If you only take min(above, left) and forget "
        "the diagonal f[r-1][c-1], you get 9.")


def test_best_square_can_end_anywhere():
    m = [[1, 1, 0],
         [1, 1, 0],
         [0, 0, 1]]
    assert maximal_square(m) == 4, (
        "Expected 4: the 2 by 2 square ends at (1, 1), not at the bottom-right cell. Keep the maximum over all cells.")


def test_random_against_brute_force():
    rng = random.Random(29)
    for _ in range(300):
        rows, cols = rng.randint(1, 7), rng.randint(1, 7)
        p = rng.choice([0.5, 0.75, 0.9])
        m = [[1 if rng.random() < p else 0 for _ in range(cols)] for _ in range(rows)]
        want = brute(m)
        got = maximal_square([row[:] for row in m])
        assert got == want, (
            f"matrix={m}: expected area {want}, got {got}. f[r][c] = 1 + min(above, left, diagonal) for a 1, "
            "0 for a 0; first row/column cells with a 1 are 1; answer = (max f) squared.")


def test_big_grid():
    make = ("import random\n"
            "rng = random.Random(2029)\n"
            "m = [[1 if rng.random() < 0.97 else 0 for _ in range(250)] for _ in range(250)]\n"
            "full = [[1] * 250 for _ in range(250)]\n")
    code = make + "from solution import maximal_square\nprint(maximal_square(m), maximal_square(full))\n"
    names = {}
    exec(make, names)                 # the same grid, built here for the checker
    r = run_big(code)
    assert r is not None, (
        "Time limit (10 s) on a 250 by 250 grid. Checking every square cell by cell is O(n^5); a recursion "
        "f(r, c) = 1 + min(three calls) without a cache is exponential: add a memo, or fill the table row by row.")
    assert r.returncode == 0, "Your code crashed on a 250 by 250 grid:\n" + r.stderr[-800:]
    want = [str(oracle(names["m"])), str(250 * 250)]
    assert r.stdout.split() == want, f"Big grids: expected areas {want}, got {r.stdout.split()}."
