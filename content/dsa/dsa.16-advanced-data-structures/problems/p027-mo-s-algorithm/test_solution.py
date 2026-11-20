import pathlib
import random
import subprocess
import sys

from solution import distinct_counts

HERE = pathlib.Path(__file__).parent


def test_example():
    got = distinct_counts([4, 7, 4, 4, 9, 7], [(0, 6), (0, 3), (2, 5), (1, 2), (3, 6), (2, 2)])
    assert got == [3, 2, 2, 1, 3, 0], f"Expected [3, 2, 2, 1, 3, 0], got {got}. Answers go in the question order."


def test_window_never_negative():
    a = [1, 2, 3, 4, 5, 6]
    qs = [(4, 6), (0, 2), (5, 6), (0, 1), (2, 4)]
    assert distinct_counts(a, qs) == [2, 2, 1, 1, 2], "Grow the window before shrinking it."


def test_random_against_sets():
    rng = random.Random(1627)
    for _ in range(150):
        n = rng.randint(1, 40)
        a = [rng.randint(0, 6) for _ in range(n)]
        qs = []
        for _ in range(rng.randint(1, 25)):
            l = rng.randint(0, n)
            qs.append((l, rng.randint(l, n)))
        want = [len(set(a[l:r])) for l, r in qs]
        assert distinct_counts(a, qs) == want, f"a={a}, queries={qs}: expected {want}."


BIG_CODE = (
    "import random\n"
    "from solution import distinct_counts\n"
    "rng = random.Random(1627)\n"
    "n = 5 * 10**4\n"
    "a = [rng.randint(0, 5000) for _ in range(n)]\n"
    "qs = []\n"
    "for _ in range(5 * 10**4):\n"
    "    if rng.random() < 0.5:\n"
    "        l = rng.randint(0, n // 10)\n"
    "        qs.append((l, rng.randint(9 * n // 10, n)))\n"
    "    else:\n"
    "        l = rng.randrange(n)\n"
    "        qs.append((l, min(n, l + rng.randint(0, 3000))))\n"
    "ans = distinct_counts(a, qs)\n"
    "print(sum(ans), min(ans), ans[0])\n"
)
BIG_WANT = ['155416435', '0', '26']


def test_large_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG_CODE], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, ("too slow: len(set(a[l:r])) per question is O(n). Sort the questions (Mo's order) and slide one window.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == BIG_WANT, f"Large input: expected {BIG_WANT}, got {r.stdout.split()}."
