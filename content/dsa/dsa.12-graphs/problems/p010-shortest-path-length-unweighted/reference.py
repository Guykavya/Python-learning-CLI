from collections import deque


def distance(n, edges, s, t):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    dist = {s: 0}
    queue = deque([s])
    while queue:
        u = queue.popleft()
        if u == t:
            return dist[u]
        for v in adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                queue.append(v)
    return -1
