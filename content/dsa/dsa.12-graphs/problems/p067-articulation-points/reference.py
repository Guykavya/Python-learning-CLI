def articulation_points(n, edges):
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, i))
        adj[v].append((u, i))
    tin = [-1] * n
    low = [0] * n
    timer = 0
    points = set()
    for s in range(n):
        if tin[s] != -1:
            continue
        tin[s] = low[s] = timer
        timer += 1
        root_children = 0
        stack = [(s, -1, iter(adj[s]))]
        while stack:
            u, via, it = stack[-1]
            step = next(it, None)
            if step is None:
                stack.pop()
                if stack:
                    p = stack[-1][0]
                    low[p] = min(low[p], low[u])
                    if p != s and low[u] >= tin[p]:
                        points.add(p)
                continue
            v, i = step
            if i == via:
                continue
            if tin[v] == -1:
                tin[v] = low[v] = timer
                timer += 1
                if u == s:
                    root_children += 1
                stack.append((v, i, iter(adj[v])))
            else:
                low[u] = min(low[u], tin[v])
        if root_children >= 2:
            points.add(s)
    return sorted(points)
