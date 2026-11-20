def max_independent_set(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    parent = [-1] * n
    seen = [False] * n
    seen[0] = True
    order = [0]
    i = 0
    while i < len(order):                       # BFS: every parent before its children
        v = order[i]
        i += 1
        for w in adj[v]:
            if not seen[w]:
                seen[w] = True
                parent[w] = v
                order.append(w)

    take = [1] * n                               # v itself
    skip = [0] * n
    for v in reversed(order):                    # children before parents
        p = parent[v]
        if p != -1:
            take[p] += skip[v]
            skip[p] += max(take[v], skip[v])
    return max(take[0], skip[0])
