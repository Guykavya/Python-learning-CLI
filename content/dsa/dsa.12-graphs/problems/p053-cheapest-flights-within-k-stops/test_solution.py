import random

from solution import find_cheapest_price


def slow(n, flights, src, dst, k):
    """Try every walk with at most k + 1 flights."""
    best = -1
    out = [[] for _ in range(n)]
    for u, v, p in flights:
        out[u].append((v, p))

    def walk(u, used, cost):
        nonlocal best
        if u == dst and used > 0:
            if best == -1 or cost < best:
                best = cost
        if used == k + 1:
            return
        for v, p in out[u]:
            walk(v, used + 1, cost + p)

    walk(src, 0, 0)
    return best


FL = [(0, 1, 100), (1, 2, 100), (2, 0, 100), (1, 3, 600), (2, 3, 200)]


def test_the_examples():
    assert find_cheapest_price(4, FL, 0, 3, 1) == 700, "with 1 stop the best is 0 -> 1 -> 3 = 700."
    assert find_cheapest_price(4, FL, 0, 3, 2) == 400, "with 2 stops, 0 -> 1 -> 2 -> 3 = 400 is allowed."


def test_the_copy_trap():
    flights = [(0, 1, 100), (1, 2, 100), (0, 2, 500)]
    got = find_cheapest_price(3, flights, 0, 2, 0)
    assert got == 500, (
        f"0 stops: only the direct flight (500) is allowed, got {got}. If you got 200, a price found earlier in the "
        "same round was used again: read from a copy of the previous round (prev = dist[:]).")
    assert find_cheapest_price(3, flights, 0, 2, 1) == 200, "1 stop: 0 -> 1 -> 2 = 200."


def test_copy_trap_when_edges_are_listed_backwards():
    flights = [(2, 3, 1), (1, 2, 1), (0, 1, 1), (0, 3, 100)]
    assert find_cheapest_price(4, flights, 0, 3, 2) == 3, "2 stops allow 0 -> 1 -> 2 -> 3 = 3; you need k + 1 = 3 rounds."
    flights2 = [(0, 1, 1), (1, 2, 1), (2, 3, 1), (0, 3, 100)]
    got = find_cheapest_price(4, flights2, 0, 3, 1)
    assert got == 100, f"1 stop: 0 -> 1 -> 2 -> 3 has 2 stops and is not allowed; the answer is the direct 100. Got {got}."


def test_k_stops_means_k_plus_one_flights():
    got = find_cheapest_price(3, [(0, 1, 1), (1, 2, 1)], 0, 2, 1)
    assert got == 2, f"one stop (city 1) means two flights: 0 -> 1 -> 2 = 2. Got {got}. Do you run only k rounds?"


def test_dijkstra_on_cities_is_not_enough():
    # The cheapest route to 3 has many stops; the limit forces a dearer one with fewer.
    flights = [(0, 1, 1), (1, 2, 1), (2, 3, 1), (0, 3, 50), (3, 4, 1)]
    got = find_cheapest_price(5, flights, 0, 4, 1)
    assert got == 51, (
        f"with 1 stop the only route is 0 -> 3 -> 4 = 51; the cheaper 0 -> 1 -> 2 -> 3 -> 4 has 3 stops. Got {got}. "
        "Plain Dijkstra keeps only the cheapest route to 3 and cannot know it uses too many flights.")


def test_a_cheap_route_with_too_many_flights_must_not_block_a_dearer_one():
    # 2 is reached cheaply in 2 flights (0 -> 1 -> 2 = 2) and dearly in 1 flight (0 -> 2 = 5).
    flights = [(0, 1, 1), (1, 2, 1), (0, 2, 5), (2, 3, 1)]
    got = find_cheapest_price(4, flights, 0, 3, 1)
    assert got == 6, (
        f"with 1 stop the route must be 0 -> 2 -> 3 = 6, got {got}. Keeping one best price per city (Dijkstra with "
        "dist[city]) throws away the 1-flight price 5 for city 2 because 2 is cheaper, but the cheaper one used 2 flights. "
        "Keep the prices per round (Bellman-Ford with a copy), or make (city, flights used) the state.")


def test_no_route():
    assert find_cheapest_price(3, [(0, 1, 5)], 0, 2, 2) == -1, "city 2 cannot be reached: -1."
    assert find_cheapest_price(3, [(0, 1, 5), (1, 2, 5)], 0, 2, 0) == -1, "only a 1-stop route exists, k = 0: -1."
    assert find_cheapest_price(2, [(1, 0, 5)], 0, 1, 1) == -1, "flights are one-way: 1 -> 0 does not help from 0."


def test_input_not_changed():
    flights = list(FL)
    find_cheapest_price(4, flights, 0, 3, 2)
    assert flights == FL, "do not change the flights list."


def test_random_against_trying_every_walk():
    rng = random.Random(53)
    for _ in range(400):
        n = rng.randint(2, 6)
        pairs = [(u, v) for u in range(n) for v in range(n) if u != v]
        rng.shuffle(pairs)
        flights = [(u, v, rng.randint(1, 30)) for u, v in pairs[:rng.randint(0, len(pairs))]]
        src, dst = rng.sample(range(n), 2)
        k = rng.randint(0, 3)
        want = slow(n, flights, src, dst, k)
        got = find_cheapest_price(n, flights, src, dst, k)
        assert got == want, f"find_cheapest_price({n}, {flights}, {src}, {dst}, {k}): expected {want}, got {got}."


def test_hundred_cities():
    rng = random.Random(530)
    n = 100
    flights = []
    for u in range(n):
        for v in rng.sample(range(n), 30):
            if u != v:
                flights.append((u, v, rng.randint(1, 10000)))
    for k in (0, 1, 5, 99):
        got = find_cheapest_price(n, flights, 0, 99, k)
        dist = [float("inf")] * n
        dist[0] = 0
        for _ in range(k + 1):
            prev = dist[:]
            for u, v, p in flights:
                if prev[u] + p < dist[v]:
                    dist[v] = prev[u] + p
        want = -1 if dist[99] == float("inf") else dist[99]
        assert got == want, f"100 cities, k = {k}: expected {want}, got {got}."
