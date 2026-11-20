import pathlib
import random
import subprocess
import sys

from solution import LazySum

HERE = pathlib.Path(__file__).parent


def test_example():
    lz = LazySum([5, 3, 8, 6, 2, 7, 4, 1])
    assert (lz.query(0, 8), lz.query(2, 7)) == (36, 27)
    lz.add(1, 6, 10)
    assert (lz.query(0, 8), lz.query(2, 7), lz.query(0, 1), lz.query(5, 6)) == (86, 67, 5, 17)
    lz.add(0, 8, -1)
    assert (lz.query(0, 8), lz.query(3, 4)) == (78, 15)


def test_push_before_descending():
    lz = LazySum([2, 4, 6, 8])
    lz.add(0, 4, 10)           # the note sits on the root
    lz.add(1, 2, 5)            # must push the root's note before going inside
    got = [lz.query(i, i + 1) for i in range(4)]
    assert got == [12, 19, 16, 18], (
        f"Expected [12, 19, 16, 18], got {got}. Push the tag down before you descend, in add AND in query.")


def test_predict_from_chapter():
    t = LazySum([1, 1, 1, 1])
    t.add(0, 4, 2)
    t.add(0, 2, 3)
    t.add(1, 3, 100)
    assert [t.query(i, i + 1) for i in range(4)] == [6, 106, 103, 3] and t.query(0, 4) == 218


def test_random_ops_against_list():
    rng = random.Random(1610)
    for trial in range(3):
        n = 50
        a = [rng.randint(-20, 20) for _ in range(n)]
        lz = LazySum(a)
        for step in range(2000):
            l = rng.randint(0, n)
            r = rng.randint(l, n)
            if rng.random() < 0.5:
                v = rng.randint(-9, 9)
                lz.add(l, r, v)
                for i in range(l, r):
                    a[i] += v
            else:
                assert lz.query(l, r) == sum(a[l:r]), f"trial {trial} step {step}: query({l}, {r}) wrong."


BIG_CODE = (
    "import random\n"
    "from solution import LazySum\n"
    "rng = random.Random(1610)\n"
    "n = 10**5\n"
    "lz = LazySum([rng.randint(-10**9, 10**9) for _ in range(n)])\n"
    "x = 0\n"
    "for _ in range(10**5):\n"
    "    l, r = rng.randint(0, n // 10), rng.randint(9 * n // 10, n)\n"
    "    if rng.random() < 0.5:\n"
    "        lz.add(l, r, rng.randint(-10**9, 10**9))\n"
    "    else:\n"
    "        x ^= lz.query(l, r)\n"
    "print(x)\n"
)
BIG_WANT = ['8759076804303697']


def test_large_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG_CODE], cwd=HERE, capture_output=True, text=True,
                           timeout=60, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "too slow: each add and query must be O(log n). For a covered node, change its sum and leave a lazy tag; "
        "do not visit every element of the range.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == BIG_WANT, f"Large input: expected {BIG_WANT}, got {r.stdout.split()}."
