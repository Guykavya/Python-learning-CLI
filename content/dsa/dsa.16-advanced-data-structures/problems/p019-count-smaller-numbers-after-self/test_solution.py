import pathlib
import random
import subprocess
import sys

from solution import smaller_after

HERE = pathlib.Path(__file__).parent


def slow(nums):
    return [sum(1 for y in nums[i + 1:] if y < x) for i, x in enumerate(nums)]


def test_examples():
    assert smaller_after([5, 2, 6, 1]) == [2, 1, 1, 0]
    assert smaller_after([]) == [] and smaller_after([3]) == [0]


def test_equal_values_are_not_smaller():
    got = smaller_after([-1, -1])
    assert got == [0, 0], f"Equal values are not smaller: expected [0, 0], got {got}. Query prefix(rank), not rank + 1."
    assert smaller_after([2, 0, 1, 1, 0]) == [4, 0, 1, 1, 0]


def test_random_against_slow():
    rng = random.Random(1619)
    for _ in range(500):
        a = [rng.randint(-5, 5) for _ in range(rng.randint(0, 25))]
        assert smaller_after(list(a)) == slow(a), f"smaller_after({a}) should be {slow(a)}."


BIG_CODE = (
    "import random\n"
    "from solution import smaller_after\n"
    "rng = random.Random(1619)\n"
    "n = 10**5\n"
    "out = smaller_after([rng.randint(-10**9, 10**9) for _ in range(n)])\n"
    "print(sum(out), out[0], out[n // 2], max(out))\n"
)
BIG_WANT = ['2504684002', '5290', '17446', '99582']


def test_large_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG_CODE], cwd=HERE, capture_output=True, text=True,
                           timeout=40, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, ("too slow: comparing each number with all later ones is O(n**2). Scan from the right with a Fenwick tree over ranks.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == BIG_WANT, f"Large input: expected {BIG_WANT}, got {r.stdout.split()}."
