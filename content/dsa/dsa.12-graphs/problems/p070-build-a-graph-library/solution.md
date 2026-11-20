## Approach

One adjacency list of `(neighbour, weight)` pairs serves every method. BFS and DFS ignore the weights; Dijkstra uses them. All searches use explicit queues or stacks, so a chain of `10**5` vertices is fine. Kahn's algorithm gives a topological order without recursion and detects cycles by counting.

## Code

```python
import heapq
from collections import deque


class Graph:
    def __init__(self, n, directed=False):
        self.n = n
        self.directed = directed
        self.adj = [[] for _ in range(n)]

    def add_edge(self, u, v, w=1):
        if not (0 <= u < self.n and 0 <= v < self.n):
            raise IndexError(f"vertex out of range: {u}, {v}")
        if w < 0:
            raise ValueError("negative weights are not allowed")
        self.adj[u].append((v, w))
        if not self.directed:
            self.adj[v].append((u, w))

    def bfs(self, s):
        seen = [False] * self.n
        seen[s] = True
        order, queue = [], deque([s])
        while queue:
            u = queue.popleft()
            order.append(u)
            for v, _ in self.adj[u]:
                if not seen[v]:
                    seen[v] = True
                    queue.append(v)
        return order

    def dfs(self, s):
        seen = [False] * self.n
        order, stack = [], [s]
        while stack:
            u = stack.pop()
            if seen[u]:
                continue
            seen[u] = True
            order.append(u)
            for v, _ in reversed(self.adj[u]):
                if not seen[v]:
                    stack.append(v)
        return order

    def components(self):
        if self.directed:
            raise ValueError("components() needs an undirected graph")
        seen = [False] * self.n
        result = []
        for s in range(self.n):
            if seen[s]:
                continue
            seen[s] = True
            group, stack = [s], [s]
            while stack:
                u = stack.pop()
                for v, _ in self.adj[u]:
                    if not seen[v]:
                        seen[v] = True
                        group.append(v)
                        stack.append(v)
            result.append(sorted(group))
        return result

    def topo(self):
        if not self.directed:
            raise ValueError("topo() needs a directed graph")
        indeg = [0] * self.n
        for u in range(self.n):
            for v, _ in self.adj[u]:
                indeg[v] += 1
        queue = deque(u for u in range(self.n) if indeg[u] == 0)
        order = []
        while queue:
            u = queue.popleft()
            order.append(u)
            for v, _ in self.adj[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    queue.append(v)
        return order if len(order) == self.n else None

    def shortest(self, s):
        INF = float("inf")
        dist = [INF] * self.n
        dist[s] = 0
        heap = [(0, s)]
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u]:
                continue
            for v, w in self.adj[u]:
                if d + w < dist[v]:
                    dist[v] = d + w
                    heapq.heappush(heap, (d + w, v))
        return dist
```

## Complexity

`bfs`, `dfs`, `components`, `topo`: `O(V + E)` time and `O(V)` extra memory. `shortest`: `O((V + E) log V)`. The graph itself takes `O(V + E)`.

## Another way

`topo` can also be the DFS way (reverse finishing order with an iterator stack and three colours to detect a cycle). `components` could use Union-Find over the edges, which also allows adding edges later and asking again cheaply. A library for real use would also offer `path(s, t)` from a parent dictionary, and a `has_cycle()`.
