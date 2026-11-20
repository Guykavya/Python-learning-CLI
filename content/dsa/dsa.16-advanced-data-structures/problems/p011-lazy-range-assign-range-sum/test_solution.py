import pathlib
import random
import subprocess
import sys

from solution import AssignSum

HERE = pathlib.Path(__file__).parent


def test_example():
    s = AssignSum([5, 3, 8, 6, 2, 7, 4, 1])
    s.assign(2, 6, 9)
    assert (s.query(0, 8), s.query(2, 6), s.query(1, 3)) == (49, 36, 12)
    s.assign(0, 8, 0)
    assert s.query(0, 8) == 0
    s.assign(3, 5, 4)
    assert (s.query(0, 8), s.query(4, 5)) == (8, 4)


def test_assign_zero_is_real():
    s = AssignSum([1, 2, 3, 4])
    s.assign(0, 4, 0)
    s.assign(1, 2, 7)          # partial update: must push the root's tag 0 first
    got = [s.query(i, i + 1) for i in range(4)]
    assert got == [0, 7, 0, 0], (
        f"Expected [0, 7, 0, 0], got {got}. A pending assignment of 0 must be pushed: use None for 'no tag' and "
        "test 'is not None', never 'if tag:'.")


def test_newer_assignment_wins():
    s = AssignSum([0] * 8)
    s.assign(0, 8, 5)          # tag on the root
    s.assign(0, 4, 2)          # newer, on the left half
    s.assign(2, 3, 9)          # newest, one element
    got = [s.query(i, i + 1) for i in range(8)]
    assert got == [2, 2, 9, 2, 5, 5, 5, 5], f"Expected [2, 2, 9, 2, 5, 5, 5, 5], got {got}."


def test_random_ops_against_list():
    rng = random.Random(1611)
    for trial in range(3):
        n = 50
        a = [rng.randint(-20, 20) for _ in range(n)]
        s = AssignSum(a)
        for step in range(2000):
            l = rng.randint(0, n)
            r = rng.randint(l, n)
            if rng.random() < 0.5:
                v = rng.choice([0, 0, rng.randint(-9, 9)])
                s.assign(l, r, v)
                a[l:r] = [v] * (r - l)
            else:
                assert s.query(l, r) == sum(a[l:r]), f"trial {trial} step {step}: query({l}, {r}) wrong."


BIG_CODE = (
    "import random\n"
    "from solution import AssignSum\n"
    "rng = random.Random(1611)\n"
    "n = 10**5\n"
    "s = AssignSum([rng.randint(-10**9, 10**9) for _ in range(n)])\n"
    "x = 0\n"
    "for _ in range(10**5):\n"
    "    l, r = rng.randint(0, n // 10), rng.randint(9 * n // 10, n)\n"
    "    if rng.random() < 0.5:\n"
    "        s.assign(rng.randint(0, n - 1), r, rng.choice([0, rng.randint(-10**9, 10**9)]))\n"
    "    else:\n"
    "        x ^= s.query(l, r)\n"
    "print(x)\n"
)
BIG_WANT = ['-40221794579918']


def test_large_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG_CODE], cwd=HERE, capture_output=True, text=True,
                           timeout=60, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, "too slow: each assign and query must be O(log n). Use a lazy tag on covered nodes."
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == BIG_WANT, f"Large input: expected {BIG_WANT}, got {r.stdout.split()}."
