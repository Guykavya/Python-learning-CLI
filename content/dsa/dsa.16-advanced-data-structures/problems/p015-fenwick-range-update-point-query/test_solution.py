import pathlib
import random
import subprocess
import sys

from solution import RangeAdder

HERE = pathlib.Path(__file__).parent


def test_example():
    ra = RangeAdder([5, 3, 8, 6, 2, 7, 4, 1])
    ra.add(2, 6, 10)
    ra.add(0, 8, -1)
    ra.add(4, 5, 100)
    got = [ra.get(i) for i in range(8)]
    assert got == [4, 2, 17, 15, 111, 16, 3, 0], f"Expected [4, 2, 17, 15, 111, 16, 3, 0], got {got}."


def test_edges_of_the_range():
    ra = RangeAdder([0] * 5)
    ra.add(1, 3, 7)
    got = [ra.get(i) for i in range(5)]
    assert got == [0, 7, 7, 0, 0], (
        f"add(1, 3, 7) changes positions 1 and 2 only, got {got}. d[1] += 7, d[3] -= 7; get(i) = base + prefix(i + 1).")


def test_random_ops_against_list():
    rng = random.Random(1615)
    n = 50
    a = [rng.randint(-20, 20) for _ in range(n)]
    ra = RangeAdder(a)
    for step in range(2000):
        if rng.random() < 0.5:
            l = rng.randint(0, n)
            r = rng.randint(l, n)
            v = rng.randint(-9, 9)
            ra.add(l, r, v)
            for i in range(l, r):
                a[i] += v
        else:
            i = rng.randrange(n)
            assert ra.get(i) == a[i], f"step {step}: get({i}) should be {a[i]}."


BIG_CODE = (
    "import random\n"
    "from solution import RangeAdder\n"
    "rng = random.Random(1615)\n"
    "n = 2 * 10**5\n"
    "ra = RangeAdder([rng.randint(-10**9, 10**9) for _ in range(n)])\n"
    "x = 0\n"
    "for _ in range(2 * 10**5):\n"
    "    if rng.random() < 0.5:\n"
    "        ra.add(rng.randint(0, n // 10), rng.randint(9 * n // 10, n), rng.randint(-10**9, 10**9))\n"
    "    else:\n"
    "        x ^= ra.get(rng.randrange(n))\n"
    "print(x)\n"
)
BIG_WANT = ['-157356097233']


def test_large_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG_CODE], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, "too slow: a range add must be two Fenwick updates, not one per element."
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == BIG_WANT, f"Large input: expected {BIG_WANT}, got {r.stdout.split()}."
