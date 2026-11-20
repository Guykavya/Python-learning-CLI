import pathlib
import random
import subprocess
import sys

from solution import count_inversions

HERE = pathlib.Path(__file__).parent


def slow(a):
    return sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] > a[j])


def test_examples():
    assert count_inversions([40, 10, 30, 10, 20]) == 6
    assert (count_inversions([1, 2, 3, 4]), count_inversions([4, 3, 2, 1])) == (0, 6)
    assert count_inversions([]) == 0 and count_inversions([7]) == 0


def test_equal_values_are_not_inversions():
    got = count_inversions([2, 2, 2])
    assert got == 0, f"Equal values are not inversions: expected 0, got {got}. Count earlier elements > x."
    assert count_inversions([3, 1, 3, 1]) == 3


def test_random_against_pairs():
    rng = random.Random(1618)
    for _ in range(500):
        a = [rng.randint(-5, 5) for _ in range(rng.randint(0, 25))]
        assert count_inversions(list(a)) == slow(a), f"count_inversions({a}) should be {slow(a)}."


BIG_CODE = (
    "import random\n"
    "from solution import count_inversions\n"
    "rng = random.Random(1618)\n"
    "n = 2 * 10**5\n"
    "print(count_inversions([rng.randint(-10**9, 10**9) for _ in range(n)]),\n"
    "      count_inversions(list(range(n, 0, -1))), count_inversions([rng.randint(0, 9) for _ in range(n)]))\n"
)
BIG_WANT = ['10012929914', '19999900000', '8996349389']


def test_large_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG_CODE], cwd=HERE, capture_output=True, text=True,
                           timeout=40, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, ("too slow: checking all pairs of 2 * 10**5 numbers is 2 * 10**10 comparisons. Use a Fenwick tree over ranks.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == BIG_WANT, f"Large input: expected {BIG_WANT}, got {r.stdout.split()}."
