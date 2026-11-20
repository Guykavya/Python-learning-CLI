import pathlib
import random
import subprocess
import sys

from solution import Fenwick

HERE = pathlib.Path(__file__).parent


def test_example():
    fw = Fenwick(8, [5, 3, 8, 6, 2, 7, 4, 1])
    assert fw.t[1:] == [5, 8, 8, 22, 2, 9, 4, 36], f"The built cells should match the chapter, got {fw.t[1:]}."
    assert (fw.range_sum(2, 7), fw.range_sum(3, 3), fw.get(5)) == (27, 0, 7), (
        "range_sum(l, r) = prefix(r) - prefix(l) for half-open ranges.")
    fw.set(3, 100)
    assert (fw.range_sum(2, 7), fw.get(3)) == (121, 100), "set(i, v) adds the difference v - get(i)."
    fw.set(3, 100)
    assert fw.get(3) == 100, "Setting the same value twice must not change anything."


def test_range_from_zero():
    fw = Fenwick(3, [4, 5, 6])
    assert fw.range_sum(0, 2) == 9 and fw.range_sum(0, 0) == 0 and fw.range_sum(2, 3) == 6


def test_build_matches_adds():
    rng = random.Random(1614)
    for _ in range(50):
        n = rng.randint(1, 40)
        a = [rng.randint(-9, 9) for _ in range(n)]
        slow = Fenwick(n)
        for i, x in enumerate(a):
            slow.add(i, x)
        assert Fenwick(n, a).t == slow.t, f"The O(n) build of {a} gives other cells than n calls to add."


def test_random_ops_against_list():
    rng = random.Random(16140)
    n = 50
    a = [rng.randint(-20, 20) for _ in range(n)]
    fw = Fenwick(n, a)
    for step in range(2000):
        kind = rng.random()
        if kind < 0.3:
            i, v = rng.randrange(n), rng.randint(-20, 20)
            a[i] = v
            fw.set(i, v)
        elif kind < 0.5:
            i, v = rng.randrange(n), rng.randint(-20, 20)
            a[i] += v
            fw.add(i, v)
        else:
            l = rng.randint(0, n)
            r = rng.randint(l, n)
            assert fw.range_sum(l, r) == sum(a[l:r]), f"step {step}: range_sum({l}, {r}) wrong."


BIG_CODE = (
    "import random, time\n"
    "from solution import Fenwick\n"
    "rng = random.Random(1614)\n"
    "n = 10**6\n"
    "a = [rng.randint(-10**9, 10**9) for _ in range(n)]\n"
    "t0 = time.perf_counter()\n"
    "fw = Fenwick(n, a)\n"
    "build = time.perf_counter() - t0\n"
    "x = 0\n"
    "for _ in range(2 * 10**5):\n"
    "    if rng.random() < 0.5:\n"
    "        fw.set(rng.randrange(n), rng.randint(-10**9, 10**9))\n"
    "    else:\n"
    "        x ^= fw.range_sum(rng.randint(0, n // 10), rng.randint(9 * n // 10, n))\n"
    "print(x)\n"
    "import sys\n"
    "print('build', round(build, 2), file=sys.stderr)\n"
)
BIG_WANT = ['109094690873']


def test_large_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG_CODE], cwd=HERE, capture_output=True, text=True,
                           timeout=40, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, "too slow: build in O(n), and every operation must be O(log n)."
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == BIG_WANT, f"Large input: expected {BIG_WANT}, got {r.stdout.split()}."
    build = float(r.stderr.split()[-1])
    assert build < 3.0, (
        f"Building from 10**6 values took {build} s. Calling add n times is O(n log n); push each cell into its "
        "parent once for an O(n) build.")
