import pathlib
import random
import subprocess
import sys

from solution import rod_cut

HERE = pathlib.Path(__file__).parent


def brute(price, n):
    """Every way to choose the first piece, recursively, no memo (n <= 14 only)."""
    if n == 0:
        return 0
    return max(price[k - 1] + brute(price, n - k) for k in range(1, n + 1))


def test_chapter_prices():
    prices = [1, 5, 8, 9, 10, 17, 17, 20]
    got = [rod_cut(prices, n) for n in range(9)]
    want = [0, 1, 5, 8, 10, 13, 17, 18, 22]
    assert got == want, (
        f"For lengths 0..8 expected {want}, got {got}. f[m] = max(price[k - 1] + f[m - k]) for k in 1..m; "
        "k = m is 'sell the rod whole'.")


def test_whole_rod_can_be_best():
    assert rod_cut([1, 1, 10], 3) == 10, (
        "price = [1, 1, 10]: selling the rod of 3 whole (10) is best. Let the first piece be the whole rod (k = m).")


def test_many_pieces():
    got = rod_cut([3, 5, 6], 3)
    assert got == 9, (
        f"price = [3, 5, 6]: three pieces of length 1 give 9; expected 9, got {got}. One cut is not always "
        "enough: f[m - k] must be the best for the REST, cut again if that helps.")
    got = rod_cut([1, 5, 8, 9], 4)
    assert got == 10, (
        f"Expected 10 (2 + 2), got {got}. Greedy by price per length takes 3 + 1 = 9.")


def test_zero_length():
    assert rod_cut([4, 7], 0) == 0, "A rod of length 0 sells for 0."
    assert rod_cut([], 0) == 0, "No prices and no rod: 0."


def test_shorter_rod_than_price_list():
    assert rod_cut([2, 5, 7, 100], 3) == 7, (
        "n = 3 with four prices: only pieces up to length 3 exist. Do not use price[3] (length 4).")


def test_random_against_brute_force():
    rng = random.Random(3939)
    for _ in range(200):
        size = rng.randint(1, 12)
        price = [rng.randint(0, 30) for _ in range(size)]
        n = rng.randint(0, size)
        want = brute(price, n)
        got = rod_cut(list(price), n)
        assert got == want, f"price={price}, n={n}: expected {want}, got {got}."


def test_long_rod():
    code = (
        "import random\n"
        "from solution import rod_cut\n"
        "rng = random.Random(39)\n"
        "price = [rng.randint(0, 10**6) for _ in range(3000)]\n"
        "print(rod_cut(price, 3000))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=20, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (20 s) for n = 3000: without a table there are 2**2999 cuttings. Fill f[0..n].")
    if "RecursionError" in r.stderr:
        assert False, "RecursionError for n = 3000: fill a list f[0..n] from short rods to long ones."
    assert r.returncode == 0, "Your code crashed on the long rod:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["660132000"], f"n = 3000: expected 660132000, got {r.stdout.split()}."
