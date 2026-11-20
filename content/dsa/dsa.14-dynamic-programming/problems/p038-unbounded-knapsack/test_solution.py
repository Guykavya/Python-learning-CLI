import functools
import pathlib
import random
import subprocess
import sys

from solution import unbounded_knapsack

HERE = pathlib.Path(__file__).parent


def brute(wt, val, W):
    """Choose how many copies of item i, then move to item i + 1 (small inputs only)."""
    @functools.cache
    def go(i, w):
        if i == len(wt):
            return 0
        best, k = 0, 0
        while k * wt[i] <= w:
            best = max(best, k * val[i] + go(i + 1, w - k * wt[i]))
            k += 1
        return best
    return go(0, W)


def zero_one(wt, val, W):
    """Each item once (downward loop): used only to explain a wrong answer."""
    g = [0] * (W + 1)
    for i in range(len(wt)):
        for w in range(W, wt[i] - 1, -1):
            g[w] = max(g[w], g[w - wt[i]] + val[i])
    return g[W]


def test_examples():
    assert unbounded_knapsack([2, 3], [10, 14], 7) == 34, "Expected 34: 2 + 2 + 3 (10 + 10 + 14)."
    assert unbounded_knapsack([4, 5], [7, 9], 12) == 21, (
        "Expected 21: three items of weight 4. Greedy by value per weight takes two 5s (18).")
    assert unbounded_knapsack([5], [1], 4) == 0, "Nothing fits in a bag of 4: 0."


def test_reuse():
    got = unbounded_knapsack([2], [10], 7)
    assert got != 10, (
        "unbounded_knapsack([2], [10], 7) gave 10: the item was used only once (the 0/1 loop). Loop the "
        "capacity UPWARDS so that g[w - wt] may already contain the same item.")
    assert got == 30, f"Three copies of weight 2 fit in 7: expected 30, got {got}."


def test_leftover_space_is_fine():
    got = unbounded_knapsack([3], [5], 7)
    assert got == 10, (
        f"Two items of weight 3 fill 6 of 7: expected 10, got {got}. If you got a very negative number or -1, "
        "you solved 'exactly W'. Here the bag may have space left: start every g[w] at 0.")
    assert unbounded_knapsack([], [], 9) == 0, "No items: 0."
    assert unbounded_knapsack([1], [3], 0) == 0, "Capacity 0: 0."


def test_random_against_brute_force():
    rng = random.Random(3838)
    for _ in range(300):
        n = rng.randint(0, 5)
        wt = [rng.randint(1, 9) for _ in range(n)]
        val = [rng.randint(0, 20) for _ in range(n)]
        W = rng.randint(0, 30)
        want = brute(tuple(wt), tuple(val), W)
        got = unbounded_knapsack(list(wt), list(val), W)
        if got != want and got == zero_one(wt, val, W):
            assert False, (
                f"wt={wt}, val={val}, W={W}: you returned {got}, the 0/1 answer (each item once); with reuse the "
                f"best is {want}. Loop w UPWARDS.")
        assert got == want, f"wt={wt}, val={val}, W={W}: expected {want}, got {got}."


def test_large_capacity():
    code = (
        "import random\n"
        "from solution import unbounded_knapsack\n"
        "rng = random.Random(38)\n"
        "wt = [rng.randint(1, 1000) for _ in range(50)]\n"
        "val = [rng.randint(0, 10**6) for _ in range(50)]\n"
        "print(unbounded_knapsack(wt, val, 10**5), unbounded_knapsack([1, 7], [2, 15], 10**5))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=20, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, "Time limit (20 s) for W = 10**5: one list of W + 1 values, one pass per item."
    if "RecursionError" in r.stderr:
        assert False, "RecursionError for W = 10**5: fill a list g[0..W] instead of recursing."
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["2658035341", "214285"], (
        "Large capacity: expected 2658035341, and 214285 (14,285 items of weight 7 plus five of weight 1); "
        f"got {r.stdout.split()}.")
