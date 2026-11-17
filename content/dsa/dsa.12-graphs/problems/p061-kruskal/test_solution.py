import heapq
import itertools
import random
import subprocess
import sys
from pathlib import Path

from solution import kruskal

HERE = Path(__file__).parent

def prim_total(n, edges):
    """A plain O(V^2) Prim: total weight of a minimum spanning tree, None if disconnected."""
    INF = float("inf")
    w = [[INF] * n for _ in range(n)]
    for u, v, c in edges:
        if u != v and c < w[u][v]:
            w[u][v] = w[v][u] = c
    best = [INF] * n
    best[0] = 0
    used = [False] * n
    total = 0
    for _ in range(n):
        u = -1
        for i in range(n):
            if not used[i] and (u == -1 or best[i] < best[u]):
                u = i
        if best[u] == INF:
            return None
        used[u] = True
        total += best[u]
        for v in range(n):
            if not used[v] and w[u][v] < best[v]:
                best[v] = w[u][v]
    return total


def brute_total(n, edges):
    """Try every set of n - 1 edges (tiny graphs only)."""
    if n == 1:
        return 0
    best = None
    for pick in itertools.combinations(edges, n - 1):
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                x = parent[x]
            return x

        ok = True
        for u, v, w in pick:
            ru, rv = find(u), find(v)
            if ru == rv:
                ok = False
                break
            parent[ru] = rv
        if ok:
            t = sum(w for _, _, w in pick)
            if best is None or t < best:
                best = t
    return best


def test_the_examples():
    got = kruskal(4, [(0, 1, 1), (1, 2, 4), (0, 2, 3), (2, 3, 2), (1, 3, 5)])
    assert got == 6, f"the tree 0-1 (1), 2-3 (2), 0-2 (3) costs 6, got {got}."
    assert kruskal(3, [(0, 1, 1)]) is None, "vertex 2 has no edge: no spanning tree exists, return None."


def test_cheapest_edges_can_form_a_cycle():
    edges = [(0, 1, 1), (1, 2, 1), (0, 2, 1), (2, 3, 10)]
    got = kruskal(4, edges)
    assert got == 12, (
        f"the three 1-edges form a triangle: only two of them can be used, and 2-3 (10) is needed for vertex 3. "
        f"Expected 12, got {got}. Skip an edge whose ends are already connected.")


def test_not_connected_even_with_many_edges():
    edges = [(0, 1, 1), (1, 2, 1), (0, 2, 1), (3, 4, 1)]
    assert kruskal(5, edges) is None, "{0, 1, 2} and {3, 4} are not connected: None, not the weight of a forest."


def test_single_vertex_and_self_loops():
    assert kruskal(1, []) == 0, "one vertex: the empty tree, total 0."
    assert kruskal(1, [(0, 0, 5)]) == 0, "a self loop is never part of a tree."
    assert kruskal(2, [(0, 0, -5), (1, 1, -5), (0, 1, 3)]) == 3, "self loops are skipped even when they are cheap."


def test_negative_weights_and_parallel_edges():
    got = kruskal(3, [(0, 1, 5), (0, 1, -2), (1, 2, 0), (0, 2, -1)])
    assert got == -3, f"take 0-1 (-2) and 0-2 (-1): total -3. Got {got}."


def test_roots_not_parents():
    # After 0-1 and 2-3 and 1-3, vertices 0 and 2 have different parents but the same root.
    edges = [(0, 1, 1), (2, 3, 1), (1, 3, 1), (0, 2, 2), (3, 4, 5)]
    got = kruskal(5, edges)
    assert got == 8, f"0-2 (2) closes a cycle and must be skipped; the tree is 1 + 1 + 1 + 5 = 8. Got {got}. Compare roots (find), not parents."


def test_input_not_changed():
    edges = [(0, 1, 5), (1, 2, 1)]
    copy = list(edges)
    kruskal(3, edges)
    assert edges == copy, "do not sort the caller's list in place; use sorted()."


def test_tiny_graphs_against_every_choice():
    rng = random.Random(61)
    for _ in range(200):
        n = rng.randint(1, 5)
        edges = [(rng.randrange(n), rng.randrange(n), rng.randint(-3, 9)) for _ in range(rng.randint(0, 7))]
        want = brute_total(n, edges)
        got = kruskal(n, edges)
        assert got == want, f"kruskal({n}, {edges}): expected {want}, got {got}."


def test_random_against_prim():
    rng = random.Random(610)
    for _ in range(200):
        n = rng.randint(1, 30)
        edges = [(rng.randrange(n), rng.randrange(n), rng.randint(-20, 50)) for _ in range(rng.randint(0, 80))]
        want = prim_total(n, edges)
        got = kruskal(n, edges)
        assert got == want, f"kruskal on {n} vertices and {len(edges)} edges: expected {want} (Prim), got {got}."


BIG = """
import random
from solution import kruskal
rng = random.Random(611)
n = 100000
edges = [(i, i + 1, rng.randint(1, 10 ** 6)) for i in range(n - 1)]
edges += [(rng.randrange(n), rng.randrange(n), rng.randint(1, 10 ** 6)) for _ in range(100000)]
rng.shuffle(edges)
print(kruskal(n, edges))
"""


def test_big_graph():
    rng = random.Random(611)
    n = 100000
    edges = [(i, i + 1, rng.randint(1, 10 ** 6)) for i in range(n - 1)]
    edges += [(rng.randrange(n), rng.randrange(n), rng.randint(1, 10 ** 6)) for _ in range(100000)]
    rng.shuffle(edges)
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((w, v))
        adj[v].append((w, u))
    seen = [False] * n
    heap = [(0, 0)]
    total = 0
    while heap:
        w, u = heapq.heappop(heap)
        if seen[u]:
            continue
        seen[u] = True
        total += w
        for item in adj[u]:
            if not seen[item[1]]:
                heapq.heappush(heap, item)
    try:
        r = subprocess.run([sys.executable, "-c", BIG], cwd=HERE, capture_output=True, text=True, timeout=20)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            "10**5 vertices and 2 * 10**5 edges did not finish in 20 seconds. Use Union-Find with path compression "
            "(or halving) to test 'already connected?', not a search through the tree for every edge.") from None
    assert r.returncode == 0, "your function crashed on the big graph:\n" + r.stderr[-800:]
    assert r.stdout.strip() == str(total), f"wrong total on a graph with 10**5 vertices: expected {total}, got {r.stdout.strip()}."
