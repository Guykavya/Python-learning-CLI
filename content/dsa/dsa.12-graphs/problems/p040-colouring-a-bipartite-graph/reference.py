from collections import deque


def two_colour(n, dislikes):
    adj = [[] for _ in range(n)]
    for a, b in dislikes:
        adj[a].append(b)
        adj[b].append(a)
    group = [-1] * n
    for s in range(n):
        if group[s] != -1:
            continue
        group[s] = 0
        queue = deque([s])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if group[v] == -1:
                    group[v] = 1 - group[u]
                    queue.append(v)
                elif group[v] == group[u]:
                    return None                    # two enemies forced into one group
    return group
