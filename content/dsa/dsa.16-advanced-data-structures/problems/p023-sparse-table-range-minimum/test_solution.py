import pathlib
import random
import subprocess
import sys

from solution import SparseMin

HERE = pathlib.Path(__file__).parent


def test_table_rows():
    sp = SparseMin([5, 3, 8, 6, 2, 7, 4, 1])
    assert sp.table == [[5, 3, 8, 6, 2, 7, 4, 1], [3, 3, 6, 2, 2, 4, 1], [3, 2, 2, 2, 1], [1]], (
        f"table[k][i] = min(a[i : i + 2**k]); got {sp.table}.")
    assert (sp.query(1, 7), sp.query(0, 8), sp.query(4, 5), sp.query(2, 4)) == (2, 1, 2, 6)


def test_not_power_of_two():
    sp = SparseMin([4, 9, 1, 7, 3])
    assert [len(row) for row in sp.table] == [5, 4, 2], "Rows of length n - 2**k + 1, while 2**k <= n."
    assert [sp.query(0, 5), sp.query(3, 5), sp.query(0, 2), sp.query(1, 4)] == [1, 3, 4, 1]


def test_every_range_against_min():
    rng = random.Random(1623)
    for _ in range(60):
        n = rng.randint(1, 40)
        a = [rng.randint(-50, 50) for _ in range(n)]
        sp = SparseMin(a)
        for l in range(n):
            for r in range(l + 1, n + 1):
                assert sp.query(l, r) == min(a[l:r]), f"query({l}, {r}) on {a} should be {min(a[l:r])}."


BIG_CODE = (
    "import random\n"
    "from solution import SparseMin\n"
    "rng = random.Random(1623)\n"
    "n = 2 * 10**5\n"
    "sp = SparseMin([rng.randint(-10**9, 10**9) for _ in range(n)])\n"
    "x = 0\n"
    "q = sp.query\n"
    "for _ in range(10**6):\n"
    "    l = rng.randrange(n)\n"
    "    x += q(l, rng.randint(l + 1, n))\n"
    "print(x)\n"
)
BIG_WANT = ['-999346079193185']


def test_large_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG_CODE], cwd=HERE, capture_output=True, text=True,
                           timeout=40, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, ("too slow: 10**6 queries over ranges of random length. Each query must be two table lookups, O(1).")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == BIG_WANT, f"Large input: expected {BIG_WANT}, got {r.stdout.split()}."
