from collections import deque

MOD = 10**9 + 7


def _topological_order(n, adj):
    indeg = [0] * n
    for u in range(n):
        for v, _ in adj[u]:
            indeg[v] += 1
    ready = deque(v for v in range(n) if indeg[v] == 0)
    order = []
    while ready:
        u = ready.popleft()
        order.append(u)
        for v, _ in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                ready.append(v)
    return order


def _adjacency(n, edges):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
    return adj


def longest_from(n, edges, source):
    adj = _adjacency(n, edges)
    best = [None] * n
    best[source] = 0
    for u in _topological_order(n, adj):
        if best[u] is None:
            continue                               # not reachable: push nothing
        for v, w in adj[u]:
            if best[v] is None or best[u] + w > best[v]:
                best[v] = best[u] + w
    return best


def count_paths(n, edges, source, target):
    adj = _adjacency(n, edges)
    ways = [0] * n
    ways[source] = 1
    for u in _topological_order(n, adj):
        if ways[u] == 0:
            continue
        for v, _ in adj[u]:
            ways[v] = (ways[v] + ways[u]) % MOD
    return ways[target]
