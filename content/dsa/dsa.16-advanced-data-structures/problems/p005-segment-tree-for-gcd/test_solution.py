import math
import pathlib
import random
import subprocess
import sys

from solution import GcdTree

HERE = pathlib.Path(__file__).parent


def test_example():
    gt = GcdTree([12, 18, 30, 8, 20, 45])
    assert (gt.query(0, 3), gt.query(2, 5), gt.query(3, 4), gt.query(5, 5)) == (6, 2, 8, 0), (
        "gcd(12, 18, 30) = 6, gcd(30, 8, 20) = 2, a single element is itself, the empty range is 0.")
    gt.update(3, 6)
    assert gt.query(0, 4) == 6


def test_identity_and_zeros():
    gt = GcdTree([4, 0, 6, 0])
    assert gt.query(0, 4) == 2 and gt.query(1, 2) == 0 and gt.query(1, 3) == 6, (
        "Zeros are allowed: gcd(0, x) = x, gcd(0, 0) = 0. The identity is 0, not 1.")
    gt = GcdTree([9, 6, 15])
    assert gt.query(1, 3) == 3, "gcd(6, 15) = 3: with identity 1 you would get 1."


def test_random_ops_against_list():
    rng = random.Random(1605)
    n = 50
    a = [rng.choice([0, 6, 12, 18, 9, 30, 7, 14]) for _ in range(n)]
    gt = GcdTree(a)
    for step in range(2000):
        if rng.random() < 0.5:
            i, v = rng.randrange(n), rng.choice([0, 4, 6, 8, 12, 9, 27, 5])
            a[i] = v
            gt.update(i, v)
        else:
            l = rng.randint(0, n)
            r = rng.randint(l, n)
            want = math.gcd(*a[l:r]) if r > l else 0
            assert gt.query(l, r) == want, f"step {step}: query({l}, {r}) should be {want}."


BIG_CODE = (
    "import random\n"
    "from solution import GcdTree\n"
    "rng = random.Random(165)\n"
    "n = 2 * 10**5\n"
    "gt = GcdTree([rng.randint(1, 10**6) * 6 for _ in range(n)])\n"
    "x = 0\n"
    "for _ in range(10**5):\n"
    "    if rng.random() < 0.5:\n"
    "        gt.update(rng.randrange(n), rng.randint(1, 10**6) * rng.choice([6, 12, 30]))\n"
    "    else:\n"
    "        x += gt.query(rng.randint(0, n // 10), rng.randint(9 * n // 10, n))\n"
    "print(x)\n"
)
BIG_WANT = ['300468']


def test_large_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG_CODE], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, "too slow: each query must be O(log n) gcd calls, not one per element."
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == BIG_WANT, f"Large input: expected {BIG_WANT}, got {r.stdout.split()}."
