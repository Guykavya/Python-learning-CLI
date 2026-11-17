import random
from collections import deque

from solution import bfs_order


def model(n, edges, start, directed):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        if not directed and u != v:
            adj[v].append(u)
    seen, queue, order = {start}, deque([start]), []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                queue.append(v)
    return order


def test_the_examples():
    got = bfs_order(6, [(0, 2), (0, 1), (1, 3), (2, 3), (3, 4)], 0)
    assert got == [0, 2, 1, 3, 4], (
        f"Expected [0, 2, 1, 3, 4], got {got}. adj[0] is [2, 1] in edge-list order (do not sort it), "
        "and vertex 5 is not reachable, so it is not in the answer.")
    assert bfs_order(3, [(1, 0), (1, 2)], 0, directed=True) == [0], "Directed: the edges leave 1, so from 0 nothing is reachable."


def test_waves_not_depth():
    edges = [(0, 1), (0, 2), (1, 3), (3, 4), (2, 5)]
    got = bfs_order(6, edges, 0)
    assert got == [0, 1, 2, 3, 5, 4], (
        f"Expected [0, 1, 2, 3, 5, 4], got {got}. BFS takes all of distance 1 (1, 2) before distance 2 (3, 5). "
        "A stack (list.pop()) gives a depth-first order instead.")


def test_single_vertex_and_self_loop():
    assert bfs_order(1, [], 0) == [0], "A single vertex: just the start."
    assert bfs_order(2, [(0, 0), (0, 1)], 0) == [0, 1], "A self loop must not add the start twice."


def test_start_in_the_middle_and_directed():
    edges = [(0, 1), (1, 2), (2, 3)]
    assert bfs_order(4, edges, 2) == [2, 1, 3, 0], "Undirected: from 2, the neighbours are 1 (edge (1, 2) comes first) and 3, then 0 through 1."
    assert bfs_order(4, edges, 2, directed=True) == [2, 3], "Directed: from 2 only 3 is reachable."


def test_random_graphs():
    rng = random.Random(1209)
    for _ in range(400):
        n = rng.randint(1, 10)
        edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, 18))]
        s = rng.randrange(n)
        for directed in (False, True):
            want = model(n, edges, s, directed)
            got = bfs_order(n, edges, s, directed)
            assert got == want, f"bfs_order({n}, {edges}, {s}, directed={directed}) should be {want}, got {got}."


def test_big_graph():
    n = 100_000
    rng = random.Random(1210)
    edges = [(i, rng.randrange(i)) for i in range(1, n)]
    got = bfs_order(n, edges, 0)
    assert len(got) == n and got[0] == 0, "A random tree with 100,000 vertices: every vertex is reached once."
    assert got == model(n, edges, 0, False), "Wrong order on the big random tree."
