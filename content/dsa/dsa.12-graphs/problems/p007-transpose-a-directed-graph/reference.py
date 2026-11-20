from collections import deque


def transpose(adj):
    rev = [[] for _ in adj]
    for u, nbrs in enumerate(adj):
        for v in nbrs:
            rev[v].append(u)
    return rev


def can_reach(adj, target):
    rev = transpose(adj)
    seen = {target}
    queue = deque([target])
    while queue:
        u = queue.popleft()
        for v in rev[u]:
            if v not in seen:
                seen.add(v)
                queue.append(v)
    return sorted(seen)
