import math
import random
from itertools import permutations

from solution import fractional_knapsack


def fill_in_order(order, capacity):
    total, room = 0.0, capacity
    for value, weight in order:
        part = min(weight, room)
        total += value * part / weight
        room -= part
    return total


def brute(items, capacity):
    """Try every order of filling the bag (small n only). The best order is the best bag."""
    if not items:
        return 0.0
    return max(fill_in_order(p, capacity) for p in permutations(items))


def close(a, b):
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)


def test_chapter_examples():
    got = fractional_knapsack([(60, 10), (100, 20), (120, 30)], 50)
    assert close(got, 240.0), (
        f"Got {got}, expected 240.0: all of items 0 and 1, then 20/30 of item 2. Sort by value/weight, highest first, "
        "and take a FRACTION of the last item that does not fit.")
    got = fractional_knapsack([(30, 5), (20, 10)], 8)
    assert close(got, 36.0), f"Got {got}, expected 36.0: all of (30,5), then 3/10 of (20,10), worth 6."
    got = fractional_knapsack([(30, 5), (20, 10)], 100)
    assert close(got, 50.0), f"Got {got}, expected 50.0: everything fits."


def test_wrong_keys_are_caught():
    got = fractional_knapsack([(10, 1), (50, 50), (1, 1)], 50)
    assert close(got, 59.0), (
        f"Got {got}, expected 59.0. Sorting by VALUE takes (50,50) first and fills the bag with 50. Sort by "
        "value / weight: (10,1) first, then 49 kg worth 1 each.")
    got = fractional_knapsack([(1, 1), (100, 4)], 4)
    assert close(got, 100.0), (
        f"Got {got}, expected 100.0. Sorting by lightest first takes the poor (1,1). Density 25 beats density 1.")


def test_returns_float_and_edge_cases():
    got = fractional_knapsack([(60, 10)], 0)
    assert close(got, 0.0), f"Capacity 0: nothing fits, value 0.0; got {got}."
    assert isinstance(fractional_knapsack([(60, 10)], 0), float), "Return a float, even when the answer is 0 (use 0.0)."
    assert close(fractional_knapsack([], 10), 0.0), "No items: value 0.0."
    got = fractional_knapsack([(0, 5), (0, 3), (12, 4)], 6)
    assert close(got, 12.0), f"Zero-value items add nothing; got {got}, expected 12.0."
    got = fractional_knapsack([(7, 3)], 2)
    assert close(got, 7 * 2 / 3), (
        f"Got {got}: 2 kg of a 3 kg pile worth 7 is worth 14/3. Use true division /, not //.")


def test_input_not_changed():
    data = [(60, 10), (100, 20), (120, 30)]
    fractional_knapsack(data, 50)
    assert data == [(60, 10), (100, 20), (120, 30)], "Do not sort the caller's list in place; use sorted(...)."


def test_random_against_every_order():
    rng = random.Random(12)
    for _ in range(300):
        n = rng.randint(0, 6)
        items = [(rng.randint(0, 30), rng.randint(1, 10)) for _ in range(n)]
        capacity = rng.randint(0, 35)
        expected = brute(items, capacity)
        got = fractional_knapsack(list(items), capacity)
        assert close(got, expected), (
            f"items={items}, capacity={capacity}: the best is {expected}, you returned {got}. Sort by "
            "value/weight descending; take min(weight, room) of each item; stop when the bag is full.")


def test_large_input_is_fast():
    items = [(i % 97 + 1, i % 13 + 1) for i in range(100_000)]
    total_value = sum(v for v, _ in items)
    total_weight = sum(w for _, w in items)
    got = fractional_knapsack(items, total_weight)
    assert close(got, float(total_value)), "When the bag holds everything, the answer is the sum of all values."
