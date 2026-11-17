def strongly_connected_components(n, edges):
    adj = [[] for _ in range(n)]
    radj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        radj[v].append(u)
    seen = [False] * n
    order = []
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        stack = [(s, iter(adj[s]))]
        while stack:
            u, it = stack[-1]
            v = next(it, None)
            if v is None:
                order.append(u)
                stack.pop()
            elif not seen[v]:
                seen[v] = True
                stack.append((v, iter(adj[v])))
    comp = [-1] * n
    result = []
    for s in reversed(order):
        if comp[s] != -1:
            continue
        cid = len(result)
        comp[s] = cid
        group = [s]
        stack = [s]
        while stack:
            u = stack.pop()
            for v in radj[u]:
                if comp[v] == -1:
                    comp[v] = cid
                    group.append(v)
                    stack.append(v)
        result.append(group)
    return result
