import pathlib
import random
import subprocess
import sys

from solution import count_below

HERE = pathlib.Path(__file__).parent


def slow(a, queries):
    return [sum(1 for v in a[l:r] if v < x) for l, r, x in queries]


def test_example():
    a = [5, 1, 4, 2, 8, 3]
    got = count_below(a, [(0, 6, 4), (1, 4, 3), (2, 2, 9), (3, 6, 100), (0, 3, 1)])
    assert got == [3, 2, 0, 3, 0], f"Expected [3, 2, 0, 3, 0], got {got}."


def test_strictly_less_and_order():
    a = [3, 3, 3]
    got = count_below(a, [(0, 3, 3), (0, 3, 4), (0, 3, 2)])
    assert got == [0, 3, 0], (
        f"Expected [0, 3, 0], got {got}. Marks equal to x are NOT counted, and answers must be in the order of "
        "the questions, not sorted by x.")


def test_random_against_slow():
    rng = random.Random(1612)
    for _ in range(200):
        n = rng.randint(1, 30)
        a = [rng.randint(-5, 5) for _ in range(n)]
        qs = []
        for _ in range(rng.randint(1, 20)):
            l = rng.randint(0, n)
            qs.append((l, rng.randint(l, n), rng.randint(-6, 6)))
        assert count_below(a, qs) == slow(a, qs), f"a={a}, queries={qs}: expected {slow(a, qs)}."


BIG_CODE = (
    "import random\n"
    "from solution import count_below\n"
    "rng = random.Random(1612)\n"
    "n = 10**5\n"
    "a = [rng.randint(-10**9, 10**9) for _ in range(n)]\n"
    "qs = [(rng.randint(0, n // 10), rng.randint(9 * n // 10, n), rng.randint(-10**9, 10**9)) for _ in range(10**5)]\n"
    "ans = count_below(a, qs)\n"
    "print(sum(ans), ans[0], ans[-1])\n"
)
BIG_WANT = ['4493587571', '57448', '8692']


def test_large_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG_CODE], cwd=HERE, capture_output=True, text=True,
                           timeout=60, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "too slow: 10**5 questions over long ranges cannot each scan the range. Sort the questions by x and insert "
        "the marks in value order into a Fenwick tree over positions (or use a merge sort tree).")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == BIG_WANT, f"Large input: expected {BIG_WANT}, got {r.stdout.split()}."
