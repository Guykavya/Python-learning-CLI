import pathlib
import random
import subprocess
import sys

from solution import RangeAddSum

HERE = pathlib.Path(__file__).parent


def test_example():
    rr = RangeAddSum([5, 3, 8, 6, 2, 7, 4, 1])
    assert (rr.range_sum(0, 8), rr.range_sum(2, 7)) == (36, 27)
    rr.add(2, 6, 10)
    assert (rr.range_sum(0, 8), rr.range_sum(2, 7), rr.range_sum(0, 2)) == (76, 67, 8), (
        "prefix(p) = base[p] + p * b1.prefix(p) - b2.prefix(p), with b2 over j * d[j].")
    rr.add(0, 8, -1)
    assert (rr.range_sum(0, 8), rr.range_sum(3, 5)) == (68, 26)


def test_random_ops_against_list():
    rng = random.Random(1621)
    for trial in range(3):
        n = 50
        a = [rng.randint(-20, 20) for _ in range(n)]
        rr = RangeAddSum(a)
        for step in range(2000):
            l = rng.randint(0, n)
            r = rng.randint(l, n)
            if rng.random() < 0.5:
                v = rng.randint(-9, 9)
                rr.add(l, r, v)
                for i in range(l, r):
                    a[i] += v
            else:
                assert rr.range_sum(l, r) == sum(a[l:r]), f"trial {trial} step {step}: range_sum({l}, {r}) wrong."


BIG_CODE = (
    "import random\n"
    "from solution import RangeAddSum\n"
    "rng = random.Random(1621)\n"
    "n = 2 * 10**5\n"
    "rr = RangeAddSum([rng.randint(-10**9, 10**9) for _ in range(n)])\n"
    "x = 0\n"
    "for _ in range(2 * 10**5):\n"
    "    l, r = rng.randint(0, n // 10), rng.randint(9 * n // 10, n)\n"
    "    if rng.random() < 0.5:\n"
    "        rr.add(l, r, rng.randint(-10**9, 10**9))\n"
    "    else:\n"
    "        x ^= rr.range_sum(l, r)\n"
    "print(x)\n"
)
BIG_WANT = ['38035841696032542']


def test_large_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG_CODE], cwd=HERE, capture_output=True, text=True,
                           timeout=40, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, ("too slow: a range add must be four Fenwick updates, not one per element.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == BIG_WANT, f"Large input: expected {BIG_WANT}, got {r.stdout.split()}."
