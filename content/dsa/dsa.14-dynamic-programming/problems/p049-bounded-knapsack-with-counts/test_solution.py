import pathlib
import random
import subprocess
import sys

from solution import bounded_knapsack

HERE = pathlib.Path(__file__).parent


def brute(items, W):
    """Try every number of copies of every kind (only for small inputs)."""
    best = 0

    def go(k, room, value):
        nonlocal best
        if k == len(items):
            best = max(best, value)
            return
        weight, val, count = items[k]
        c = 0
        while c <= count and c * weight <= room:
            go(k + 1, room - c * weight, value + c * val)
            c += 1

    go(0, W, 0)
    return best


def split_answer(items, W):
    g = [0] * (W + 1)
    for weight, value, count in items:
        b = 1
        while count > 0:
            t = min(b, count)
            for w in range(W, t * weight - 1, -1):
                g[w] = max(g[w], g[w - t * weight] + t * value)
            count -= t
            b *= 2
    return g[W]


def test_examples():
    assert bounded_knapsack([(2, 3, 2), (3, 4, 1)], 7) == 10, (
        "Expected 10: two copies of (2, 3) and one of (3, 4) weigh 7.")
    assert bounded_knapsack([(1, 5, 3)], 10) == 15, (
        "Only 3 copies exist: 15. If you got 50, the count is ignored (an upward loop is the unbounded knapsack).")
    assert bounded_knapsack([(4, 10, 5)], 3) == 0, "Nothing fits in a bag of 3."


def test_counts_zero_and_empty():
    assert bounded_knapsack([(1, 2, 0), (2, 3, 1)], 5) == 3, "A kind with count 0 cannot be used."
    assert bounded_knapsack([], 10) == 0, "No items: 0."
    assert bounded_knapsack([(1, 1, 5)], 0) == 0, "A bag of capacity 0 holds nothing."


def test_last_bundle_is_the_rest():
    assert bounded_knapsack([(1, 10, 5)], 7) == 50, (
        "5 copies of (1, 10): 50, even though the bag holds 7. If you got 70, your bundles were 1, 2, 4 "
        "(7 copies). The last bundle must be the rest: 1, 2, 2.")
    assert bounded_knapsack([(1, 1, 6)], 100) == 6, "Bundles of 6 copies: 1, 2, 3. They make at most 6."


def test_count_limit_with_competition():
    assert bounded_knapsack([(3, 10, 2), (2, 6, 5)], 10) == 32, (
        "Best: two of (3, 10) and two of (2, 6): weight 10, value 32.")


def test_random_against_brute_force():
    rng = random.Random(49)
    for _ in range(300):
        items = [(rng.randint(1, 5), rng.randint(0, 9), rng.randint(0, 6)) for _ in range(rng.randint(0, 4))]
        W = rng.randint(0, 15)
        want = brute(items, W)
        got = bounded_knapsack(list(items), W)
        assert got == want, (
            f"items={items}, W={W}: expected {want} (tried every number of copies), got {got}. "
            "Each bundle is a 0/1 item (downward loop); the last bundle is the rest of the count.")


def test_big_input_is_fast():
    rng = random.Random(4949)
    items = [(rng.randint(1, 10), rng.randint(1, 1000), rng.randint(200, 1000)) for _ in range(100)]
    want = split_answer(items, 5000)
    code = (
        "from solution import bounded_knapsack\n"
        f"print(bounded_knapsack({items!r}, 5000))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on 100 kinds with up to 1000 copies and W = 5000. One 0/1 item per copy is about "
        "3 * 10**8 steps; split each count into bundles 1, 2, 4, ... and the rest. (A plain recursion "
        "without a memo is exponential: add a memo or use the table.)")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == [str(want)], f"Large input: expected {want}, got {r.stdout.split()}."
