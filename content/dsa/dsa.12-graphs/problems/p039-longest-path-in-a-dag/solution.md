## Approach

A path into `v` ends with some edge `u -> v`, so the best path to `v` is the best path to some `u` plus that edge. In a DAG we can compute all of these in one pass, if each `u` is final before we use it. A topological order gives exactly that: every edge goes forward in the order (chapter section 7, "Dynamic programming on a DAG").

We push values forward. Unreachable vertices keep `None`, and a `None` is never pushed, so a vertex that cannot be reached from `source` (like 4 in the example) never adds its edges. Negative weights are no problem: there is no cycle to repeat them.

Counting uses the same order: every path to `v` is a path to some `u` followed by one of the edges `u -> v`. Parallel edges are separate list entries, so each adds `ways[u]` once.

```python
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
```

## Complexity

The topological order and each pass are `O(n + E)`.

## Another way

Relax every edge `n - 1` times, Bellman-Ford style, but with `max`: correct for a DAG and much slower (`O(n * E)`). Or a memoised recursive function `longest(v) = max(longest(u) + w)` over the edges into `v`: short, but it recurses as deep as the longest path, which on 100,000 vertices passes the recursion limit. In a graph **with** cycles the longest simple path is a famous hard problem (NP-hard): the topological order is what makes it easy here.
