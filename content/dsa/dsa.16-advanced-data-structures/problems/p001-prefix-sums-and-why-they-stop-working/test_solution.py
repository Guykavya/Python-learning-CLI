import pathlib
import random
import subprocess
import sys

from solution import PrefixSums

HERE = pathlib.Path(__file__).parent


def test_example():
    ps = PrefixSums([5, 3, 8, 6, 2, 7, 4, 1])
    assert ps.pre == [0, 5, 8, 16, 22, 24, 31, 35, 36], f"pre should be [0, 5, 8, ...], got {ps.pre}."
    assert (ps.query(2, 7), ps.query(0, 8), ps.query(4, 4)) == (27, 36, 0), (
        "Half-open ranges: query(l, r) = pre[r] - pre[l]; the empty range gives 0.")
    assert ps.set(3, 100) == 5, "set(3, ...) on n = 8 repairs pre[4] .. pre[8]: 5 entries."
    assert ps.query(2, 7) == 121 and ps.query(0, 4) == 116, "After a[3] = 100 the sums must include the new value."
    assert ps.set(7, 1) == 1 and ps.set(0, 5) == 8


def test_cost_counter():
    ps = PrefixSums([0] * 1000)
    total = sum(ps.set(i, 1) for i in range(0, 1000, 10))
    assert total == sum(1000 - i for i in range(0, 1000, 10)), (
        "set(i, v) must return n - i, the number of prefix entries that contain a[i].")
    assert ps.query(0, 1000) == 100


def test_random_against_naive():
    rng = random.Random(1601)
    for _ in range(40):
        n = 50
        a = [rng.randint(-20, 20) for _ in range(n)]
        ps = PrefixSums(a)
        for _ in range(50):
            if rng.random() < 0.4:
                i, v = rng.randrange(n), rng.randint(-20, 20)
                a[i] = v
                assert ps.set(i, v) == n - i
            else:
                l = rng.randint(0, n)
                r = rng.randint(l, n)
                assert ps.query(l, r) == sum(a[l:r]), f"query({l}, {r}) should be {sum(a[l:r])}."


BIG_CODE = (
    "import random\n"
    "from solution import PrefixSums\n"
    "rng = random.Random(16)\n"
    "n = 10**6\n"
    "ps = PrefixSums([rng.randint(-10**6, 10**6) for _ in range(n)])\n"
    "x = 0\n"
    "for _ in range(2 * 10**5):\n"
    "    x ^= ps.query(rng.randint(0, n // 10), rng.randint(9 * n // 10, n))\n"
    "print(x)\n"
)
BIG_WANT = ['-143372117']


def test_queries_are_constant_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG_CODE], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "too slow: each query must be O(1). 2 * 10**5 queries over ranges of about 8 * 10**5 elements cannot add "
        "up the elements; use pre[r] - pre[l].")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == BIG_WANT, f"Large input: expected {BIG_WANT}, got {r.stdout.split()}."
