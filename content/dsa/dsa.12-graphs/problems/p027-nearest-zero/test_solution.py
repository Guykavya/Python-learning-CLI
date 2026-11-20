import pathlib
import random
import subprocess
import sys

from solution import nearest_zero

HERE = pathlib.Path(__file__).parent


def brute(mat):
    zeros = [(r, c) for r, row in enumerate(mat) for c, x in enumerate(row) if x == 0]
    return [[min(abs(r - a) + abs(c - b) for a, b in zeros) for c in range(len(mat[0]))] for r in range(len(mat))]


def test_examples():
    assert nearest_zero([[0, 0, 0], [0, 1, 0], [1, 1, 1]]) == [[0, 0, 0], [0, 1, 0], [1, 2, 1]], (
        "First example: the bottom middle cell is 2 steps from the nearest 0.")
    assert nearest_zero([[1, 1, 1], [1, 1, 1], [1, 1, 0]]) == [[4, 3, 2], [3, 2, 1], [2, 1, 0]], (
        "Second example: the only 0 is bottom right, so the top left cell is 4 steps away. A single DP pass from "
        "the top left cannot see a 0 that lies below/right.")


def test_input_not_changed_and_rows_independent():
    mat = [[1, 0], [1, 1]]
    keep = [row[:] for row in mat]
    result = nearest_zero(mat)
    assert mat == keep, "nearest_zero changed the input matrix. Build a new one."
    assert result == [[1, 0], [2, 1]], "[[1,0],[1,1]] gives [[1,0],[2,1]]."
    assert result[0] is not result[1], "The rows of the result are the same list object: use a list comprehension."


def test_single_cells_and_lines():
    assert nearest_zero([[0]]) == [[0]], "A single 0 has distance 0."
    assert nearest_zero([[1, 1, 0, 1, 1, 1]]) == [[2, 1, 0, 1, 2, 3]], "A single row: distances grow in both directions."
    assert nearest_zero([[1], [0], [1], [1]]) == [[1], [0], [1], [2]], "A single column."


def test_random_against_brute_force():
    rng = random.Random(27)
    for _ in range(300):
        rows, cols = rng.randint(1, 9), rng.randint(1, 9)
        mat = [[0 if rng.random() < 0.15 else 1 for _ in range(cols)] for _ in range(rows)]
        mat[rng.randrange(rows)][rng.randrange(cols)] = 0
        assert nearest_zero(mat) == brute(mat), (
            f"Wrong distances for {mat}. Start the BFS from ALL zeros at once, use 4 directions, and give a cell "
            "its distance the first time the wave reaches it.")


def test_big_matrix_time_limit():
    code = (
        "from solution import nearest_zero\n"
        "n = 300\n"
        "mat = [[1] * n for _ in range(n)]\n"
        "mat[0][0] = 0\n"
        "d = nearest_zero(mat)\n"
        "print(d[n - 1][n - 1], d[150][7], sum(map(sum, d)))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        raise AssertionError(
            "Time limit (10 s) on a 300 x 300 matrix with one 0: a BFS for every cell is 90,000 searches. "
            "Use ONE BFS that starts from all zeros at once.") from None
    assert r.returncode == 0, "Your code crashed on the big matrix:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["598", "157", str(300 * 299 * 300)], (
        f"Wrong values on the 300 x 300 matrix (expected far corner 598): got {r.stdout.strip()!r}.")
