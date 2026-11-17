import random

import pytest

from solution import kth_smallest


def make_matrix(rng, rows, cols, step=3, low=0):
    """Rows and columns are sorted (not strictly): each cell is the larger of its upper and left neighbour plus 0..step."""
    m = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            up = m[i - 1][j] if i else low
            left = m[i][j - 1] if j else low
            m[i][j] = max(up, left) + rng.randint(0, step)
    return m


def flat_sorted(matrix):
    return sorted(v for row in matrix for v in row)


class CountingRow:
    """A row that counts every cell you read (by index, by slice or by iteration)."""

    def __init__(self, values, counter):
        self._v = values
        self._c = counter

    def __len__(self):
        return len(self._v)

    def __getitem__(self, i):
        got = self._v[i]
        self._c[0] += len(got) if isinstance(i, slice) else 1
        return got

    def __iter__(self):
        for x in self._v:
            self._c[0] += 1
            yield x


def test_the_example():
    matrix = [[1, 5, 9], [10, 11, 13], [12, 13, 15]]
    got = [kth_smallest(matrix, k) for k in range(1, 10)]
    assert got == [1, 5, 9, 10, 11, 12, 13, 13, 15], (
        f"k = 1..9 should give [1, 5, 9, 10, 11, 12, 13, 13, 15], got {got}. The two 13s count twice.")


def test_tiny_matrices():
    assert kth_smallest([[7]], 1) == 7, "one cell: k = 1 is that cell."
    assert kth_smallest([[1, 2, 3, 4]], 3) == 3, "a single row: the k-th item of the row."
    assert kth_smallest([[1], [2], [3], [4]], 4) == 4, "a single column: the k-th item of the column."
    assert kth_smallest([[1, 2], [1, 3]], 2) == 1, "equal numbers count as often as they appear: sorted is 1, 1, 2, 3."


def test_all_equal_numbers():
    matrix = [[5] * 4 for _ in range(3)]
    for k in (1, 6, 12):
        assert kth_smallest(matrix, k) == 5, f"every number is 5, so the {k}-th smallest is 5."


def test_negative_numbers():
    matrix = [[-9, -5, -1], [-7, -3, 0], [-6, 2, 8]]
    want = flat_sorted(matrix)
    for k in range(1, 10):
        assert kth_smallest(matrix, k) == want[k - 1], (
            f"k = {k}: expected {want[k - 1]}, got {kth_smallest(matrix, k)}. Do not start a search at 0: numbers can be negative.")


def test_first_and_last_k():
    rng = random.Random(8)
    matrix = make_matrix(rng, 7, 5)
    want = flat_sorted(matrix)
    assert kth_smallest(matrix, 1) == want[0], "k = 1 is the top-left cell."
    assert kth_smallest(matrix, 35) == want[-1], "k = n * m is the bottom-right cell."


def test_the_matrix_is_not_changed():
    matrix = [[1, 3, 5], [2, 4, 6], [7, 8, 9]]
    keep = [row[:] for row in matrix]
    kth_smallest(matrix, 5)
    assert matrix == keep, "your function changed the matrix."


@pytest.mark.parametrize("seed", range(80))
def test_random_matrices(seed):
    rng = random.Random(seed)
    rows, cols = rng.randint(1, 9), rng.randint(1, 9)
    matrix = make_matrix(rng, rows, cols, step=rng.choice([0, 1, 3, 10]), low=rng.randint(-20, 0))
    want = flat_sorted(matrix)
    k = rng.randint(1, rows * cols)
    got = kth_smallest(matrix, k)
    assert got == want[k - 1], (
        f"{rows}x{cols} matrix {matrix}, k = {k}: expected {want[k - 1]}, got {got}. "
        "Check the number of pops (k - 1, then look at the top) and that equal numbers count several times.")


def test_a_big_matrix_with_k_in_the_middle():
    rng = random.Random(4)
    matrix = make_matrix(rng, 300, 300)
    want = flat_sorted(matrix)
    for k in (1, 77, 45000, 89999, 90000):
        assert kth_smallest(matrix, k) == want[k - 1], f"300x300 matrix, k = {k}: wrong answer."


def test_small_k_must_not_read_the_whole_matrix():
    rng = random.Random(10)
    data = make_matrix(rng, 1000, 1000)
    want = flat_sorted(data)
    counter = [0]
    matrix = [CountingRow(row, counter) for row in data]
    for k in (1, 50, 1000):
        counter[0] = 0
        got = kth_smallest(matrix, k)
        assert got == want[k - 1], f"1000x1000 matrix, k = {k}: expected {want[k - 1]}, got {got}."
        assert counter[0] <= 100_000, (
            f"for k = {k} you read {counter[0]:,} of the 1,000,000 cells. Flattening (or pushing every cell into the heap) "
            "reads them all. Use a heap with one cell per row (only the first min(n, k) rows), or a binary search on the value.")
