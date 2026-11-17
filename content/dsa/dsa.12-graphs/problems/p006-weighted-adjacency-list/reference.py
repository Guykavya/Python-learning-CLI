def weighted_adj(n, edges, directed=False):
    adj = [{} for _ in range(n)]

    def put(a, b, w):
        if b not in adj[a] or w < adj[a][b]:
            adj[a][b] = w

    for u, v, w in edges:
        put(u, v, w)
        if not directed:
            put(v, u, w)
    return adj
