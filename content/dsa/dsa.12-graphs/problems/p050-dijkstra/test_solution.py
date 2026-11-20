import random
import subprocess
import sys
from pathlib import Path

from solution import dijkstra

HERE = Path(__file__).parent
INF = float("inf")


def floyd(n, edges):
    """Slow but simple: all-pairs shortest paths, O(n^3)."""
    d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for u, v, w in edges:
        d[u][v] = min(d[u][v], w)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
    return d


def test_the_example():
    edges = [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1), (2, 3, 5), (3, 4, 3)]
    got = dijkstra(6, edges, 0)
    assert got == [0, 3, 1, 4, 7, INF], (
        f"expected [0, 3, 1, 4, 7, inf], got {got}. 0 -> 2 -> 1 (1 + 2 = 3) beats the direct 4, "
        "and vertex 5 has no edges, so it stays inf.")


def test_returns_a_list_with_inf_for_unreachable():
    got = dijkstra(3, [(0, 1, 2)], 0)
    assert isinstance(got, list), f"return a list of length n, got {type(got).__name__}."
    assert got == [0, 2, INF], f"vertex 2 cannot be reached: its distance is float('inf'), not -1 or None. Got {got}."


def test_first_route_found_is_not_final():
    # 1 is reached first with 5, later with 1 + 1 = 2
    got = dijkstra(3, [(0, 1, 5), (0, 2, 1), (2, 1, 1)], 0)
    assert got == [0, 2, 1], (
        f"expected [0, 2, 1], got {got}. Vertex 1 is first reached with 5 but 0 -> 2 -> 1 costs 2. "
        "Do not mark a vertex as done when you push it: only the pop makes its distance final.")


def test_weights_not_edge_counts():
    got = dijkstra(3, [(0, 1, 10), (0, 2, 1), (2, 1, 1)], 0)
    assert got[1] == 2, f"0 -> 2 -> 1 costs 2, the single edge 0 -> 1 costs 10. BFS counts edges; Dijkstra adds weights. Got {got[1]}."


def test_edges_are_one_way():
    got = dijkstra(2, [(1, 0, 3)], 0)
    assert got == [0, INF], f"the only edge goes 1 -> 0, so 1 is unreachable from 0. Do not add reverse edges. Got {got}."


def test_parallel_edges_self_loops_and_zero_weights():
    edges = [(0, 1, 7), (0, 1, 2), (1, 1, 0), (1, 2, 0), (2, 0, 1), (2, 3, 0)]
    got = dijkstra(4, edges, 0)
    assert got == [0, 2, 2, 2], f"parallel edges: use the cheaper one; 0-weight edges keep the distance. Expected [0, 2, 2, 2], got {got}."


def test_single_vertex_and_other_sources():
    assert dijkstra(1, [], 0) == [0], "one vertex: [0]."
    edges = [(0, 1, 1), (1, 2, 1), (2, 0, 1)]
    assert dijkstra(3, edges, 2) == [1, 2, 0], "the source is not always 0: start from the vertex you are given."


def test_the_edge_list_is_not_changed():
    edges = [(0, 1, 4), (1, 2, 1)]
    copy = list(edges)
    dijkstra(3, edges, 0)
    assert edges == copy, "do not change the edges list you were given."


def test_random_graphs_against_floyd_warshall():
    rng = random.Random(50)
    for _ in range(300):
        n = rng.randint(1, 12)
        edges = [(rng.randrange(n), rng.randrange(n), rng.randint(0, 9)) for _ in range(rng.randint(0, 30))]
        s = rng.randrange(n)
        want = floyd(n, edges)[s]
        got = dijkstra(n, edges, s)
        assert got == want, f"dijkstra({n}, {edges}, {s}): expected {want}, got {got}."


BIG = """
import random
from solution import dijkstra
rng = random.Random(5050)
n, m = 100000, 300000
edges = [(rng.randrange(n), rng.randrange(n), rng.randint(0, 10000)) for _ in range(m)]
d = dijkstra(n, edges, 0)
print(sum(x for x in d if x != float('inf')), sum(1 for x in d if x == float('inf')))
"""


def test_big_graph_is_fast_enough():
    import heapq
    rng = random.Random(5050)
    n, m = 100000, 300000
    edges = [(rng.randrange(n), rng.randrange(n), rng.randint(0, 10000)) for _ in range(m)]
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
    dist = [INF] * n
    dist[0] = 0
    heap = [(0, 0)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (d + w, v))
    want = f"{sum(x for x in dist if x != INF)} {sum(1 for x in dist if x == INF)}"
    try:
        r = subprocess.run([sys.executable, "-c", BIG], cwd=HERE, capture_output=True, text=True, timeout=15)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            "10**5 vertices and 3 * 10**5 edges did not finish in 15 seconds. Use a heap for the closest vertex "
            "(not a scan over all vertices), and skip stale entries.") from None
    assert r.returncode == 0, "your function crashed on the big graph:\n" + r.stderr[-800:]
    assert r.stdout.strip() == want, f"wrong distances on the big graph (sum of finite distances, count of inf): expected {want}, got {r.stdout.strip()}."
