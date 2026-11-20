import itertools
import pathlib
import random
import subprocess
import sys

from solution import shortest_tour

HERE = pathlib.Path(__file__).parent


def brute(dist):
    """Try every order of places 1..n-1 (n <= 7 only)."""
    n = len(dist)
    best = float("inf")
    for order in itertools.permutations(range(1, n)):
        route = (0,) + order + (0,)
        best = min(best, sum(dist[a][b] for a, b in zip(route, route[1:])))
    return best if n > 1 else 0


def tour_cost(dist, order):
    route = list(order) + [order[0]]
    return sum(dist[a][b] for a, b in zip(route, route[1:]))


def check(dist, result, want):
    """Validate (length, order). Returns an error message or None."""
    n = len(dist)
    if not (isinstance(result, tuple) and len(result) == 2):
        return f"return a tuple (length, order); got {result!r}"
    length, order = result
    if length != want:
        return f"the shortest tour has length {want}, you returned {length}"
    if not isinstance(order, list) or sorted(order) != list(range(n)):
        return f"order must list every place 0..{n - 1} exactly once, got {order!r}"
    if order[0] != 0:
        return f"order must start at the depot 0, got {order!r}"
    cost = tour_cost(dist, order)
    if cost != length:
        return (f"driving {order} and back to 0 costs {cost}, not {length} (rebuild the order with the parent of "
                "each state, removing 'last' from the mask before each step back)")
    return None


def test_examples():
    d = [[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]]
    error = check(d, shortest_tour(d), 80)
    assert error is None, f"Chapter example: {error}."
    error = check([[0]], shortest_tour([[0]]), 0)
    assert error is None, f"One place: the tour is (0, [0]). {error}."


def test_one_way_roads():
    d = [[0, 1, 9], [9, 0, 1], [1, 9, 0]]
    error = check(d, shortest_tour(d), 3)
    assert error is None, (
        f"One-way roads: 0 -> 1 -> 2 -> 0 costs 1 + 1 + 1 = 3, the other direction 27. {error}. "
        "Use dist[last][nxt] in the direction you drive.")
    d = [[0, 5], [7, 0]]
    error = check(d, shortest_tour(d), 12)
    assert error is None, f"Two places: 0 -> 1 -> 0 costs 5 + 7 = 12. {error}."


def test_return_to_depot_counts():
    d = [[0, 1, 100], [100, 0, 1], [1, 100, 0]]
    error = check(d, shortest_tour(d), 3)
    assert error is None, (
        f"{error}. If you got 2, you forgot the drive back to 0: add dist[last][0] to f[full][last].")


def test_nearest_neighbour_is_not_enough():
    d = [[0, 1, 2, 3],
         [1, 0, 1, 5],
         [2, 1, 0, 20],
         [3, 5, 20, 0]]
    error = check(d, shortest_tour(d), 11)
    assert error is None, (
        f"{error}. 'Always drive to the closest place' goes 0 -> 1 -> 2 -> 3 -> 0 = 25; the best is "
        "0 -> 2 -> 1 -> 3 -> 0 = 11. Greedy is not enough: use the DP.")


def test_random_against_brute_force():
    rng = random.Random(7676)
    for _ in range(150):
        n = rng.randint(1, 7)
        d = [[0 if i == j else rng.randint(0, 30) for j in range(n)] for i in range(n)]
        error = check(d, shortest_tour([row[:] for row in d]), brute(d))
        assert error is None, f"dist={d}: {error}."


def test_thirteen_places():
    code = (
        "import random\n"
        "from solution import shortest_tour\n"
        "rng = random.Random(76)\n"
        "n = 13\n"
        "d = [[0 if i == j else rng.randint(1, 10**4) for j in range(n)] for i in range(n)]\n"
        "length, order = shortest_tour(d)\n"
        "route = order + [order[0]]\n"
        "print(length, sum(d[a][b] for a, b in zip(route, route[1:])), sorted(order) == list(range(n)), order[0])\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (30 s) for 13 places: trying all 12! = 479,001,600 orders is far too slow. "
        "The bitmask DP has 2**13 * 13 states.")
    assert r.returncode == 0, "Your code crashed on 13 places:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["14039", "14039", "True", "0"], (
        "13 places: expected length 14039 and an order that starts at 0, lists every place once and costs "
        f"exactly that; got (length, its cost, valid, first) = {r.stdout.split()}.")
