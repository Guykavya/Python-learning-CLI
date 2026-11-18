import pathlib
import random
import subprocess
import sys
from collections import deque

from solution import coins_used

HERE = pathlib.Path(__file__).parent


def fewest(coins, amount):
    """Breadth-first search over amounts (dsa.10): fewest coins, or None. A different method from the DP."""
    dist = {0: 0}
    queue = deque([0])
    while queue:
        a = queue.popleft()
        if a == amount:
            return dist[a]
        for c in coins:
            b = a + c
            if b <= amount and b not in dist:
                dist[b] = dist[a] + 1
                queue.append(b)
    return None


def check(coins, amount, got):
    """Return an error message, or None when the list is a valid optimal answer."""
    want = fewest(coins, amount)
    if want is None:
        return None if got is None else f"{amount} cannot be made from {coins}: return None, not {got!r}"
    if got is None:
        return f"{amount} CAN be made from {coins} with {want} coins, but you returned None"
    if not isinstance(got, list):
        return f"return a list of coins, not {type(got).__name__}"
    bad = [c for c in got if c not in coins]
    if bad:
        return f"{bad} are not coin values from {coins}"
    if sum(got) != amount:
        return f"your coins {got} add up to {sum(got)}, not {amount}"
    if len(got) != want:
        return (f"your list has {len(got)} coins but {want} is possible. Store last[a] only when f[a] improves "
                "(inside the if), and walk back from amount.")
    return None


def run_big(code, timeout=10):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=timeout, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_examples():
    for coins, amount in [([1, 2, 5], 11), ([1, 3, 4], 6), ([2], 3), ([7], 0)]:
        err = check(coins, amount, coins_used(coins, amount))
        assert err is None, f"coins_used({coins}, {amount}): " + err


def test_greedy_is_not_enough():
    err = check([1, 3, 4], 6, coins_used([1, 3, 4], 6))
    assert err is None, "Greedy (4, 1, 1) uses 3 coins; 3 + 3 uses 2. " + err
    err = check([1, 5, 6, 9], 11, coins_used([1, 5, 6, 9], 11))
    assert err is None, "Greedy (9, 1, 1) uses 3 coins; 5 + 6 uses 2. " + err


def test_impossible_and_zero():
    assert coins_used([5, 10], 3) is None, "3 cannot be made from 5 and 10: return None."
    assert coins_used([4, 6], 7) is None, "Even coins never make 7: return None, not a partial list."
    assert coins_used([3], 0) == [], "Amount 0 needs no coins: return [] (not None)."


def test_random_validated():
    rng = random.Random(33)
    for _ in range(400):
        coins = rng.sample(range(1, 15), rng.randint(1, 4))
        amount = rng.randint(0, 22)
        got = coins_used(list(coins), amount)
        err = check(coins, amount, got)
        assert err is None, f"coins_used({coins}, {amount}) returned {got!r}: " + err


def test_medium_amount_needs_memo():
    code = "from solution import coins_used\nprint(repr(coins_used([1, 2, 5], 300)))\n"
    r = run_big(code)
    assert r is not None, (
        "Time limit (10 s) for amount 300. exponential: add a memo. Trying every coin at every step makes "
        "the same amounts again and again; each amount 0..300 is one state.")
    assert r.returncode == 0, "Your code crashed on amount 300:\n" + r.stderr[-800:]
    line = r.stdout.strip()
    got = None if line == "None" else [int(x) for x in line.strip("[]").split(",") if x.strip()]
    err = check([1, 2, 5], 300, got)
    assert err is None, "coins_used([1, 2, 5], 300): " + err


def test_big_amounts():
    code = ("from solution import coins_used\n"
            "a = coins_used([7, 13, 29, 101, 997], 9999)\n"
            "b = coins_used([1, 5, 10, 25], 10000)\n"
            "c = coins_used([6, 10, 15], 10**4 - 1)\n"
            "print(repr(a)); print(repr(b)); print(repr(c))\n")
    r = run_big(code)
    assert r is not None, (
        "Time limit (10 s) for amounts near 10,000. exponential: add a memo. A table f[0..amount] with "
        "len(coins) steps per cell is about 50,000 steps.")
    assert r.returncode == 0, (
        "Your code crashed on an amount near 10,000. A top-down recursion goes about 10,000 calls deep "
        "(RecursionError): fill the table bottom-up.\n" + r.stderr[-600:])
    lines = r.stdout.strip().splitlines()
    cases = [([7, 13, 29, 101, 997], 9999), ([1, 5, 10, 25], 10000), ([6, 10, 15], 10**4 - 1)]
    for (coins, amount), line in zip(cases, lines):
        got = None if line == "None" else [int(x) for x in line.strip("[]").split(",") if x.strip()]
        err = check(coins, amount, got)
        assert err is None, f"coins_used({coins}, {amount}): " + err
