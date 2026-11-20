import pathlib
import random
import subprocess
import sys

from solution import SegTree

HERE = pathlib.Path(__file__).parent


def test_chapter_update():
    st = SegTree([5, 3, 8, 6, 2, 7, 4, 1])
    st.update(3, 100)
    assert st.t[1:16] == [130, 116, 14, 8, 108, 9, 5, 5, 3, 8, 100, 2, 7, 4, 1], (
        f"After update(3, 100) only the path 11 -> 5 -> 2 -> 1 changes, got {st.t[1:16]}.")
    assert (st.query(2, 7), st.query(0, 4)) == (121, 116)


def test_set_not_add():
    st = SegTree([1, 1, 1])
    st.update(1, 5)
    st.update(1, 5)
    assert st.query(0, 3) == 7, "update(i, v) sets a[i] = v; doing it twice must not add twice."


def test_mid_goes_right():
    st = SegTree([0, 0, 0, 0])
    st.update(2, 9)
    assert st.query(2, 3) == 9 and st.query(0, 2) == 0, (
        "Position 2 = mid of [0, 4) belongs to the RIGHT child [2, 4): go left only if i < mid.")


def test_random_ops_against_list():
    rng = random.Random(1603)
    n = 50
    a = [rng.randint(-50, 50) for _ in range(n)]
    st = SegTree(a)
    for step in range(2000):
        if rng.random() < 0.5:
            i, v = rng.randrange(n), rng.randint(-50, 50)
            a[i] = v
            st.update(i, v)
        else:
            l = rng.randint(0, n)
            r = rng.randint(l, n)
            assert st.query(l, r) == sum(a[l:r]), (
                f"step {step}: query({l}, {r}) should be {sum(a[l:r])}. After a leaf changes, recompute every "
                "ancestor from its two children on the way back up.")


BIG_CODE = (
    "import random\n"
    "from solution import SegTree\n"
    "rng = random.Random(163)\n"
    "n = 2 * 10**5\n"
    "st = SegTree([rng.randint(-10**6, 10**6) for _ in range(n)])\n"
    "x = 0\n"
    "for _ in range(10**5):\n"
    "    if rng.random() < 0.5:\n"
    "        st.update(rng.randrange(n), rng.randint(-10**6, 10**6))\n"
    "    else:\n"
    "        x ^= st.query(rng.randint(0, n // 10), rng.randint(9 * n // 10, n))\n"
    "print(x)\n"
)
BIG_WANT = ['415705876']


def test_large_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG_CODE], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "too slow: each query and update must be O(log n). Do not rebuild the tree or add up ranges.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == BIG_WANT, f"Large input: expected {BIG_WANT}, got {r.stdout.split()}."
