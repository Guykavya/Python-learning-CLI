import random
import subprocess
import sys
from collections import Counter
from pathlib import Path

from solution import prim

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


def check(n, edges, got):
    """Validate a Prim answer: a real tree, grown from 0, each step a cheapest edge leaving the tree."""
    want = prim_total(n, edges)
    if want is None:
        assert got is None, f"the graph on {n} vertices with edges {edges} is not connected: return None, got {got}."
        return
    assert got is not None, f"the graph {edges} on {n} vertices is connected, but you returned None."
    total, tree = got
    assert len(tree) == n - 1, f"a spanning tree of {n} vertices has {n - 1} edges, you returned {len(tree)}: {tree}."
    available = Counter()
    for u, v, w in edges:
        if u != v:
            available[(u, v, w)] += 1
            available[(v, u, w)] += 1
    in_tree = {0}
    for step, (u, v, w) in enumerate(tree):
        assert available[(u, v, w)] > 0, f"step {step}: {(u, v, w)} is not an edge of the graph (or used twice)."
        available[(u, v, w)] -= 1
        available[(v, u, w)] -= 1
        assert u in in_tree and v not in in_tree, (
            f"step {step}: {(u, v, w)} must go from a tree vertex u to a new vertex v; the tree was {sorted(in_tree)}. "
            "Skip heap entries whose far end is already in the tree.")
        cheapest = min(c for a, b, c in edges if (a in in_tree) != (b in in_tree))
        assert w == cheapest, (
            f"step {step}: you added an edge of weight {w}, but the cheapest edge leaving the tree {sorted(in_tree)} "
            f"has weight {cheapest}. The heap key is the edge weight alone (not a distance from 0), and the order of "
            "adding is part of the answer.")
        in_tree.add(v)
    assert total == sum(w for _, _, w in tree) == want, f"the total must be the sum of the tree edges and minimal ({want}), got {total}."


def test_the_example():
    got = prim(4, [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 5), (2, 3, 8)])
    assert got == (8, [(0, 2, 1), (2, 1, 2), (1, 3, 5)]), f"expected (8, [(0, 2, 1), (2, 1, 2), (1, 3, 5)]), got {got}."


def test_edge_weight_not_distance():
    edges = [(0, 1, 1), (1, 2, 1), (2, 3, 1), (0, 3, 2.5)]
    got = prim(4, edges)
    assert got is not None and got[0] == 3, (
        f"the tree 0-1, 1-2, 2-3 costs 3; got {got}. If you took 0-3 (2.5), your key is the distance from 0 "
        "(Dijkstra), not the single edge weight.")
    check(4, edges, got)


def test_not_connected_and_tiny():
    assert prim(3, [(0, 1, 1)]) is None, "vertex 2 has no edge: None."
    assert prim(1, []) == (0, []), "one vertex: (0, [])."
    assert prim(2, [(1, 1, 3)]) is None, "a self loop does not connect anything: None."


def test_both_directions_of_an_edge_are_usable():
    got = prim(3, [(1, 0, 4), (2, 1, 3)])
    assert got == (7, [(0, 1, 4), (1, 2, 3)]), f"the edges are undirected: from 0 the edge (1, 0, 4) leads to 1. Got {got}."


def test_input_not_changed():
    edges = [(0, 1, 4), (1, 2, 3)]
    copy = list(edges)
    prim(3, edges)
    assert edges == copy, "do not change the edges list."


def test_random_graphs():
    rng = random.Random(62)
    for _ in range(300):
        n = rng.randint(1, 12)
        edges = [(rng.randrange(n), rng.randrange(n), rng.randint(-5, 9)) for _ in range(rng.randint(0, 30))]
        check(n, edges, prim(n, edges))


BIG = """
import random
from solution import prim
rng = random.Random(620)
n = 50000
edges = [(i, i + 1, rng.randint(1, 1000)) for i in range(n - 1)]
edges += [(rng.randrange(n), rng.randrange(n), rng.randint(1, 1000)) for _ in range(100000)]
got = prim(n, edges)
print("None" if got is None else f"{got[0]} {len(got[1])}")
"""


def test_big_graph():
    rng = random.Random(620)
    n = 50000
    edges = [(i, i + 1, rng.randint(1, 1000)) for i in range(n - 1)]
    edges += [(rng.randrange(n), rng.randrange(n), rng.randint(1, 1000)) for _ in range(100000)]
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    want = 0
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            want += w
    try:
        r = subprocess.run([sys.executable, "-c", BIG], cwd=HERE, capture_output=True, text=True, timeout=20)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            "50,000 vertices and 150,000 edges did not finish in 20 seconds. Use a heap of the edges leaving the tree "
            "(O(E log V)); scanning all vertices for the cheapest one is O(V^2), fine only for dense graphs.") from None
    assert r.returncode == 0, "your function crashed on the big graph:\n" + r.stderr[-800:]
    assert r.stdout.strip() == f"{want} {n - 1}", (
        f"on 50,000 vertices expected total {want} with {n - 1} edges, got '{r.stdout.strip()}' (total, number of edges).")
