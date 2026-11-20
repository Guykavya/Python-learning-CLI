import random

from solution import bellman_ford

INF = float("inf")


def model(n, edges, s):
    """Floyd-Warshall: dist[s][v], and a negative cycle is reachable from s if s reaches some v with d[v][v] < 0."""
    d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for u, v, w in edges:
        if w < d[u][v]:
            d[u][v] = w
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
    if any(d[s][v] < INF and d[v][v] < 0 for v in range(n)):
        return None
    return d[s]


def test_the_examples():
    got = bellman_ford(4, [(0, 1, 4), (0, 2, 5), (2, 1, -3), (1, 3, 2)], 0)
    assert got == [0, 2, 5, 4], f"0 -> 2 -> 1 costs 5 - 3 = 2 (a negative edge, no negative cycle). Expected [0, 2, 5, 4], got {got}."
    got = bellman_ford(3, [(0, 1, 1), (1, 2, -2), (2, 1, 1)], 0)
    assert got is None, f"1 -> 2 -> 1 adds up to -1 and 0 can reach it: return None, got {got}."
    got = bellman_ford(4, [(0, 1, 3), (2, 3, -5), (3, 2, 1)], 0)
    assert got == [0, 3, INF, INF], (
        f"the negative cycle 2 -> 3 -> 2 cannot be reached from 0, so it does not matter: expected [0, 3, inf, inf], got {got}. "
        "Do you look for negative cycles anywhere in the graph instead of only those reachable from the source?")


def test_negative_self_loop():
    assert bellman_ford(2, [(0, 1, 1), (1, 1, -1)], 0) is None, "a self loop with weight -1 is a negative cycle, and 0 reaches it."
    assert bellman_ford(2, [(0, 1, 1), (1, 1, 0)], 0) == [0, 1], "a 0-weight self loop is not negative: do not use <= in the check."


def test_zero_weight_cycle_is_not_negative():
    got = bellman_ford(3, [(0, 1, 2), (1, 2, -3), (2, 1, 3)], 0)
    assert got == [0, 2, -1], f"1 -> 2 -> 1 adds up to 0: not negative. Expected [0, 2, -1], got {got}."


def test_the_longest_simple_route_needs_all_rounds():
    # Edges listed backwards: each round extends the best route by one edge only.
    n = 7
    edges = [(i, i + 1, -1) for i in reversed(range(n - 1))]
    got = bellman_ford(n, edges, 0)
    assert got == [0, -1, -2, -3, -4, -5, -6], (
        f"a path of 6 negative edges listed backwards needs all n - 1 = 6 rounds; got {got}. "
        "If you got None, you ran one round too few before the check.")


def test_cycle_reachable_only_through_a_negative_edge():
    edges = [(0, 1, -2), (1, 2, 1), (2, 3, 1), (3, 1, -3), (0, 4, 1)]
    assert bellman_ford(5, edges, 0) is None, "1 -> 2 -> 3 -> 1 adds up to -1 and is reachable: None."
    assert bellman_ford(5, edges, 4) == [INF, INF, INF, INF, 0], "from 4 nothing else can be reached, so the cycle does not matter."


def test_no_edges_and_single_vertex():
    assert bellman_ford(1, [], 0) == [0], "one vertex, no edges: [0]."
    assert bellman_ford(3, [], 1) == [INF, 0, INF], "no edges: only the source has a distance."


def test_input_not_changed():
    edges = [(0, 1, 4), (1, 2, -1)]
    copy = list(edges)
    bellman_ford(3, edges, 0)
    assert edges == copy, "do not change the edges list."


def test_random_graphs():
    rng = random.Random(57)
    for _ in range(500):
        n = rng.randint(1, 7)
        edges = [(rng.randrange(n), rng.randrange(n), rng.randint(-4, 9)) for _ in range(rng.randint(0, 14))]
        s = rng.randrange(n)
        want = model(n, edges, s)
        got = bellman_ford(n, edges, s)
        assert got == want, f"bellman_ford({n}, {edges}, {s}): expected {want}, got {got}."


def test_bigger_graph():
    rng = random.Random(570)
    n = 300
    edges = [(rng.randrange(n), rng.randrange(n), rng.randint(0, 1000)) for _ in range(3000)]
    edges += [(i, i + 1, -1) for i in range(0, 299, 3)]
    got = bellman_ford(n, edges, 0)
    dist = [INF] * n
    dist[0] = 0
    for _ in range(n - 1):
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    neg = any(dist[u] + w < dist[v] for u, v, w in edges if dist[u] < INF)
    assert got == (None if neg else dist), "wrong answer on a graph with 300 vertices and 3,100 edges."
