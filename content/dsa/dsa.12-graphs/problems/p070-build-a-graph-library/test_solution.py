import random
import subprocess
import sys
from collections import deque
from pathlib import Path

import pytest

from solution import Graph

HERE = Path(__file__).parent
INF = float("inf")


# ---------- small, obviously right models (written with recursion and plain loops: tiny graphs only)

def build(n, edges, directed=False):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
        if not directed:
            adj[v].append((u, w))
    return adj


def model_bfs(adj, s):
    seen, order, q = {s}, [], deque([s])
    while q:
        u = q.popleft()
        order.append(u)
        for v, _ in adj[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    return order


def model_dfs(adj, s):
    seen, order = set(), []

    def visit(u):
        seen.add(u)
        order.append(u)
        for v, _ in adj[u]:
            if v not in seen:
                visit(v)

    visit(s)
    return order


def model_components(adj):
    n, seen, out = len(adj), set(), []
    for s in range(n):
        if s not in seen:
            comp = model_bfs(adj, s)
            seen.update(comp)
            out.append(sorted(comp))
    return out


def model_dist(adj, s):
    n = len(adj)
    d = [INF] * n
    d[s] = 0
    for _ in range(n):
        for u in range(n):
            for v, w in adj[u]:
                if d[u] + w < d[v]:
                    d[v] = d[u] + w
    return d


def has_cycle(adj):
    color = [0] * len(adj)

    def visit(u):
        color[u] = 1
        for v, _ in adj[u]:
            if color[v] == 1 or (color[v] == 0 and visit(v)):
                return True
        color[u] = 2
        return False

    return any(color[u] == 0 and visit(u) for u in range(len(adj)))


def make(n, edges, directed=False):
    g = Graph(n, directed=directed)
    for u, v, w in edges:
        g.add_edge(u, v, w)
    return g


# ---------- the example and each method on its own

def test_the_example():
    g = make(6, [(0, 1, 1), (0, 2, 1), (1, 3, 1), (2, 3, 1), (4, 5, 1)])
    assert g.bfs(0) == [0, 1, 2, 3], f"bfs(0) should be [0, 1, 2, 3], got {g.bfs(0)}."
    assert g.dfs(0) == [0, 1, 3, 2], f"dfs(0) should be [0, 1, 3, 2] (0, then 1, then 1's neighbour 3, then back to 3's neighbour 2), got {g.dfs(0)}."
    assert g.components() == [[0, 1, 2, 3], [4, 5]], f"components() should be [[0, 1, 2, 3], [4, 5]], got {g.components()}."
    d = Graph(3, directed=True)
    d.add_edge(0, 1, 5)
    d.add_edge(1, 2, 1)
    d.add_edge(0, 2, 9)
    assert d.shortest(0) == [0, 5, 6], f"shortest(0) should be [0, 5, 6] (0 -> 1 -> 2 = 6 beats the direct 9), got {d.shortest(0)}."
    assert d.topo() == [0, 1, 2], f"the only topological order is [0, 1, 2], got {d.topo()}."


def test_default_weight_and_undirected_edges():
    g = Graph(3)
    g.add_edge(0, 1)
    g.add_edge(2, 1)
    assert g.shortest(0) == [0, 1, 2], f"the default weight is 1 and edges go both ways: expected [0, 1, 2], got {g.shortest(0)}."
    assert g.bfs(2) == [2, 1, 0], f"from 2 the undirected edge (2, 1) leads to 1, then (0, 1) leads to 0; got {g.bfs(2)}."


def test_add_edge_checks():
    g = Graph(3)
    with pytest.raises(ValueError):
        g.add_edge(0, 1, -2)
    with pytest.raises(IndexError):
        g.add_edge(0, 3)
    with pytest.raises(IndexError):
        g.add_edge(-1, 0)
    assert g.bfs(0) == [0], "an edge that was refused must not be added."


def test_dfs_order_is_the_recursive_order():
    g = make(5, [(0, 1, 1), (0, 2, 1), (0, 3, 1), (1, 4, 1), (2, 4, 1)])
    got = g.dfs(0)
    assert got == [0, 1, 4, 2, 3], (
        f"expected [0, 1, 4, 2, 3], got {got}. With a stack, push the neighbours in REVERSE order and skip a vertex "
        "that is already visited when you pop it; marking at push time or pushing in list order gives another order.")


def test_bfs_has_no_duplicates():
    g = make(4, [(0, 1, 1), (0, 2, 1), (1, 3, 1), (2, 3, 1)])
    got = g.bfs(0)
    assert got == [0, 1, 2, 3], f"3 is reachable from 1 and from 2 but must appear once; got {got}. Mark a vertex when you push it."


def test_unreachable_vertices():
    g = make(4, [(0, 1, 2)], directed=True)
    assert g.bfs(0) == [0, 1] and g.dfs(0) == [0, 1], "bfs and dfs list only the vertices reachable from the start."
    assert g.shortest(0) == [0, 2, INF, INF], f"unreachable vertices have distance inf, got {g.shortest(0)}."
    assert g.bfs(2) == [2], "from an isolated vertex only itself is reachable."


def test_components_rules():
    g = make(5, [(3, 1, 1), (4, 0, 1)])
    assert g.components() == [[0, 4], [1, 3], [2]], (
        f"each component sorted, the list ordered by smallest vertex, isolated vertices included: [[0, 4], [1, 3], [2]]; got {g.components()}.")
    d = Graph(2, directed=True)
    with pytest.raises(ValueError):
        d.components()


def test_topo_rules():
    d = make(4, [(0, 1, 1), (1, 2, 1), (2, 0, 1)], directed=True)
    assert d.topo() is None, "0 -> 1 -> 2 -> 0 is a cycle: topo() returns None."
    u = Graph(2)
    with pytest.raises(ValueError):
        u.topo()
    e = Graph(3, directed=True)
    got = e.topo()
    assert got is not None and sorted(got) == [0, 1, 2], f"no edges: any order of all three vertices is fine; got {got}."


def test_self_loop_is_a_cycle_and_weights_matter():
    d = make(2, [(0, 0, 1), (0, 1, 1)], directed=True)
    assert d.topo() is None, "a self loop is a cycle of length 1: no topological order."
    g = make(3, [(0, 1, 10), (0, 2, 1), (2, 1, 1)])
    assert g.shortest(0)[1] == 2, "0 -> 2 -> 1 costs 2, the direct edge 10: shortest must add weights (not BFS)."


@pytest.mark.parametrize("directed", [False, True])
def test_random_graphs_against_models(directed):
    rng = random.Random(70 + directed)
    for _ in range(200):
        n = rng.randint(1, 10)
        edges = [(rng.randrange(n), rng.randrange(n), rng.randint(0, 9)) for _ in range(rng.randint(0, 18))]
        g = make(n, edges, directed)
        adj = build(n, edges, directed)
        s = rng.randrange(n)
        assert g.bfs(s) == model_bfs(adj, s), f"bfs({s}) on {n} vertices, edges {edges}, directed={directed}: expected {model_bfs(adj, s)}, got {g.bfs(s)}."
        assert g.dfs(s) == model_dfs(adj, s), f"dfs({s}) on {n} vertices, edges {edges}, directed={directed}: expected {model_dfs(adj, s)}, got {g.dfs(s)}."
        assert g.shortest(s) == model_dist(adj, s), f"shortest({s}) on edges {edges}, directed={directed}: expected {model_dist(adj, s)}, got {g.shortest(s)}."
        if directed:
            order = g.topo()
            if has_cycle(adj):
                assert order is None, f"edges {edges} contain a cycle: topo() must return None, got {order}."
            else:
                assert order is not None and sorted(order) == list(range(n)), f"topo() must list every vertex once, got {order}."
                pos = {v: i for i, v in enumerate(order)}
                for u, v, _ in edges:
                    assert pos[u] < pos[v], f"topo() gave {order}, but the edge {u} -> {v} goes backwards."
        else:
            assert g.components() == model_components(adj), f"components() on edges {edges}: expected {model_components(adj)}, got {g.components()}."


BIG = """
from solution import Graph
n = 100000
g = Graph(n)
for i in range(n - 1):
    g.add_edge(i, i + 1)
d = g.dfs(0)
c = g.components()
h = Graph(n, directed=True)
for i in range(n - 1):
    h.add_edge(i, i + 1, 2)
t = h.topo()
s = h.shortest(0)
print(len(d), d[-1], len(c), len(t), t[0], t[-1], s[-1])
"""


def test_a_chain_of_100000_vertices():
    try:
        r = subprocess.run([sys.executable, "-c", BIG], cwd=HERE, capture_output=True, text=True, timeout=20)
    except subprocess.TimeoutExpired:
        raise AssertionError("a chain of 100,000 vertices did not finish in 20 seconds: every method must be O(V + E) (Dijkstra O((V + E) log V)).") from None
    assert "RecursionError" not in r.stderr and "maximum recursion depth" not in r.stderr, (
        "a chain of 100,000 vertices hit the recursion limit: dfs (and topo, if it uses DFS) must use an explicit stack.")
    assert r.returncode == 0, "your class crashed on a chain of 100,000 vertices:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["100000", "99999", "1", "100000", "0", "99999", "199998"], (
        f"on the chain expected dfs length 100000 ending at 99999, one component, a topological order 0 .. 99999 and "
        f"distance 199998 to the end; got {r.stdout.strip()}.")
