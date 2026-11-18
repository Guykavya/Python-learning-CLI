import pathlib
import random
import subprocess
import sys

from solution import coin_change

HERE = pathlib.Path(__file__).parent


def brute(coins, amount):
    """Try every last coin (plain recursion, small amounts only). None means impossible."""
    if amount == 0:
        return 0
    best = None
    for c in coins:
        if c <= amount:
            rest = brute(coins, amount - c)
            if rest is not None and (best is None or rest + 1 < best):
                best = rest + 1
    return best


def run_big(code, limit):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=limit, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_chapter_examples():
    assert coin_change([1, 2, 5], 11) == 3, "Expected 3 (5 + 5 + 1)."
    got = coin_change([1, 3, 4], 6)
    assert got != 3, (
        "coin_change([1, 3, 4], 6) gave 3: that is greedy (4 + 1 + 1). 3 + 3 uses 2 coins. "
        "Try every coin as the last one and keep the minimum.")
    assert got == 2, f"Expected 2 (3 + 3), got {got}."


def test_impossible():
    got = coin_change([2], 3)
    assert got == -1, (
        f"coin_change([2], 3) should be -1 (odd amount, only 2s), got {got!r}. Convert infinity to -1 "
        "only at the end.")
    assert coin_change([5, 10], 3) == -1, "Every coin is bigger than 3: -1."


def test_amount_zero():
    assert coin_change([7], 0) == 0, "Amount 0 needs no coins: f(0) = 0, not -1."
    assert coin_change([1, 2], 0) == 0, "Amount 0 needs no coins."


def test_return_type():
    got = coin_change([2], 3)
    assert isinstance(got, int), f"Return an int (-1), not {type(got).__name__}: convert inf to -1."
    got = coin_change([1, 2, 5], 11)
    assert isinstance(got, int), f"Return an int, not {type(got).__name__}."


def test_random_against_recursion():
    rng = random.Random(1717)
    for _ in range(300):
        coins = rng.sample(range(1, 13), rng.randint(1, 4))
        amount = rng.randint(0, 22)
        want = brute(coins, amount)
        want = -1 if want is None else want
        got = coin_change(list(coins), amount)
        assert got == want, (
            f"coins={coins}, amount={amount}: expected {want} (all coin sequences tried), got {got}. "
            "f(a) = 1 + min(f(a - c)) over coins c <= a; f(0) = 0; unreachable = infinity until the end.")


def test_not_exponential():
    code = "from solution import coin_change\nprint(coin_change([1, 2, 5], 100))\n"
    r = run_big(code, 5)
    assert r is not None, (
        "Time limit (5 s) for amount 100: exponential: add a memo. Trying every coin sequence for 100 "
        "is billions of sequences; a table computes each amount once.")
    assert r.returncode == 0, "Your code crashed on amount 100:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["20"], f"coin_change([1, 2, 5], 100) should be 20, got {r.stdout.split()}."


def test_large_amounts():
    code = (
        "from solution import coin_change\n"
        "print(coin_change([1, 5, 10, 25], 9999), coin_change([2], 9999), coin_change([3, 7, 13, 101], 10000))\n"
        "print(coin_change([186, 419, 83, 408], 6249), coin_change([9973, 9967], 10000))\n"
        "print(coin_change(list(range(97, 130, 4)), 9999))\n"
    )
    r = run_big(code, 15)
    assert r is not None, "Time limit (15 s) for amounts up to 10**4: fill a table f[0..amount] once."
    if "RecursionError" in r.stderr:
        assert False, (
            "RecursionError for amount 10**4: a recursion with a 1-coin is 10,000 calls deep, even with a memo. "
            "Fill a table from a = 1 up to amount.")
    assert r.returncode == 0, "Your code crashed on a large amount:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["405", "-1", "108", "20", "-1", "79"], (
        f"Large amounts: expected 405 -1 108 / 20 -1 / 79, got {r.stdout.split()}.")
