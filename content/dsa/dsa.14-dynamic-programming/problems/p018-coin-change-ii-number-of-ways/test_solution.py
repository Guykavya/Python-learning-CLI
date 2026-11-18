import pathlib
import random
import subprocess
import sys

from solution import coin_ways

HERE = pathlib.Path(__file__).parent


def brute(coins, amount, i=0):
    """Decide how many of coin i to take, then move to coin i + 1 (small inputs only)."""
    if amount == 0:
        return 1
    if i == len(coins):
        return 0
    total = 0
    k = 0
    while k * coins[i] <= amount:
        total += brute(coins, amount - k * coins[i], i + 1)
        k += 1
    return total


def sequences(coins, amount):
    """Order DOES matter here (amounts outside): used only to explain a wrong answer."""
    f = [0] * (amount + 1)
    f[0] = 1
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                f[a] += f[a - c]
    return f[amount]


def run_big(code, limit):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=limit, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_loop_order():
    got = coin_ways([1, 2, 5], 5)
    assert got != 9, (
        "coin_ways([1, 2, 5], 5) gave 9: that counts SEQUENCES (1+2+2 and 2+1+2 counted twice). "
        "Put the loop over coins OUTSIDE and the loop over amounts inside (chapter section 7).")
    assert got == 4, f"Expected 4 (5, 2+2+1, 2+1+1+1, 1+1+1+1+1), got {got}."
    assert coin_ways([1, 2, 3], 4) == 4, "Expected 4, as in chapter section 7."
    assert coin_ways([2, 5, 3, 6], 10) == 5, "Expected 5 (Try it 6 of chapter section 7)."


def test_edges():
    assert coin_ways([2], 3) == 0, "Only 2s cannot make 3: 0."
    assert coin_ways([7], 0) == 1, "Amount 0: one combination, the empty one. f[0] = 1."
    assert coin_ways([5, 10], 3) == 0, "Every coin is bigger than 3: 0."
    assert coin_ways([3], 9) == 1, "Only 3 + 3 + 3."


def test_coin_order_does_not_matter():
    assert coin_ways([5, 1, 2], 5) == coin_ways([1, 2, 5], 5) == 4, (
        "The order of the coins list must not change the count.")


def test_random_against_brute_force():
    rng = random.Random(1818)
    for _ in range(300):
        coins = rng.sample(range(1, 10), rng.randint(1, 4))
        amount = rng.randint(0, 25)
        want = brute(coins, amount)
        got = coin_ways(list(coins), amount)
        if got != want and got == sequences(coins, amount):
            assert False, (
                f"coins={coins}, amount={amount}: you returned {got}, the number of SEQUENCES; combinations "
                f"are {want}. Swap the loops: coins outside, amounts inside.")
        assert got == want, (
            f"coins={coins}, amount={amount}: expected {want} combinations, got {got}. "
            "f[0] = 1; for each coin c, for a from c up: f[a] += f[a - c].")


def test_large_amounts():
    code = (
        "from solution import coin_ways\n"
        "print(coin_ways([1, 2, 5, 10, 20, 50, 100, 200], 5000))\n"
        "print(coin_ways([3, 7, 13, 101], 10000), coin_ways([5, 37, 2, 11], 10000), coin_ways([2], 9999))\n"
    )
    r = run_big(code, 15)
    assert r is not None, (
        "Time limit (15 s) for amounts up to 10**4: exponential: add a memo. The table needs only "
        "len(coins) passes over the amounts.")
    if "RecursionError" in r.stderr:
        assert False, "RecursionError for a large amount: fill a table f[0..amount] instead of recursing."
    assert r.returncode == 0, "Your code crashed on a large amount:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["10082315214426", "6157528", "41288653", "0"], (
        f"Large amounts: expected 10082315214426 / 6157528 41288653 0, got {r.stdout.split()}.")
