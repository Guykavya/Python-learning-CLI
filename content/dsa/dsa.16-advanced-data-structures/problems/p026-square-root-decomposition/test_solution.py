import pathlib
import random
import subprocess
import sys

from solution import BlockSum

HERE = pathlib.Path(__file__).parent


def bound(bs):
    return 2 * (bs.B - 1) + bs.n // bs.B + 1 if hasattr(bs, "n") else None


def test_example():
    bs = BlockSum(list(range(1, 101)))
    assert bs.B == 10 and bs.blocks[:3] == [55, 155, 255], "B = isqrt(100) = 10; blocks hold the block sums."
    assert bs.query(0, 100) == (5050, 10), "Ten whole blocks: 10 steps."
    assert bs.query(7, 93) == (4343, 14), "3 single elements + 8 whole blocks + 3 single elements = 14 steps."
    assert bs.query(3, 5) == (9, 2)
    bs.update(50, 0)
    assert bs.query(7, 93) == (4292, 14)


def test_short_last_block():
    bs = BlockSum([1, 2, 3, 4, 5, 6, 7])          # n = 7, B = 2
    assert bs.B == 2 and bs.blocks == [3, 7, 11, 7], "The last block (only a[6]) still has its sum."
    assert bs.query(0, 7)[0] == 28 and bs.query(5, 6) == (6, 1) and bs.query(3, 3) == (0, 0)


def test_random_ops_and_step_bound():
    rng = random.Random(1626)
    for _ in range(20):
        n = rng.randint(1, 120)
        a = [rng.randint(-20, 20) for _ in range(n)]
        bs = BlockSum(a)
        B = bs.B
        limit = 2 * (B - 1) + n // B + 1
        for step in range(100):
            if rng.random() < 0.4:
                i, v = rng.randrange(n), rng.randint(-20, 20)
                a[i] = v
                bs.update(i, v)
            else:
                l = rng.randint(0, n)
                r = rng.randint(l, n)
                total, touched = bs.query(l, r)
                assert total == sum(a[l:r]), f"n={n}: query({l}, {r}) sum should be {sum(a[l:r])}."
                assert touched <= limit, (
                    f"n={n}, B={B}: query({l}, {r}) took {touched} steps, more than 2(B-1) + n//B + 1 = {limit}. "
                    "Use whole block sums in the middle.")


BIG_CODE = (
    "import random\n"
    "from solution import BlockSum\n"
    "rng = random.Random(1626)\n"
    "n = 10**5\n"
    "bs = BlockSum([rng.randint(-10**6, 10**6) for _ in range(n)])\n"
    "x = steps = 0\n"
    "for _ in range(2 * 10**4):\n"
    "    if rng.random() < 0.5:\n"
    "        bs.update(rng.randrange(n), rng.randint(-10**6, 10**6))\n"
    "    else:\n"
    "        s, t = bs.query(rng.randint(0, n // 10), rng.randint(9 * n // 10, n))\n"
    "        x ^= s\n"
    "        steps = max(steps, t)\n"
    "print(x, steps <= 2 * 315 + 317 + 1)\n"
)
BIG_WANT = ['110166587', 'True']


def test_large_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG_CODE], cwd=HERE, capture_output=True, text=True,
                           timeout=60, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, ("too slow: each query must take O(sqrt n) steps.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == BIG_WANT, f"Large input: expected {BIG_WANT}, got {r.stdout.split()}."
