import ast
import heapq
import random
import subprocess
import sys
from pathlib import Path

from solution import zero_one_bfs

INF = float("inf")
SOLUTION = Path(__file__).with_name("solution.py")
HERE = Path(__file__).parent


def dijkstra(n, edges, s):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
    dist = [INF] * n
    dist[s] = 0
    heap = [(0, s)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (d + w, v))
    return dist


def test_no_heapq():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    mods = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    mods |= {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    assert "heapq" not in mods, "this exercise is about the deque trick: do not import heapq (Dijkstra would work, but costs a log factor)."


def test_the_example():
    got = zero_one_bfs(4, [(0, 1, 1), (0, 2, 0), (2, 1, 0), (1, 3, 1)], 0)
    assert got == [0, 0, 0, 1], (
        f"expected [0, 0, 0, 1], got {got}. Vertex 1 is first reached through a 1-edge, but 0 -> 2 -> 1 is free. "
        "Compare distances (dist[u] + w < dist[v]) instead of a seen flag.")


def test_weights_count():
    got = zero_one_bfs(3, [(0, 1, 1), (1, 2, 1), (0, 2, 1)], 0)
    assert got == [0, 1, 1], f"all weights 1: this is plain BFS. Got {got}."
    got = zero_one_bfs(3, [(0, 1, 0), (1, 2, 0)], 0)
    assert got == [0, 0, 0], f"all weights 0: everything reachable has distance 0. Got {got}. Do you ignore the weights?"


def test_zero_edge_found_after_a_one_edge():
    got = zero_one_bfs(4, [(0, 1, 1), (0, 2, 1), (1, 3, 1), (2, 3, 0)], 0)
    assert got == [0, 1, 1, 1], f"0 -> 2 -> 3 costs 1 + 0 = 1, not 2. Got {got}."
    got = zero_one_bfs(5, [(0, 1, 1), (0, 2, 0), (2, 3, 0), (3, 1, 0), (1, 4, 0)], 0)
    assert got == [0, 0, 0, 0, 0], f"a chain of free edges 0 -> 2 -> 3 -> 1 -> 4 beats the 1-edge 0 -> 1. Got {got}."


def test_unreachable_is_inf():
    got = zero_one_bfs(3, [(1, 2, 0)], 0)
    assert got == [0, INF, INF], f"vertices 1 and 2 cannot be reached from 0: float('inf'). Got {got}."


def test_edges_are_one_way_and_parallel_edges():
    assert zero_one_bfs(2, [(1, 0, 0)], 0) == [0, INF], "the edge goes 1 -> 0; from 0 vertex 1 is unreachable."
    assert zero_one_bfs(2, [(0, 1, 1), (0, 1, 0), (1, 1, 1)], 0) == [0, 0], "two edges 0 -> 1: the free one wins."


def test_random_against_dijkstra():
    rng = random.Random(56)
    for _ in range(400):
        n = rng.randint(1, 12)
        edges = [(rng.randrange(n), rng.randrange(n), rng.randint(0, 1)) for _ in range(rng.randint(0, 30))]
        s = rng.randrange(n)
        want = dijkstra(n, edges, s)
        got = zero_one_bfs(n, edges, s)
        assert got == want, f"zero_one_bfs({n}, {edges}, {s}): expected {want}, got {got}."


BIG = """
import random
from solution import zero_one_bfs
rng = random.Random(560)
n = 100000
edges = [(i, i + 1, 1) for i in range(n - 1)]
edges += [(rng.randrange(n), rng.randrange(n), rng.randint(0, 1)) for _ in range(200000)]
d = zero_one_bfs(n, edges, 0)
print(sum(x for x in d if x != float('inf')), sum(1 for x in d if x == float('inf')))
"""


def test_big_graph():
    rng = random.Random(560)
    n = 100000
    edges = [(i, i + 1, 1) for i in range(n - 1)]
    edges += [(rng.randrange(n), rng.randrange(n), rng.randint(0, 1)) for _ in range(200000)]
    want = dijkstra(n, edges, 0)
    want = f"{sum(x for x in want if x != INF)} {sum(1 for x in want if x == INF)}"
    try:
        r = subprocess.run([sys.executable, "-c", BIG], cwd=HERE, capture_output=True, text=True, timeout=15)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            "10**5 vertices and 3 * 10**5 edges did not finish in 15 seconds (the deque version needs about one). "
            "Check which end each edge goes to: weight 0 to the FRONT (appendleft), weight 1 to the BACK (append). "
            "With the ends swapped the answers can still be right, but vertices are processed again and again.") from None
    assert r.returncode == 0, "your function crashed on the big graph:\n" + r.stderr[-800:]
    assert r.stdout.strip() == want, f"wrong distances on the big graph (sum of finite distances, count of inf): expected {want}, got {r.stdout.strip()}."
