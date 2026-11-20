import math
import pathlib
import random
import subprocess
import sys

from solution import MinTree

HERE = pathlib.Path(__file__).parent


def test_example():
    mt = MinTree([5, 3, 8, 6, 2, 7, 4, 1])
    assert (mt.query(0, 4), mt.query(4, 8), mt.query(2, 7)) == (3, 1, 2)
    mt.update(5, -9)
    assert (mt.query(2, 7), mt.query(0, 2)) == (-9, 3)


def test_identity():
    mt = MinTree([5, 3, 8, 6])
    got = mt.query(1, 3)
    assert got == 3, (
        f"query(1, 3) of [5, 3, 8, 6] is 3, got {got}. If you got 0, the 'no overlap' case returns 0: the "
        "identity for min is math.inf.")
    assert mt.query(2, 2) == math.inf, "The empty range returns math.inf."


def test_random_ops_against_list():
    rng = random.Random(1604)
    n = 50
    a = [rng.randint(1, 100) for _ in range(n)]
    mt = MinTree(a)
    for step in range(2000):
        if rng.random() < 0.5:
            i, v = rng.randrange(n), rng.randint(-100, 100)
            a[i] = v
            mt.update(i, v)
        else:
            l = rng.randint(0, n)
            r = rng.randint(l, n)
            want = min(a[l:r], default=math.inf)
            assert mt.query(l, r) == want, f"step {step}: query({l}, {r}) should be {want}."


BIG_CODE = (
    "import random\n"
    "from solution import MinTree\n"
    "rng = random.Random(164)\n"
    "n = 2 * 10**5\n"
    "mt = MinTree([rng.randint(-10**9, 10**9) for _ in range(n)])\n"
    "x = 0\n"
    "for _ in range(10**5):\n"
    "    if rng.random() < 0.5:\n"
    "        mt.update(rng.randrange(n), rng.randint(-10**9, 10**9))\n"
    "    else:\n"
    "        x ^= mt.query(rng.randint(0, n // 10), rng.randint(9 * n // 10, n))\n"
    "print(x)\n"
)
BIG_WANT = ['-999992068']


def test_large_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG_CODE], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, "too slow: each query must be O(log n). Do not call min() on a slice of the array."
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == BIG_WANT, f"Large input: expected {BIG_WANT}, got {r.stdout.split()}."
