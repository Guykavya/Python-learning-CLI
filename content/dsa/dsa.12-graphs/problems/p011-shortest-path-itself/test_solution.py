import random
from collections import deque

from solution import shortest_path


def bfs_dist(n, edges, s):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    dist = {s: 0}
    queue = deque([s])
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                queue.append(v)
    return dist


def check(n, edges, s, t, got):
    dist = bfs_dist(n, edges, s)
    where = f"shortest_path({n}, {edges}, {s}, {t})" if len(edges) < 40 else f"shortest_path on {n} vertices from {s} to {t}"
    if t not in dist:
        assert got is None, f"{where}: {t} is not reachable, so the answer is None, got {got!r}."
        return
    assert got is not None, f"{where}: {t} is reachable (distance {dist[t]}), but you returned None."
    got = list(got)
    assert got and got[0] == s, f"{where}: the path must start with {s}; got {got[:5]}... Did you forget to reverse it?"
    assert got[-1] == t, f"{where}: the path must end with {t}; got ...{got[-5:]}."
    pairs = set()
    for u, v in edges:
        pairs.add((u, v))
        pairs.add((v, u))
    for a, b in zip(got, got[1:]):
        assert (a, b) in pairs, f"{where}: {a} and {b} are next to each other in your path, but there is no edge {a}-{b}."
    assert len(got) - 1 == dist[t], (
        f"{where}: your path has {len(got) - 1} edges, a shortest one has {dist[t]}. A DFS path is not always shortest: use BFS.")


def test_the_examples():
    edges = [(0, 1), (1, 2), (2, 3), (0, 3)]
    got = shortest_path(5, edges, 0, 2)
    assert got in ([0, 1, 2], [0, 3, 2]), f"Expected [0, 1, 2] or [0, 3, 2], got {got}."
    assert shortest_path(5, [(0, 1)], 0, 4) is None, "4 cannot be reached: return None."
    assert shortest_path(2, [], 1, 1) == [1], "s == t: the path is just [s]."


def test_paths_through_vertex_zero():
    got = shortest_path(4, [(3, 0), (0, 1), (1, 2)], 3, 2)
    assert got == [3, 0, 1, 2], (
        f"Expected [3, 0, 1, 2], got {got}. If the path stops at 0, you probably walked back with `while parent[x]:`; "
        "vertex 0 is falsy. Compare with None.")


def test_random_graphs():
    rng = random.Random(1211)
    for _ in range(400):
        n = rng.randint(1, 10)
        edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, 16))]
        s, t = rng.randrange(n), rng.randrange(n)
        check(n, edges, s, t, shortest_path(n, edges, s, t))


def test_ring_needs_bfs():
    n = 50
    ring = [(i, (i + 1) % n) for i in range(n)]
    check(n, ring, 0, n - 1, shortest_path(n, ring, 0, n - 1))


def test_long_path():
    n = 100_000
    edges = [(i, i + 1) for i in range(n - 1)]
    try:
        got = shortest_path(n, edges, 0, n - 1)
    except RecursionError:
        raise AssertionError("RecursionError on a path of 100,000 vertices: use BFS and walk the parents back with a loop.") from None
    assert got is not None and len(got) == n and got[0] == 0 and got[-1] == n - 1, "On the long path the answer is all 100,000 vertices in order."
