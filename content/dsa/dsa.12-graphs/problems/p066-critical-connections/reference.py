def critical_connections(n, edges):
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, i))
        adj[v].append((u, i))
    tin = [-1] * n
    low = [0] * n
    timer = 0
    found = []
    for s in range(n):
        if tin[s] != -1:
            continue
        tin[s] = low[s] = timer
        timer += 1
        stack = [(s, -1, iter(adj[s]))]
        while stack:
            u, via, it = stack[-1]
            step = next(it, None)
            if step is None:
                stack.pop()
                if stack:
                    p = stack[-1][0]
                    if low[u] < low[p]:
                        low[p] = low[u]
                    if low[u] > tin[p]:
                        found.append(edges[via])
                continue
            v, i = step
            if i == via:
                continue
            if tin[v] == -1:
                tin[v] = low[v] = timer
                timer += 1
                stack.append((v, i, iter(adj[v])))
            elif tin[v] < low[u]:
                low[u] = tin[v]
    return found
