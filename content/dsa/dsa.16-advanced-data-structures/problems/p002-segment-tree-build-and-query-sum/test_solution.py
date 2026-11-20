import pathlib
import random
import subprocess
import sys

from solution import SegTree

HERE = pathlib.Path(__file__).parent


def test_chapter_tree():
    st = SegTree([5, 3, 8, 6, 2, 7, 4, 1])
    assert st.t[1:16] == [36, 22, 14, 8, 14, 9, 5, 5, 3, 8, 6, 2, 7, 4, 1], (
        f"t[1:16] should be the chapter's tree, got {st.t[1:16]}. Root at 1, children 2i and 2i + 1.")
    assert (st.query(2, 7), st.query(0, 8), st.query(3, 4), st.query(5, 5)) == (27, 36, 6, 0)


def test_not_power_of_two():
    st = SegTree([1, 2, 3, 4, 5])
    assert st.t[1] == 15 and st.t[2] == 3 and st.t[3] == 12, (
        "For n = 5: root [0,5) = 15, left child [0,2) = 3, right child [2,5) = 12 (mid = (lo + hi) // 2).")
    assert len(st.t) >= 16, "The recursive layout needs room for index 15 when n = 5: use 4n."
    assert [st.query(l, r) for l, r in [(0, 5), (1, 4), (4, 5), (2, 2)]] == [15, 9, 5, 0]


def test_single_element():
    st = SegTree([42])
    assert st.query(0, 1) == 42 and st.query(0, 0) == 0 and st.query(1, 1) == 0


def test_random_against_sum():
    rng = random.Random(1602)
    for _ in range(40):
        n = rng.randint(1, 50)
        a = [rng.randint(-50, 50) for _ in range(n)]
        st = SegTree(a)
        for _ in range(50):
            l = rng.randint(0, n)
            r = rng.randint(l, n)
            assert st.query(l, r) == sum(a[l:r]), f"query({l}, {r}) on {a} should be {sum(a[l:r])}."


BIG_CODE = (
    "import random\n"
    "from solution import SegTree\n"
    "rng = random.Random(162)\n"
    "n = 2 * 10**5\n"
    "st = SegTree([rng.randint(-10**6, 10**6) for _ in range(n)])\n"
    "x = 0\n"
    "for _ in range(10**5):\n"
    "    x ^= st.query(rng.randint(0, n // 10), rng.randint(9 * n // 10, n))\n"
    "print(x)\n"
)
BIG_WANT = ['189803260']


def test_large_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG_CODE], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "too slow: each query must be O(log n). 10**5 queries over ranges of about 1.6 * 10**5 elements: return "
        "whole nodes that lie inside the query instead of adding up elements.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == BIG_WANT, f"Large input: expected {BIG_WANT}, got {r.stdout.split()}."
