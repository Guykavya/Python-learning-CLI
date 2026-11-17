import random

from solution import distance

INF = float("inf")


def floyd(n, edges):
    d = [[INF] * n for _ in range(n)]
    for i in range(n):
        d[i][i] = 0
    for u, v in edges:
        d[u][v] = d[v][u] = min(d[u][v], 1) if u != v else 0
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
    return d


def test_the_examples():
    edges = [(0, 1), (1, 2), (2, 3), (0, 3)]
    assert distance(5, edges, 0, 2) == 2, "0 -> 1 -> 2 has 2 edges (count edges, not vertices)."
    assert distance(5, edges, 0, 4) == -1, "Vertex 4 has no edges: return -1."
    assert distance(3, [(0, 1)], 2, 2) == 0, "s == t: distance 0, even for an isolated vertex."


def test_dfs_is_not_enough():
    ring = [(0, 1), (1, 2), (2, 3), (3, 0)]
    assert distance(4, ring, 0, 3) == 1, (
        "On the ring 0-1-2-3-0, vertex 3 is ONE edge from 0. If you got 3, your search followed 0 -> 1 -> 2 -> 3 (depth first). Use BFS.")


def test_random_against_floyd_warshall():
    rng = random.Random(1210)
    for _ in range(300):
        n = rng.randint(1, 9)
        edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, 14))]
        d = floyd(n, edges)
        for s in range(n):
            for t in range(n):
                want = -1 if d[s][t] == INF else d[s][t]
                got = distance(n, edges, s, t)
                assert got == want, f"distance({n}, {edges}, {s}, {t}) should be {want}, got {got}."


def test_long_path():
    n = 100_000
    edges = [(i, i + 1) for i in range(n - 1)]
    try:
        assert distance(n, edges, 0, n - 1) == n - 1, "A path of 100,000 vertices: the distance from one end to the other is 99,999."
        assert distance(n, edges, n - 1, 0) == n - 1, "Undirected: the same distance backwards."
    except RecursionError:
        raise AssertionError("RecursionError on a long path: use BFS with a queue, not recursion.") from None
