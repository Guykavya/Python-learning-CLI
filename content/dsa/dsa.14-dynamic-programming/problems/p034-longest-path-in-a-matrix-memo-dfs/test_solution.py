import pathlib
import random
import subprocess
import sys

from solution import longest_increasing_path

HERE = pathlib.Path(__file__).parent


def brute(matrix):
    """DFS from every cell with no memo (small matrices only)."""
    rows, cols = len(matrix), len(matrix[0])

    def walk(r, c):
        best = 1
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and matrix[nr][nc] > matrix[r][c]:
                best = max(best, 1 + walk(nr, nc))
        return best

    return max(walk(r, c) for r in range(rows) for c in range(cols))


def run_big(code, limit):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=limit, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_examples():
    got = longest_increasing_path([[9, 9, 4], [6, 6, 8], [2, 1, 1]])
    assert got == 4, f"Expected 4 (the path 1 -> 2 -> 6 -> 9), got {got}."
    got = longest_increasing_path([[3, 4, 5], [3, 2, 6], [2, 2, 1]])
    assert got == 4, f"Expected 4 (the path 3 -> 4 -> 5 -> 6), got {got}."


def test_edges():
    assert longest_increasing_path([[7]]) == 1, "A single cell is a path of length 1: count cells, not steps."
    assert longest_increasing_path([[5, 5], [5, 5]]) == 1, (
        "Equal values: no step is allowed, because the next value must be STRICTLY larger. Use >, not >=.")
    assert longest_increasing_path([[1, 2, 3, 4, 5]]) == 5, "One row 1..5: the path is the whole row."
    assert longest_increasing_path([[5], [4], [3], [2], [1]]) == 5, (
        "One column 5..1: the path goes UP from 1 to 5. Moves in all four directions are allowed.")


def test_all_four_directions():
    m = [[1, 2, 3],
         [8, 9, 4],
         [7, 6, 5]]
    got = longest_increasing_path(m)
    assert got == 9, (
        f"The spiral 1 -> 2 -> ... -> 9 uses right, down, left and up moves: expected 9, got {got}. "
        "Only moving right and down (as in chapter section 8) is not enough here.")


def test_no_wrap_around():
    m = [[1, 9],
         [9, 9],
         [2, 9]]
    got = longest_increasing_path(m)
    assert got == 2, (
        f"Expected 2, got {got}. If you got 3, a negative index wrapped around: matrix[-1] is the last row "
        "in Python, not 'outside the grid'. Check 0 <= nr < rows and 0 <= nc < cols first.")


def test_start_anywhere():
    m = [[9, 8, 7],
         [1, 2, 6],
         [9, 3, 4]]
    got = longest_increasing_path(m)
    assert got == 8, (
        f"Expected 8 (1 -> 2 -> 3 -> 4 -> 6 -> 7 -> 8 -> 9), got {got}. The best path does not have to "
        "start at (0, 0): take the maximum of f over every cell.")


def test_random_against_brute_force():
    rng = random.Random(3434)
    for _ in range(200):
        rows, cols = rng.randint(1, 4), rng.randint(1, 4)
        m = [[rng.randint(0, 6) for _ in range(cols)] for _ in range(rows)]
        want = brute(m)
        got = longest_increasing_path([row[:] for row in m])
        assert got == want, (
            f"matrix={m}: expected {want}, got {got}. f(r, c) = 1 + max f of the strictly larger neighbours "
            "(1 if there is none); the answer is the max over all cells.")


def test_large_needs_a_memo():
    code = (
        "import random\n"
        "from solution import longest_increasing_path\n"
        "n = 150\n"
        "print(longest_increasing_path([[r + c for c in range(n)] for r in range(n)]))\n"
        "rng = random.Random(34)\n"
        "print(longest_increasing_path([[rng.randint(0, 10**6) for _ in range(n)] for _ in range(n)]))\n"
        "rows, cols = 7, 100\n"
        "snake = [[0] * cols for _ in range(rows)]\n"
        "v = 0\n"
        "for r in range(rows):\n"
        "    order = range(cols) if r % 2 == 0 else range(cols - 1, -1, -1)\n"
        "    for c in order:\n"
        "        snake[r][c] = v\n"
        "        v += 1\n"
        "print(longest_increasing_path(snake))\n"
    )
    r = run_big(code, 20)
    assert r is not None, (
        "Time limit (20 s) on a 150 by 150 matrix: without a memo the DFS repeats the same sub-paths an "
        "exponential number of times. Store f(r, c) once it is known.")
    if "RecursionError" in r.stderr:
        assert False, (
            "RecursionError on a 700-cell snake path: one recursion level per cell is fine (700 < 1000), so "
            "check that equal values are not stepped onto and that each level adds only one frame.")
    assert r.returncode == 0, "Your code crashed on a large matrix:\n" + r.stderr[-800:]
    out = r.stdout.split()
    assert out[:1] == ["299"], f"150 by 150 matrix with value r + c: the longest path has 299 cells, got {out[:1]}."
    assert out[2:] == ["700"], f"The 7 by 100 snake visits every cell in order: expected 700, got {out[2:]}."
    assert out[1:2] == ["12"], f"Random 150 by 150 matrix (seed 34): expected 12, got {out[1:2]}."
