import pathlib
import random
import subprocess
import sys

from solution import BestRun

HERE = pathlib.Path(__file__).parent


def kadane(xs):
    best = cur = xs[0]
    for x in xs[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best


def test_example():
    br = BestRun([2, -5, 4, -1, 3, -6, 5])
    assert (br.best(0, 7), br.best(2, 5), br.best(0, 2), br.best(5, 7)) == (6, 6, 2, 5)
    br.update(1, 10)
    assert br.best(0, 7) == 18, "After a[1] = 10: 2 + 10 + 4 - 1 + 3 = 18."


def test_non_empty_piece():
    br = BestRun([2, -5, -3, 4])
    assert br.best(1, 2) == -5, (
        "A single negative element: the piece must be non-empty, so the answer is -5, not 0. A leaf v is (v, v, v, v).")
    assert br.best(1, 3) == -3


def test_crossing_and_order():
    br = BestRun([-1, 3, -1, 3, -1])
    assert br.best(0, 5) == 5, "The best piece 3 - 1 + 3 crosses the middle: merge x.suffix + y.prefix."
    br2 = BestRun([5, -10, 1, 1, 1])
    assert br2.best(0, 5) == 5 and br2.best(1, 5) == 3, (
        "If left and right parts are merged in the wrong order, prefixes and suffixes get mixed up.")


def test_random_ops_against_kadane():
    rng = random.Random(1608)
    n = 50
    a = [rng.randint(-20, 20) for _ in range(n)]
    br = BestRun(a)
    for step in range(2000):
        if rng.random() < 0.4:
            i, v = rng.randrange(n), rng.randint(-20, 20)
            a[i] = v
            br.update(i, v)
        else:
            l = rng.randrange(n)
            r = rng.randint(l + 1, n)
            assert br.best(l, r) == kadane(a[l:r]), f"step {step}: best({l}, {r}) should be {kadane(a[l:r])}."


BIG_CODE = (
    "import random\n"
    "from solution import BestRun\n"
    "rng = random.Random(168)\n"
    "n = 10**5\n"
    "br = BestRun([rng.randint(-10**9, 10**9) for _ in range(n)])\n"
    "x = 0\n"
    "for _ in range(10**5):\n"
    "    if rng.random() < 0.5:\n"
    "        br.update(rng.randrange(n), rng.randint(-10**9, 10**9))\n"
    "    else:\n"
    "        x ^= br.best(rng.randint(0, n // 10), rng.randint(9 * n // 10, n))\n"
    "print(x)\n"
)
BIG_WANT = ['80855818048']


def test_large_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG_CODE], cwd=HERE, capture_output=True, text=True,
                           timeout=60, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, "too slow: each query must be O(log n) merges. Kadane over the range is O(r - l)."
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == BIG_WANT, f"Large input: expected {BIG_WANT}, got {r.stdout.split()}."
