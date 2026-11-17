import random
import time

from solution import floyd_warshall

INF = float("inf")


def bellman_rows(n, edges):
    """One Bellman-Ford per source: a different algorithm, the same answers."""
    rows = []
    for s in range(n):
        d = [INF] * n
        d[s] = 0
        for _ in range(n - 1):
            for u, v, w in edges:
                if d[u] + w < d[v]:
                    d[v] = d[u] + w
        rows.append(d)
    return rows


def test_the_example():
    got = floyd_warshall(4, [(0, 1, 3), (0, 2, 8), (1, 2, 2), (2, 3, 1), (3, 0, 2), (1, 3, 7)])
    want = [[0, 3, 5, 6], [5, 0, 2, 3], [3, 6, 0, 1], [2, 5, 7, 0]]
    assert got == want, f"expected {want}, got {got}. dist[0][3] = 6 through 0 -> 1 -> 2 -> 3."


def test_the_loop_order_trap():
    got = floyd_warshall(4, [(0, 1, 1), (1, 0, 6), (2, 3, 2), (3, 1, 8)])
    assert got[2] == [16, 10, 0, 2], (
        f"row 2 should be [16, 10, 0, 2] (2 -> 3 -> 1 -> 0 = 2 + 8 + 6), got {got[2]}. "
        "If dist[2][0] stayed inf, your k loop is not the outermost one: when the pair (2, 0) was done, "
        "dist[2][1] was not known yet.")


def test_parallel_edges_and_self_loops():
    got = floyd_warshall(2, [(0, 1, 9), (0, 1, 4), (0, 1, 7), (1, 1, 5)])
    assert got == [[0, 4], [INF, 0]], (
        f"expected [[0, 4], [inf, 0]], got {got}. Keep the cheapest of the parallel edges (4); a self loop of 5 "
        "does not change the diagonal 0; and the edges are one-way, so 1 cannot reach 0.")


def test_rows_are_separate_lists():
    got = floyd_warshall(3, [(0, 1, 1)])
    assert got == [[0, 1, INF], [INF, 0, INF], [INF, INF, 0]], (
        f"only 0 -> 1 exists: expected [[0, 1, inf], [inf, 0, inf], [inf, inf, 0]], got {got}. "
        "If a whole column changed, your rows are one shared list ([[inf] * n] * n).")
    got[0][2] = 99
    assert got[1][2] != 99, "the rows of the table must be separate lists: changing one row changed another."


def test_negative_edges():
    got = floyd_warshall(3, [(0, 1, 4), (1, 2, -2), (0, 2, 3)])
    assert got[0] == [0, 4, 2], f"0 -> 1 -> 2 = 4 - 2 = 2 beats the direct 3. Got {got[0]}."


def test_single_vertex_and_no_edges():
    assert floyd_warshall(1, []) == [[0]], "one vertex: [[0]]."
    assert floyd_warshall(2, []) == [[0, INF], [INF, 0]], "no edges: 0 on the diagonal, inf elsewhere."


def test_input_not_changed():
    edges = [(0, 1, 3), (1, 0, 1)]
    copy = list(edges)
    floyd_warshall(2, edges)
    assert edges == copy, "do not change the edges list."


def test_random_against_bellman_ford():
    rng = random.Random(58)
    for _ in range(300):
        n = rng.randint(1, 8)
        # w = base + h[u] - h[v] with base >= 0: around any cycle the h terms cancel, so no cycle is negative,
        # but single edges can be negative
        h = [rng.randint(0, 6) for _ in range(n)]
        edges = []
        for _ in range(rng.randint(0, 20)):
            u, v = rng.randrange(n), rng.randrange(n)
            edges.append((u, v, rng.randint(0, 5) + h[u] - h[v]))
        want = bellman_rows(n, edges)
        got = floyd_warshall(n, edges)
        assert got == want, f"floyd_warshall({n}, {edges}): expected {want}, got {got}."


def test_150_vertices():
    rng = random.Random(580)
    n = 150
    edges = [(rng.randrange(n), rng.randrange(n), rng.randint(1, 1000)) for _ in range(1500)]
    start = time.perf_counter()
    got = floyd_warshall(n, edges)
    took = time.perf_counter() - start
    import heapq
    for s in (0, 7, 149):
        d = [INF] * n
        d[s] = 0
        adj = [[] for _ in range(n)]
        for u, v, w in edges:
            adj[u].append((v, w))
        heap = [(0, s)]
        while heap:
            du, u = heapq.heappop(heap)
            if du > d[u]:
                continue
            for v, w in adj[u]:
                if du + w < d[v]:
                    d[v] = du + w
                    heapq.heappush(heap, (du + w, v))
        assert got[s] == d, f"row {s} of the 150-vertex table is wrong."
    assert took < 60, f"150 vertices took {took:.1f} s; three plain nested loops need only a few seconds."
