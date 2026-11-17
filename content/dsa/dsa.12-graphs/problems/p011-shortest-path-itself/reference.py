from collections import deque


def shortest_path(n, edges, s, t):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    parent = {s: None}
    queue = deque([s])
    while queue:
        u = queue.popleft()
        if u == t:
            break
        for v in adj[u]:
            if v not in parent:
                parent[v] = u
                queue.append(v)
    if t not in parent:
        return None
    path = []
    x = t
    while x is not None:
        path.append(x)
        x = parent[x]
    path.reverse()
    return path
