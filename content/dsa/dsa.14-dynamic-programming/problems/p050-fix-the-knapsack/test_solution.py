import pathlib
import random
import subprocess
import sys

from solution import knapsack

HERE = pathlib.Path(__file__).parent


def brute(weights, values, capacity):
    """Try every subset of parcels (only for a few parcels)."""
    n = len(weights)
    best = 0
    for mask in range(1 << n):
        w = v = 0
        for i in range(n):
            if mask >> i & 1:
                w += weights[i]
                v += values[i]
        if w <= capacity and v > best:
            best = v
    return best


def table(weights, values, capacity):
    f = [[0] * (capacity + 1) for _ in range(len(weights) + 1)]
    for i in range(1, len(weights) + 1):
        wt, val = weights[i - 1], values[i - 1]
        for c in range(capacity + 1):
            f[i][c] = f[i - 1][c]
            if wt <= c:
                f[i][c] = max(f[i][c], f[i - 1][c - wt] + val)
    return f[len(weights)][capacity]


def test_customer_report():
    assert knapsack([2], [10], 7) == 10, (
        "One parcel of weight 2 and value 10: the answer is 10. 30 means the parcel was taken three times: "
        "the capacity loop goes upwards and reads cells already updated for this parcel. Loop from high to low.")


def test_friendly_example_still_works():
    assert knapsack([1, 3, 4, 5], [1, 4, 5, 7], 7) == 9, "Chapter example: parcels of weight 3 and 4, value 9."


def test_exact_fit_is_kept():
    assert knapsack([3], [5], 3) == 5, (
        "A parcel that exactly fills the drone must be taken. If you got 0, your downward loop stops at "
        "weights[i] + 1: use range(capacity, weights[i] - 1, -1).")
    assert knapsack([4, 2], [7, 3], 6) == 10, "Both parcels fit exactly: 7 + 3 = 10."


def test_empty_and_zero_capacity():
    assert knapsack([], [], 10) == 0, "No parcels: 0."
    assert knapsack([1, 2], [5, 6], 0) == 0, "Capacity 0 holds nothing."
    assert knapsack([5], [100], 4) == 0, "The only parcel is too heavy: 0."


def test_does_not_change_the_input():
    w, v = [2, 3, 4], [3, 4, 5]
    knapsack(w, v, 5)
    assert w == [2, 3, 4] and v == [3, 4, 5], "Do not change the lists you are given."


def test_random_against_brute_force():
    rng = random.Random(50)
    for _ in range(400):
        n = rng.randint(1, 8)
        weights = [rng.randint(1, 6) for _ in range(n)]
        values = [rng.randint(0, 10) for _ in range(n)]
        capacity = rng.randint(0, 18)
        want = brute(weights, values, capacity)
        got = knapsack(list(weights), list(values), capacity)
        assert got == want, (
            f"weights={weights}, values={values}, capacity={capacity}: expected {want} (tried every subset), "
            f"got {got}. A larger answer means a parcel was used twice: loop the capacity downwards.")


def test_big_input_is_fast():
    rng = random.Random(5050)
    weights = [rng.randint(1, 100) for _ in range(300)]
    values = [rng.randint(0, 1000) for _ in range(300)]
    want = table(weights, values, 3000)
    code = (
        "from solution import knapsack\n"
        f"print(knapsack({weights!r}, {values!r}, 3000))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on 300 parcels and capacity 3000. The one-array loop is about a million steps; "
        "trying every subset is exponential: add a memo or keep the table.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == [str(want)], f"Large input: expected {want}, got {r.stdout.split()}."
