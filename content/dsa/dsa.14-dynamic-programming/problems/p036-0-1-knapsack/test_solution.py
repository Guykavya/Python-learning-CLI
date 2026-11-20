import itertools
import pathlib
import random
import subprocess
import sys

from solution import knapsack, knapsack_table

HERE = pathlib.Path(__file__).parent


def brute(wt, val, W):
    """Try every subset of items (small inputs only)."""
    best = 0
    n = len(wt)
    for r in range(n + 1):
        for combo in itertools.combinations(range(n), r):
            if sum(wt[i] for i in combo) <= W:
                best = max(best, sum(val[i] for i in combo))
    return best


def unbounded(wt, val, W):
    """Items reused (upward loop): used only to explain a wrong answer."""
    g = [0] * (W + 1)
    for i in range(len(wt)):
        for w in range(wt[i], W + 1):
            g[w] = max(g[w], g[w - wt[i]] + val[i])
    return g[W]


def test_table_matches_chapter():
    f = knapsack_table([1, 3, 4, 5], [1, 4, 5, 7], 7)
    want = [[0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 4, 5, 5, 5, 5],
            [0, 1, 1, 4, 5, 6, 6, 9],
            [0, 1, 1, 4, 5, 7, 8, 9]]
    assert len(f) == 5, (
        f"The table needs len(wt) + 1 = 5 rows (row 0 = no items), got {len(f)}.")
    for i in range(5):
        assert f[i] == want[i], (
            f"Row {i} should be {want[i]}, got {f[i]}. f[i][w] = max(f[i-1][w], f[i-1][w - wt[i-1]] + val[i-1]); "
            "row i is about item i - 1.")


def test_table_rows_are_separate_lists():
    f = knapsack_table([2, 3], [3, 4], 5)
    assert f == [[0, 0, 0, 0, 0, 0], [0, 0, 3, 3, 3, 3], [0, 0, 3, 4, 4, 7]], (
        f"Expected rows [0,0,0,0,0,0] / [0,0,3,3,3,3] / [0,0,3,4,4,7], got {f}. If every row is the same, "
        "you built the table with [[0] * (W + 1)] * (n + 1): all rows are one list. Use a comprehension.")


def test_one_list_examples():
    assert knapsack([1, 3, 4, 5], [1, 4, 5, 7], 7) == 9, "Expected 9: items of weight 3 and 4."
    got = knapsack([2], [10], 7)
    assert got != 30, (
        "knapsack([2], [10], 7) gave 30: the item was taken three times. The w loop must go DOWNWARDS, "
        "so that g[w - wt] still holds the value from before this item.")
    assert got == 10, f"One item of value 10: expected 10, got {got}."
    assert knapsack([8, 9], [5, 6], 7) == 0, "Nothing fits in a bag of 7: 0."
    assert knapsack([], [], 10) == 0, "No items: 0."
    assert knapsack([3], [5], 0) == 0, "Capacity 0: 0."


def test_greedy_is_not_enough():
    assert knapsack([1, 3, 4, 5], [1, 4, 5, 7], 7) == 9, (
        "Best value per weight takes weights 5 and 1 (value 8). The DP finds 9 (weights 3 and 4).")


def test_random_against_brute_force():
    rng = random.Random(3636)
    for _ in range(300):
        n = rng.randint(0, 8)
        wt = [rng.randint(1, 10) for _ in range(n)]
        val = [rng.randint(0, 20) for _ in range(n)]
        W = rng.randint(0, 25)
        want = brute(wt, val, W)
        got = knapsack(list(wt), list(val), W)
        if got != want and got == unbounded(wt, val, W):
            assert False, (
                f"wt={wt}, val={val}, W={W}: you returned {got}, the UNBOUNDED answer (items reused); each item "
                f"may be taken once, best {want}. Loop w from W DOWN to wt[i].")
        assert got == want, f"wt={wt}, val={val}, W={W}: expected {want} (every subset tried), got {got}."
        table = knapsack_table(list(wt), list(val), W)
        assert table[n][W] == want, (
            f"wt={wt}, val={val}, W={W}: knapsack_table(...)[{n}][{W}] should be {want}, got {table[n][W]}.")


def test_large_input():
    code = (
        "import random\n"
        "from solution import knapsack, knapsack_table\n"
        "rng = random.Random(36)\n"
        "wt = [rng.randint(1, 1000) for _ in range(200)]\n"
        "val = [rng.randint(0, 10**6) for _ in range(200)]\n"
        "print(knapsack(wt, val, 10**4), knapsack_table(wt[:100], val[:100], 5000)[-1][-1])\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=20, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (20 s) for 200 items and W = 10**4: trying every subset is 2**200. Fill the table.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["37529083", "16984875"], (
        f"Large input: expected 37529083 and 16984875, got {r.stdout.split()}.")
