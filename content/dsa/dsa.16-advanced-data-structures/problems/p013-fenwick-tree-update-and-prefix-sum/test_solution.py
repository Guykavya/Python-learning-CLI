import pathlib
import random
import subprocess
import sys

from solution import Fenwick

HERE = pathlib.Path(__file__).parent


def test_cells():
    fw = Fenwick(8)
    for i, x in enumerate([5, 3, 8, 6, 2, 7, 4, 1]):
        fw.add(i, x)
    assert len(fw.t) == 9, "t has n + 1 entries; t[0] is unused."
    assert fw.t[1:] == [5, 8, 8, 22, 2, 9, 4, 36], (
        f"Expected t[1:] = [5, 8, 8, 22, 2, 9, 4, 36], got {fw.t[1:]}. t[k] holds the lowbit(k) elements ending at "
        "1-indexed position k.")
    assert (fw.prefix(8), fw.prefix(4), fw.prefix(0)) == (36, 22, 0)
    fw.add(3, 94)
    assert fw.t[1:] == [5, 8, 8, 116, 2, 9, 4, 130], "add(3, 94) must touch only t[4] and t[8] (1-indexed 4 -> 8)."
    assert fw.prefix(5) == 118, "prefix(5) = 5 + 3 + 8 + 100 + 2 = 118."


def test_index_zero_and_last():
    code = (
        "from solution import Fenwick\n"
        "fw = Fenwick(5)\n"
        "fw.add(0, 7)\n"
        "fw.add(4, 1)\n"
        "print(fw.prefix(1), fw.prefix(5), fw.prefix(4))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "add(0, ...) never finished: with index 0, k & -k is 0 and k += k & -k never moves. Use k = i + 1.")
    assert r.stdout.split() == ["7", "8", "7"], f"Expected 7 8 7, got {r.stdout.split()} {r.stderr[-300:]}"


def test_random_ops_against_list():
    rng = random.Random(1613)
    n = 50
    a = [0] * n
    fw = Fenwick(n)
    for step in range(2000):
        if rng.random() < 0.5:
            i, v = rng.randrange(n), rng.randint(-20, 20)
            a[i] += v
            fw.add(i, v)
        else:
            r = rng.randint(0, n)
            assert fw.prefix(r) == sum(a[:r]), f"step {step}: prefix({r}) should be {sum(a[:r])}."


BIG_CODE = (
    "import random\n"
    "from solution import Fenwick\n"
    "rng = random.Random(1613)\n"
    "n = 2 * 10**5\n"
    "fw = Fenwick(n)\n"
    "x = 0\n"
    "for _ in range(2 * 10**5):\n"
    "    if rng.random() < 0.5:\n"
    "        fw.add(rng.randrange(n), rng.randint(-10**9, 10**9))\n"
    "    else:\n"
    "        x ^= fw.prefix(rng.randint(9 * n // 10, n))\n"
    "print(x)\n"
)
BIG_WANT = ['-165984317352']


def test_large_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG_CODE], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, "too slow: add and prefix must be O(log n): follow the lowbit jumps."
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == BIG_WANT, f"Large input: expected {BIG_WANT}, got {r.stdout.split()}."
